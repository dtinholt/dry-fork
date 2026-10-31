#!/usr/bin/env python3
"""wl_builder: an unattended builder loop for a local open model.

The model builds software under a project directory against a frozen SPEC/
and frozen tests/. It may edit only the configured writable paths. Every
iteration is logged for a registered study under runs/<run-id>/.

Standard library only (urllib for HTTP, tomllib for config).

Usage:
    python3 wl_builder.py --config harness.toml
    python3 wl_builder.py --config harness.toml --resume [RUN_ID]
    python3 wl_builder.py --selftest
"""
from __future__ import annotations

import argparse
import copy
import fnmatch
import glob as globmod
import hashlib
import http.server
import json
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

HARNESS_VERSION = "0.1.0"

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

DEFAULT_CONFIG: dict = {
    "endpoint": {
        "base_url": "http://127.0.0.1:1234/v1",
        "model": "Qwen/Qwen3.6-35B-A3B",
        "api_key": "",
        "temperature": 0.3,
        "request_timeout_s": 1800,
        "per_request_max_tokens": 8192,
        "retry_window_s": 1800,      # retry with backoff this long, then pause
        "backoff_initial_s": 5,
        "backoff_max_s": 120,
        "poll_interval_s": 60,       # sleep-poll interval while paused
        "extra_params": {},          # merged into every chat request body
    },
    "project": {
        "dir": "project",
        "python": "python3",
        "test_command": "{python} -m pytest -q -p no:cacheprovider --junitxml={junit} {select}",
        "test_timeout_s": 600,
        "test_env": {"PYTHONPATH": "{project}"},
        "runs_dir": "runs",
        "stop_file": "STOP",
        "worklog": "WORKLOG.md",
    },
    "limits": {
        "max_iterations": 500,
        "max_wall_hours": 72.0,
        "wall_clock_excludes_waits": True,  # endpoint outages and review pauses
        "iteration_token_cap": 32000,       # completion tokens per iteration
        "max_turns_per_iteration": 40,
        "iteration_time_limit_s": 3600,
        "context_budget_tokens": 100000,
        "tool_result_max_chars": 8000,
        "command_timeout_s": 120,
        "max_failures_shown": 10,
        "reads_before_write": 0,   # 0 = off; N = after N read-type tool calls with no write in an iteration, reads are refused
        "failure_message_max_chars": 500,
        "worklog_tail_chars": 6000,
        "spec_index_max_chars": 6000,
        "spec_index_heading_depth": 3,
        "max_write_chars": 400000,
    },
    "paths": {
        "writable": ["src/", "tests/fixtures-generated/"],
    },
    "commands": {
        "allowlist": ["python3", "pytest", "ls", "cat", "grep", "wc", "head", "diff"],
    },
    "sandbox": {
        "mode": "auto",  # auto | none
    },
    "review": {
        "every_k": 0,           # 0 disables the periodic trigger
        "on_milestone": True,
        "required": False,
        "poll_interval_s": 30,
        "reply_max_chars": 12000,
        "diff_max_chars": 60000,
    },
    "milestones": [
        # {"name": "roman", "select": "tests/test_roman.py"}
    ],
}


def deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_config(path: str | Path) -> dict:
    path = Path(path).expanduser().resolve()
    text = path.read_text()
    if path.suffix == ".json":
        raw = json.loads(text)
    else:
        raw = tomllib.loads(text)
    cfg = deep_merge(DEFAULT_CONFIG, raw)
    base = path.parent
    cfg["_config_path"] = str(path)
    cfg["_config_sha"] = hashlib.sha256(text.encode()).hexdigest()[:16]

    def res(p: str) -> str:
        p = os.path.expanduser(p)
        return os.path.realpath(p if os.path.isabs(p) else base / p)

    pj = cfg["project"]
    pj["dir"] = res(pj["dir"])
    pj["runs_dir"] = res(pj["runs_dir"])
    pj["stop_file"] = res(pj["stop_file"])
    if not cfg["milestones"]:
        raise SystemExit("config: at least one [[milestones]] entry is required")
    for m in cfg["milestones"]:
        if "name" not in m or "select" not in m:
            raise SystemExit("config: each milestone needs name and select")
    return cfg


# --------------------------------------------------------------------------
# Small utilities
# --------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha16(obj) -> str:
    if not isinstance(obj, (bytes, str)):
        obj = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    if isinstance(obj, str):
        obj = obj.encode()
    return hashlib.sha256(obj).hexdigest()[:16]


def atomic_write_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    os.replace(tmp, path)


def append_jsonl(path: Path, row: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def cap_text(text: str, limit: int, hint: str = "") -> str:
    if len(text) <= limit:
        return text
    head = text[: limit]
    return head + f"\n[truncated: showing {limit} of {len(text)} chars{'; ' + hint if hint else ''}]"


def tail_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    t = text[-limit:]
    nl = t.find("\n")
    if 0 <= nl < 200:
        t = t[nl + 1:]
    return "[earlier entries omitted]\n" + t


class StopRequested(Exception):
    pass


class EventLog:
    """events.jsonl plus a one-line console echo."""

    def __init__(self, path: Path | None, echo: bool = True):
        self.path = path
        self.echo = echo
        self.rows: list[dict] = []

    def __call__(self, kind: str, **fields):
        row = {"ts": now_iso(), "event": kind, **fields}
        self.rows.append(row)
        if self.path:
            append_jsonl(self.path, row)
        if self.echo:
            extra = " ".join(f"{k}={v}" for k, v in fields.items())
            print(f"[{row['ts']}] {kind} {extra}", flush=True)


# --------------------------------------------------------------------------
# Sandbox: no network, writes only to the writable paths and a scratch dir
# --------------------------------------------------------------------------

class Sandbox:
    def __init__(self, mode: str, write_dirs: list[str]):
        self.write_dirs = [os.path.realpath(d) for d in write_dirs]
        self.kind = "none"
        self.profile_path: str | None = None
        if mode == "none":
            return
        if sys.platform == "darwin" and shutil.which("sandbox-exec"):
            self.kind = "seatbelt"
            allow = " ".join(f'(subpath "{d}")' for d in self.write_dirs)
            prof = (
                "(version 1)\n(allow default)\n(deny network*)\n"
                "(allow network* (remote unix-socket))\n"
                "(deny file-write*)\n"
                f'(allow file-write* {allow} (literal "/dev/null") (literal "/dev/tty")'
                ' (subpath "/dev/fd") (literal "/dev/dtracehelper"))\n'
            )
            fd, p = tempfile.mkstemp(prefix="wl-sandbox-", suffix=".sb")
            os.write(fd, prof.encode())
            os.close(fd)
            self.profile_path = p
        elif sys.platform.startswith("linux") and shutil.which("bwrap"):
            self.kind = "bwrap"
        elif sys.platform.startswith("linux") and shutil.which("unshare"):
            try:
                ok = subprocess.run(["unshare", "-rn", "true"], capture_output=True, timeout=10).returncode == 0
            except Exception:
                ok = False
            if ok:
                self.kind = "unshare-net"

    def wrap(self, argv: list[str]) -> list[str]:
        if self.kind == "seatbelt":
            return ["sandbox-exec", "-f", self.profile_path, *argv]
        if self.kind == "bwrap":
            pre = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
                   "--unshare-net", "--die-with-parent"]
            for d in self.write_dirs:
                pre += ["--bind", d, d]
            return [*pre, *argv]
        if self.kind == "unshare-net":
            return ["unshare", "-rn", *argv]
        return argv


# --------------------------------------------------------------------------
# Path guard
# --------------------------------------------------------------------------

class PathError(Exception):
    pass


class PathGuard:
    def __init__(self, project: str, writable: list[str]):
        self.root = os.path.realpath(project)
        self.writable = [w.strip("/") for w in writable]

    def rel(self, abspath: str) -> str:
        return os.path.relpath(abspath, self.root)

    def resolve(self, path: str) -> str:
        if not isinstance(path, str) or not path or "\x00" in path:
            raise PathError("invalid path")
        p = os.path.expanduser(path)
        if not os.path.isabs(p):
            p = os.path.join(self.root, p)
        real = os.path.realpath(p)
        if real != self.root and not real.startswith(self.root + os.sep):
            raise PathError(f"refused: {path!r} is outside the project directory")
        rel = self.rel(real)
        if rel == ".git" or rel.startswith(".git" + os.sep):
            raise PathError("refused: .git is off limits")
        return real

    def check_read(self, path: str) -> str:
        return self.resolve(path)

    def is_writable_rel(self, rel: str) -> bool:
        rel = rel.replace(os.sep, "/")
        for w in self.writable:
            if rel == w or rel.startswith(w + "/"):
                return True
        return False

    def check_write(self, path: str) -> str:
        real = self.resolve(path)
        rel = self.rel(real)
        if not self.is_writable_rel(rel):
            raise PathError(
                f"refused: writes are allowed only under {', '.join(w + '/' for w in self.writable)}; "
                f"{rel!r} is read-only (SPEC/ and tests/ are frozen)")
        if os.path.isdir(real):
            raise PathError(f"refused: {rel!r} is a directory")
        return real


# --------------------------------------------------------------------------
# Unified diff application (no external `patch` dependency)
# --------------------------------------------------------------------------

class PatchError(Exception):
    pass


_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse_hunks(diff: str) -> list[tuple[int | None, list[str], list[str]]]:
    lines = diff.splitlines()
    hunks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("@@"):
            m = _HUNK_RE.match(line)
            start = int(m.group(1)) if m else None
            old, new = [], []
            i += 1
            while i < len(lines):
                b = lines[i]
                if b.startswith("@@"):
                    break
                if b.startswith("--- ") and i + 1 < len(lines) and lines[i + 1].startswith("+++ "):
                    break
                if b.startswith("\\"):
                    i += 1
                    continue
                if b.startswith("+"):
                    new.append(b[1:])
                elif b.startswith("-"):
                    old.append(b[1:])
                elif b.startswith(" "):
                    old.append(b[1:])
                    new.append(b[1:])
                elif b == "":
                    old.append("")
                    new.append("")
                else:
                    raise PatchError(f"unrecognised diff line: {b[:80]!r}")
                i += 1
            # trailing blank context lines produced by splitlines are ambiguous; trim matched pairs
            while old and new and old[-1] == "" and new[-1] == "" and (i >= len(lines)):
                old.pop()
                new.pop()
            hunks.append((start, old, new))
            continue
        i += 1
    if not hunks:
        raise PatchError("no hunks found (expected lines starting with @@)")
    return hunks


def _find(src: list[str], block: list[str], hint: int, cursor: int, loose: bool) -> int:
    norm = (lambda s: " ".join(s.split())) if loose else (lambda s: s)
    nb = [norm(b) for b in block]
    n = len(block)

    def match_at(k):
        return k >= 0 and k + n <= len(src) and all(norm(src[k + j]) == nb[j] for j in range(n))

    if hint is not None and match_at(hint):
        return hint
    if hint is not None:
        for d in range(1, 200):
            for k in (hint - d, hint + d):
                if k >= cursor and match_at(k):
                    return k
    for k in range(cursor, len(src) - n + 1):
        if match_at(k):
            return k
    for k in range(0, min(cursor, len(src) - n + 1)):
        if match_at(k):
            return k
    return -1


def apply_unified_diff(original: str | None, diff: str) -> str:
    src = [] if original is None else original.splitlines()
    hunks = parse_hunks(diff)
    offset = 0
    cursor = 0
    for idx, (start, old, new) in enumerate(hunks):
        hint = None if start is None else max(0, start - 1 + offset)
        if not old:
            pos = len(src) if hint is None else min(hint, len(src))
            if start == 0:
                pos = 0
        else:
            pos = _find(src, old, hint, cursor, loose=False)
            if pos < 0:
                pos = _find(src, old, hint, cursor, loose=True)
            if pos < 0:
                preview = "\n".join(old[:12])
                raise PatchError(
                    f"hunk {idx + 1} did not match the file. Expected these lines (context and removals):\n"
                    f"{preview}\nRe-read the file and retry, or use write_file for the whole file.")
        src[pos:pos + len(old)] = new
        offset += len(new) - len(old)
        cursor = pos + len(new)
    return "\n".join(src) + ("\n" if src else "")


# --------------------------------------------------------------------------
# Spec access
# --------------------------------------------------------------------------

_HEAD_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


class Spec:
    def __init__(self, project: str):
        self.root = Path(project) / "SPEC"
        self.files: list[Path] = sorted(self.root.rglob("*.md")) if self.root.exists() else []

    def _rel(self, p: Path) -> str:
        return str(p.relative_to(self.root.parent))

    def headings(self, p: Path) -> list[tuple[int, int, str]]:
        out, fence = [], False
        for n, line in enumerate(p.read_text(errors="replace").splitlines()):
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            m = _HEAD_RE.match(line)
            if m:
                out.append((n, len(m.group(1)), m.group(2)))
        return out

    def index(self, depth: int, max_chars: int) -> str:
        if not self.files:
            return "(no SPEC/ files found)"
        rows = []
        for p in self.files:
            size = p.stat().st_size
            rows.append(f"- {self._rel(p)} ({size} bytes)")
            for _, lvl, title in self.headings(p):
                if lvl <= depth:
                    rows.append(f"  {'  ' * (lvl - 1)}{'#' * lvl} {title}")
        return cap_text("\n".join(rows), max_chars,
                        "call read_spec with a file name to see its full heading list")

    def section(self, query: str) -> str:
        q = (query or "").strip()
        if not q:
            return "error: give a SPEC file name, 'file#heading', or a heading title"
        file_part, _, head_part = q.partition("#") if "#" in q and not q.startswith("#") else ("", "", q.lstrip("# ").strip())
        file_part = file_part.strip()
        if file_part:
            cand = [p for p in self.files if self._rel(p) == file_part or str(p.relative_to(self.root)) == file_part
                    or p.name == file_part or p.stem == file_part]
            if not cand:
                return f"error: no SPEC file matches {file_part!r}"
            return self._section_in(cand[0], head_part.strip()) if head_part.strip() else self._whole(cand[0])
        # whole-file match
        for p in self.files:
            if q in (self._rel(p), str(p.relative_to(self.root)), p.name, p.stem):
                return self._whole(p)
        # heading match: exact (case-insensitive) first, then substring
        hits = []
        for p in self.files:
            for n, lvl, title in self.headings(p):
                t = title.lower()
                ql = head_part.lower()
                if t == ql:
                    hits.insert(0, (p, title))
                elif ql in t:
                    hits.append((p, title))
        if not hits:
            return f"error: no SPEC file or heading matches {q!r}; see the spec index"
        p, title = hits[0]
        body = self._section_in(p, title)
        others = [f"{self._rel(a)}#{b}" for a, b in hits[1:8]]
        if others:
            body += "\n\n[other matching sections: " + "; ".join(others) + "]"
        return body

    def _whole(self, p: Path) -> str:
        return f"=== {self._rel(p)} ===\n" + p.read_text(errors="replace")

    def _section_in(self, p: Path, title: str) -> str:
        lines = p.read_text(errors="replace").splitlines()
        hs = self.headings(p)
        tl = title.lower()
        pick = next((h for h in hs if h[2].lower() == tl), None) or next((h for h in hs if tl in h[2].lower()), None)
        if not pick:
            return f"error: heading {title!r} not found in {self._rel(p)}"
        n, lvl, t = pick
        end = len(lines)
        for n2, lvl2, _ in hs:
            if n2 > n and lvl2 <= lvl:
                end = n2
                break
        return f"=== {self._rel(p)} # {t} ===\n" + "\n".join(lines[n:end])


# --------------------------------------------------------------------------
# Test runner
# --------------------------------------------------------------------------

class TestRunner:
    def __init__(self, cfg: dict, sandbox: Sandbox, scratch: str):
        self.cfg = cfg
        self.sandbox = sandbox
        self.scratch = scratch
        self.project = cfg["project"]["dir"]
        self.groups = cfg["milestones"]

    def env(self) -> dict:
        env = {k: v for k, v in os.environ.items()
               if not k.lower().endswith("_proxy") and k not in ("PYTHONSTARTUP",)}
        for k, v in self.cfg["project"].get("test_env", {}).items():
            env[k] = str(v).replace("{project}", self.project)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["TMPDIR"] = self.scratch
        env["NO_PROXY"] = "*"
        return env

    def run_group(self, group: dict) -> tuple[dict, str]:
        junit = os.path.join(self.scratch, f"junit-{group['name']}-{os.getpid()}-{time.time_ns()}.xml")
        cmd = self.cfg["project"]["test_command"].format(
            python=self.cfg["project"]["python"], junit=shlex.quote(junit),
            select=group["select"], project=shlex.quote(self.project), group=group["name"])
        argv = self.sandbox.wrap(shlex.split(cmd))
        t0 = time.time()
        try:
            p = subprocess.run(argv, cwd=self.project, env=self.env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=self.cfg["project"]["test_timeout_s"], stdin=subprocess.DEVNULL)
            rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
        except subprocess.TimeoutExpired as e:
            rc = -9
            out = ((e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")) + \
                f"\n[harness] test command timed out after {self.cfg['project']['test_timeout_s']} s"
        dur = round(time.time() - t0, 2)
        res = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total": 0, "rc": rc,
               "duration_s": dur, "failures": [], "parsed": "junit"}
        if os.path.exists(junit):
            try:
                self._parse_junit(junit, res)
            except ET.ParseError:
                res["parsed"] = "exitcode"
            os.unlink(junit)
        else:
            res["parsed"] = "exitcode"
        if res["parsed"] == "exitcode":
            res["total"] = 1
            res["passed"] = 1 if rc == 0 else 0
            res["failed"] = 0 if rc == 0 else 1
            if rc != 0:
                res["failures"].append({"name": f"{group['name']} (exit code {rc})", "message": out[-1500:]})
        return res, f"$ {cmd}\n(exit {rc}, {dur} s)\n{out}"

    def _parse_junit(self, path: str, res: dict) -> None:
        mlen = self.cfg["limits"]["failure_message_max_chars"]
        root = ET.parse(path).getroot()
        for tc in root.iter("testcase"):
            name = (tc.get("classname", "") + "::" + tc.get("name", "")).strip(":")
            res["total"] += 1
            bad = None
            for child in tc:
                if child.tag in ("failure", "error"):
                    bad = child
                    break
                if child.tag == "skipped":
                    res["skipped"] += 1
                    bad = "skip"
                    break
            if bad is None:
                res["passed"] += 1
            elif bad == "skip":
                pass
            else:
                key = "failed" if bad.tag == "failure" else "errors"
                res[key] += 1
                msg = (bad.get("message") or "").strip()
                text = (bad.text or "").strip()
                # keep the assertion line(s) near the end, which is where pytest puts them
                detail = msg if msg else text[-mlen:]
                if msg and text:
                    tail = "\n".join(l for l in text.splitlines()[-6:] if l.strip())
                    detail = f"{msg}\n{tail}"
                res["failures"].append({"name": name, "message": detail[:mlen]})

    def run(self, group_name: str | None = None) -> tuple[dict, str]:
        groups = self.groups if not group_name else [g for g in self.groups if g["name"] == group_name]
        if not groups:
            raise ValueError(f"unknown group {group_name!r}; groups are: {', '.join(g['name'] for g in self.groups)}")
        results, raw = {}, []
        for g in groups:
            r, out = self.run_group(g)
            results[g["name"]] = r
            raw.append(f"===== group {g['name']} =====\n{out}")
        return results, "\n".join(raw)

    def report(self, results: dict, max_fail: int) -> str:
        lines = []
        for name, r in results.items():
            status = "PASS" if r["total"] and r["passed"] == r["total"] else "open"
            lines.append(f"- {name}: {r['passed']}/{r['total']} passed, {r['failed']} failed, "
                         f"{r['errors']} errors [{status}]")
        fails = [(n, f) for n, r in results.items() for f in r["failures"]]
        if fails:
            lines.append(f"\nFirst {min(max_fail, len(fails))} of {len(fails)} failing tests:")
            for n, f in fails[:max_fail]:
                lines.append(f"* [{n}] {f['name']}\n    " + f["message"].replace("\n", "\n    "))
        return "\n".join(lines)


def all_pass(results: dict) -> bool:
    return bool(results) and all(r["total"] > 0 and r["passed"] == r["total"] for r in results.values())


def counts(results: dict | None) -> dict:
    if not results:
        return {}
    return {n: {"passed": r["passed"], "total": r["total"], "failed": r["failed"], "errors": r["errors"]}
            for n, r in results.items()}


def moved(a: dict | None, b: dict | None) -> bool:
    ka = {n: (v["passed"], v["total"]) for n, v in counts(a).items()}
    kb = {n: (v["passed"], v["total"]) for n, v in counts(b).items()}
    return ka != kb


# --------------------------------------------------------------------------
# LLM client with outage tolerance
# --------------------------------------------------------------------------

class EndpointError(Exception):
    pass


class LLMClient:
    def __init__(self, ecfg: dict, events: EventLog, stop_check=None):
        self.c = ecfg
        self.base = ecfg["base_url"].rstrip("/")
        self.events = events
        self.stop_check = stop_check or (lambda: False)
        self.wait_s_total = 0.0

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.c.get("api_key"):
            h["Authorization"] = f"Bearer {self.c['api_key']}"
        return h

    def _post(self, payload: dict) -> dict:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(self.base + "/chat/completions", data=data, headers=self._headers(), method="POST")
        with urllib.request.urlopen(req, timeout=self.c["request_timeout_s"]) as r:
            return json.loads(r.read().decode())

    def alive(self) -> bool:
        try:
            req = urllib.request.Request(self.base + "/models", headers=self._headers())
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status < 500
        except urllib.error.HTTPError as e:
            return e.code < 500
        except Exception:
            return False

    def _sleep(self, seconds: float):
        end = time.time() + seconds
        while time.time() < end:
            if self.stop_check():
                raise StopRequested()
            time.sleep(min(1.0, max(0.0, end - time.time())))

    def chat(self, payload: dict) -> tuple[dict, float]:
        """Return (response json, seconds spent waiting on outages)."""
        waited = 0.0
        first_fail = None
        delay = float(self.c["backoff_initial_s"])
        while True:
            try:
                return self._post(payload), waited
            except urllib.error.HTTPError as e:
                body = ""
                try:
                    body = e.read().decode(errors="replace")[:2000]
                except Exception:
                    pass
                if e.code not in (408, 409, 425, 429) and e.code < 500:
                    raise EndpointError(f"HTTP {e.code}: {body}") from None
                err = f"HTTP {e.code}: {body[:200]}"
            except (urllib.error.URLError, ConnectionError, TimeoutError, socket.timeout, OSError,
                    json.JSONDecodeError) as e:
                err = f"{type(e).__name__}: {str(e)[:200]}"
            t = time.time()
            first_fail = first_fail or t
            if t - first_fail < self.c["retry_window_s"]:
                self.events("endpoint_retry", error=err, sleep_s=round(delay, 1),
                            failing_for_s=round(t - first_fail, 1))
                t0 = time.time()
                self._sleep(delay)
                waited += time.time() - t0
                delay = min(delay * 2, float(self.c["backoff_max_s"]))
                continue
            # pause: sleep-poll until the endpoint answers again
            self.events("endpoint_paused", error=err, failing_for_s=round(t - first_fail, 1),
                        poll_interval_s=self.c["poll_interval_s"])
            pause_start = time.time()
            polls = 0
            while True:
                t0 = time.time()
                self._sleep(self.c["poll_interval_s"])
                waited += time.time() - t0
                polls += 1
                if self.alive():
                    break
                self.events("endpoint_waiting", polls=polls, paused_for_s=round(time.time() - pause_start, 1))
            self.events("endpoint_recovered", paused_for_s=round(time.time() - pause_start, 1), polls=polls)
            first_fail = None
            delay = float(self.c["backoff_initial_s"])
            self.wait_s_total += 0  # accounted by caller via returned `waited`


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------

def _fn(name, desc, props, required):
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": required}}}


TOOL_SCHEMAS = [
    _fn("read_spec", "Read a SPEC section. Pass a SPEC file name (e.g. 'SPEC/combat.md'), 'file#Heading', or a heading title.",
        {"section": {"type": "string"}}, ["section"]),
    _fn("read_file", "Read a file in the project (any path under the project). Optional 1-based line range.",
        {"path": {"type": "string"}, "start_line": {"type": "integer"}, "end_line": {"type": "integer"}}, ["path"]),
    _fn("write_file", "Write a whole file (creates parent dirs). Only allowed under the writable paths.",
        {"path": {"type": "string"}, "content": {"type": "string"}}, ["path", "content"]),
    _fn("apply_patch", "Apply a unified diff (hunks starting with @@) to one file under the writable paths.",
        {"path": {"type": "string"}, "unified_diff": {"type": "string"}}, ["path", "unified_diff"]),
    _fn("list_files", "List project files matching a glob, e.g. 'src/**/*.py' or 'tests/*'.",
        {"glob": {"type": "string"}}, ["glob"]),
    _fn("run_tests", "Run the acceptance tests. Optional group name; omit to run every milestone group.",
        {"group": {"type": "string"}}, []),
    _fn("run_command", "Run one command (no shell) in the project dir. Allowed programs: {allow}. No network.",
        {"cmd": {"type": "string"}}, ["cmd"]),
    _fn("note", "Append a note to WORKLOG.md: what you tried, what you learned, what to do next. Future iterations only see the worklog, not this conversation.",
        {"text": {"type": "string"}}, ["text"]),
    _fn("end_iteration", "End this iteration now. Give a one-line summary.",
        {"summary": {"type": "string"}}, ["summary"]),
]


class Tools:
    def __init__(self, cfg: dict, guard: PathGuard, spec: Spec, tests: TestRunner, sandbox: Sandbox, worklog: Path):
        self.cfg = cfg
        self.guard = guard
        self.spec = spec
        self.tests = tests
        self.sandbox = sandbox
        self.worklog = worklog
        self.iteration = 0
        self.violations: list[dict] = []
        allow = cfg["commands"]["allowlist"]
        self.schemas = json.loads(json.dumps(TOOL_SCHEMAS).replace("{allow}", ", ".join(allow)))

    # each tool returns a string; exceptions are turned into error strings by dispatch
    def read_spec(self, section: str) -> str:
        return self.spec.section(section)

    def read_file(self, path: str, start_line: int | None = None, end_line: int | None = None) -> str:
        p = self.guard.check_read(path)
        if not os.path.isfile(p):
            return f"error: {path!r} is not a file"
        text = Path(p).read_text(errors="replace")
        if start_line or end_line:
            lines = text.splitlines()
            s = max(1, int(start_line or 1))
            e = min(len(lines), int(end_line or len(lines)))
            return f"[{self.guard.rel(p)} lines {s}-{e} of {len(lines)}]\n" + "\n".join(lines[s - 1:e])
        return text

    def write_file(self, path: str, content: str) -> str:
        try:
            p = self.guard.check_write(path)
        except PathError as e:
            self.violations.append({"tool": "write_file", "path": path, "error": str(e)})
            raise
        if not isinstance(content, str):
            return "error: content must be a string"
        if len(content) > self.cfg["limits"]["max_write_chars"]:
            return f"error: content is {len(content)} chars; limit is {self.cfg['limits']['max_write_chars']}"
        os.makedirs(os.path.dirname(p), exist_ok=True)
        existed = os.path.exists(p)
        Path(p).write_text(content)
        return f"ok: {'overwrote' if existed else 'created'} {self.guard.rel(p)} ({len(content)} chars, {content.count(chr(10)) + 1} lines)"

    def apply_patch(self, path: str, unified_diff: str) -> str:
        try:
            p = self.guard.check_write(path)
        except PathError as e:
            self.violations.append({"tool": "apply_patch", "path": path, "error": str(e)})
            raise
        original = Path(p).read_text(errors="replace") if os.path.exists(p) else None
        new = apply_unified_diff(original, unified_diff)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        Path(p).write_text(new)
        return f"ok: patched {self.guard.rel(p)} ({len(new.splitlines())} lines now)"

    def list_files(self, glob: str = "**/*") -> str:
        g = glob or "**/*"
        if os.path.isabs(g) or ".." in Path(g).parts:
            raise PathError("refused: glob must be relative to the project and must not contain '..'")
        root = self.guard.root
        out = []
        for p in sorted(globmod.glob(os.path.join(root, g), recursive=True)):
            rel = os.path.relpath(p, root)
            parts = Path(rel).parts
            if parts and parts[0] == ".git" or "__pycache__" in parts or ".pytest_cache" in parts:
                continue
            if os.path.isfile(p):
                out.append(f"{rel} ({os.path.getsize(p)} bytes)")
            elif os.path.isdir(p):
                out.append(rel + "/")
        return "\n".join(out) if out else "(no matches)"

    def run_tests(self, group: str | None = None) -> str:
        results, _ = self.tests.run(group or None)
        return self.tests.report(results, self.cfg["limits"]["max_failures_shown"])

    def run_command(self, cmd: str) -> str:
        try:
            argv = shlex.split(cmd)
        except ValueError as e:
            return f"error: could not parse command: {e}"
        if not argv:
            return "error: empty command"
        prog = os.path.basename(argv[0])
        allow = self.cfg["commands"]["allowlist"]
        if prog not in allow:
            raise PathError(f"refused: {prog!r} is not allowed. Allowed: {', '.join(allow)}")
        if prog == "pytest":
            argv = [self.cfg["project"]["python"], "-m", "pytest", "-p", "no:cacheprovider", *argv[1:]]
        elif prog in ("python3", "python"):
            argv = [self.cfg["project"]["python"], *argv[1:]]
        skip_next = False
        for a in argv[1:]:
            if skip_next:
                skip_next = False
                continue
            if a == "-c":
                skip_next = True
                continue
            if a.startswith("-"):
                continue
            if os.path.isabs(os.path.expanduser(a)) or ".." in Path(a).parts or a.startswith("~"):
                self.guard.check_read(a)
        t = self.cfg["limits"]["command_timeout_s"]
        try:
            p = subprocess.run(self.sandbox.wrap(argv), cwd=self.guard.root, env=self.tests.env(),
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=t, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return f"error: command timed out after {t} s"
        out = (p.stdout or "") + (("\n[stderr]\n" + p.stderr) if p.stderr else "")
        return f"(exit {p.returncode})\n{out}"

    def note(self, text: str) -> str:
        with open(self.worklog, "a", encoding="utf-8") as f:
            f.write(f"\n### iter {self.iteration} note ({now_iso()})\n{str(text).strip()}\n")
        return "ok: appended to WORKLOG.md"

    def end_iteration(self, summary: str = "") -> str:
        return "ok: iteration will end"

    READ_TOOLS = {"read_file", "read_spec", "list_files", "run_command"}
    WRITE_TOOLS = {"write_file", "apply_patch"}

    def dispatch(self, name: str, args: dict) -> tuple[str, bool]:
        fn = getattr(self, name, None) if name in {s["function"]["name"] for s in self.schemas} else None
        if fn is None:
            return f"error: unknown tool {name!r}", False
        # Arm B2 (PREREG-W1 addendum 4): a read budget per iteration until the first write.
        rb = int(getattr(self, "reads_before_write", 0) or 0)
        if rb:
            if getattr(self, "_iter_of_counts", None) != self.iteration:
                self._iter_of_counts, self._reads, self._writes = self.iteration, 0, 0
            if name in self.READ_TOOLS and self._writes == 0 and self._reads >= rb:
                self._refused_reads = getattr(self, "_refused_reads", 0) + 1
                return (f"refused: read budget for this iteration is spent ({rb} reads before the first write). "
                        f"Write code now with write_file or apply_patch, using what you already know and the worklog; "
                        f"reads reopen after a substantive write (a file of 60 lines or more, or a patch adding 40 lines or more); stubs do not count."), False
            if name in self.READ_TOOLS: self._reads += 1
            if name in self.WRITE_TOOLS:
                # A write counts only when it carries substance (addendum 4a): a write_file of
                # at least 60 lines or a patch adding at least 40 lines. A stub does not reopen reads.
                content = str(args.get("content", "")) if name == "write_file" else str(args.get("unified_diff", args.get("diff", "")))
                added = content.count("\n") + 1 if name == "write_file" else sum(1 for l in content.splitlines() if l.startswith("+") and not l.startswith("+++"))
                if (name == "write_file" and added >= 60) or (name == "apply_patch" and added >= 40):
                    self._writes += 1
        try:
            return fn(**args), True
        except PathError as e:
            return f"error: {e}", False
        except PatchError as e:
            return f"error: patch failed: {e}", False
        except TypeError as e:
            return f"error: bad arguments for {name}: {e}", False
        except Exception as e:  # never let a tool crash the loop
            return f"error: {type(e).__name__}: {e}", False


# --------------------------------------------------------------------------
# Git helpers (the project repo only; never a parent repo)
# --------------------------------------------------------------------------

class Git:
    def __init__(self, project: str):
        self.dir = project

    def run(self, *args, check=True) -> str:
        p = subprocess.run(["git", "-c", "user.name=wl-builder", "-c", "user.email=wl-builder@localhost",
                            "-c", "commit.gpgsign=false", *args], cwd=self.dir,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if check and p.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
        return p.stdout

    def ensure_repo(self) -> bool:
        """Init a repo whose top level is the project dir itself. Returns True if created."""
        if os.path.isdir(os.path.join(self.dir, ".git")):
            return False
        self.run("init", "-q")
        gi = Path(self.dir) / ".gitignore"
        if not gi.exists():
            gi.write_text("__pycache__/\n.pytest_cache/\n*.pyc\n")
        return True

    def head(self) -> str | None:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return p.stdout.strip() if p.returncode == 0 else None

    def commit_all(self, msg: str) -> str | None:
        self.run("add", "-A")
        if not self.run("status", "--porcelain").strip():
            return None
        self.run("commit", "-q", "-m", msg)
        return self.head()

    def diff(self, a: str, b: str = "HEAD") -> str:
        return self.run("diff", "--stat", "-p", a, b, check=False)


# --------------------------------------------------------------------------
# The builder loop
# --------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an autonomous software engineer working unattended inside a builder loop.

Goal: make the frozen acceptance tests pass by writing code under {writable}, following the specification in SPEC/.

Rules:
- SPEC/ and tests/ are frozen. You cannot change them; writes there are refused. Read them freely with read_spec and read_file.
- You can write only under: {writable}.
- Work in small verified steps: read the relevant spec section and the failing test, write code, run_tests, fix.
- Milestone groups, in priority order: {groups}. Focus on the first group that is not passing.
- This conversation is discarded at the end of the iteration. The only memory carried forward is WORKLOG.md, the code, and the test results. Before the iteration ends, call note() with what you tried, what worked, what failed, and what to try next.
- Iteration budget: about {turns} tool-calling turns, {tokens} output tokens, {minutes} minutes. End with end_iteration(summary) when you have made and recorded progress.
- No network access. run_command allows only: {allow}.
"""


class Builder:
    def __init__(self, cfg: dict, run_id: str | None = None, resume: bool = False, echo: bool = True):
        self.cfg = cfg
        self.L = cfg["limits"]
        pj = cfg["project"]
        self.project = pj["dir"]
        if not os.path.isdir(self.project):
            raise SystemExit(f"project dir not found: {self.project}")
        for need in ("SPEC", "tests"):
            if not os.path.isdir(os.path.join(self.project, need)):
                raise SystemExit(f"project dir lacks {need}/")
        os.makedirs(os.path.join(self.project, "src"), exist_ok=True)
        runs = Path(pj["runs_dir"])
        runs.mkdir(parents=True, exist_ok=True)
        if resume:
            if not run_id:
                cands = sorted([p for p in runs.iterdir() if (p / "state.json").exists()],
                               key=lambda p: (p / "state.json").stat().st_mtime)
                if not cands:
                    raise SystemExit("--resume: no previous run found in " + str(runs))
                run_id = cands[-1].name
            self.run_dir = runs / run_id
            if not (self.run_dir / "state.json").exists():
                raise SystemExit(f"--resume: no state.json in {self.run_dir}")
            self.state = json.loads((self.run_dir / "state.json").read_text())
        else:
            short = re.sub(r"[^A-Za-z0-9]+", "-", cfg["endpoint"]["model"].split("/")[-1]).strip("-")[:24]
            run_id = run_id or f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{short}"
            self.run_dir = runs / run_id
            self.run_dir.mkdir(parents=True, exist_ok=False)
            self.state = None
        self.run_id = run_id
        self.scratch = str(self.run_dir / "scratch")
        os.makedirs(self.scratch, exist_ok=True)
        self.events = EventLog(self.run_dir / "events.jsonl", echo=echo)
        writable_abs = [os.path.join(self.project, w.strip("/")) for w in cfg["paths"]["writable"]]
        for d in writable_abs:
            os.makedirs(d, exist_ok=True)
        self.sandbox = Sandbox(cfg["sandbox"]["mode"], writable_abs + [self.scratch])
        self.guard = PathGuard(self.project, cfg["paths"]["writable"])
        self.spec = Spec(self.project)
        self.tests = TestRunner(cfg, self.sandbox, self.scratch)
        self.worklog = Path(self.project) / pj["worklog"]
        self.tools = Tools(cfg, self.guard, self.spec, self.tests, self.sandbox, self.worklog)
        self.git = Git(self.project)
        self.client = LLMClient(cfg["endpoint"], self.events, stop_check=self.stop_requested)
        self.f_iter = self.run_dir / "iterations.jsonl"
        self.f_trans = self.run_dir / "transcript.jsonl"
        self.f_summary = self.run_dir / "summary.json"
        self.f_state = self.run_dir / "state.json"
        self.protected_dir = self.run_dir / "protected-snapshot"

    # ---------------- state ----------------
    def save_state(self):
        atomic_write_json(self.f_state, self.state)

    def stop_requested(self) -> bool:
        return os.path.exists(self.cfg["project"]["stop_file"])

    # ---------------- protected-file integrity ----------------
    def _protected_files(self) -> list[str]:
        out = []
        root = self.project
        for dp, dns, fns in os.walk(root):
            rel_dp = os.path.relpath(dp, root)
            dns[:] = [d for d in dns if d not in (".git", "__pycache__", ".pytest_cache")]
            for fn in fns:
                rel = os.path.normpath(os.path.join(rel_dp, fn))
                if rel == os.path.basename(str(self.worklog)) or rel == ".gitignore":
                    continue
                if self.guard.is_writable_rel(rel) or fn.endswith(".pyc"):
                    continue
                out.append(rel)
        return sorted(out)

    def snapshot_protected(self):
        if self.protected_dir.exists():
            shutil.rmtree(self.protected_dir)
        manifest = {}
        for rel in self._protected_files():
            src = os.path.join(self.project, rel)
            dst = self.protected_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            manifest[rel] = sha16(Path(src).read_bytes())
        atomic_write_json(self.run_dir / "protected-manifest.json", manifest)

    def verify_protected(self) -> list[dict]:
        """Detect and undo any change to frozen files. Returns violations."""
        manifest = json.loads((self.run_dir / "protected-manifest.json").read_text())
        found = []
        current = set(self._protected_files())
        for rel, h in manifest.items():
            p = os.path.join(self.project, rel)
            if not os.path.exists(p) or sha16(Path(p).read_bytes()) != h:
                found.append({"path": rel, "kind": "modified" if os.path.exists(p) else "deleted"})
                os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
                shutil.copy2(self.protected_dir / rel, p)
        for rel in current - set(manifest):
            found.append({"path": rel, "kind": "created"})
            os.unlink(os.path.join(self.project, rel))
        return found

    def writable_hashes(self) -> dict:
        out = {}
        for w in self.cfg["paths"]["writable"]:
            base = os.path.join(self.project, w.strip("/"))
            for dp, dns, fns in os.walk(base):
                dns[:] = [d for d in dns if d not in ("__pycache__",)]
                for fn in fns:
                    if fn.endswith(".pyc"):
                        continue
                    p = os.path.join(dp, fn)
                    out[os.path.relpath(p, self.project)] = sha16(Path(p).read_bytes())
        return out

    # ---------------- setup / resume ----------------
    def init_run(self):
        created = self.git.ensure_repo()
        if not self.worklog.exists():
            self.worklog.write_text("# Worklog\n\nAppend-only. Written by the model via note() and by the harness.\n")
        self.snapshot_protected()
        base_sha = self.git.commit_all(f"wl-builder baseline for run {self.run_id}") or self.git.head()
        self.events("run_start", run_id=self.run_id, project=self.project, model=self.cfg["endpoint"]["model"],
                    endpoint=self.cfg["endpoint"]["base_url"], sandbox=self.sandbox.kind, git_init=created)
        results, raw = self.tests.run()
        (self.run_dir / "tests-0.txt").write_text(raw)
        self.state = {
            "run_id": self.run_id, "harness_version": HARNESS_VERSION, "created": now_iso(),
            "config_path": self.cfg["_config_path"], "config_sha": self.cfg["_config_sha"],
            "project": self.project, "model": self.cfg["endpoint"]["model"],
            "endpoint": self.cfg["endpoint"]["base_url"], "sandbox": self.sandbox.kind,
            "baseline_sha": base_sha, "last_review_sha": base_sha, "last_review_iter": 0,
            "iteration": 0, "in_progress": None, "attempts": {},
            "active_s": 0.0, "endpoint_wait_s": 0.0, "review_wait_s": 0.0,
            "tests_last": results, "baseline_tests": counts(results), "max_total": {n: r["total"] for n, r in results.items()},
            "milestones_passed": [n for n, r in results.items() if r["total"] and r["passed"] == r["total"]],
            "injected_replies": [], "tokens": {"prompt": 0, "completion": 0},
            "status": "running", "stop_reason": None, "violations": 0,
        }
        (self.run_dir / "config.json").write_text(json.dumps(
            {k: v for k, v in self.cfg.items()}, indent=2))
        self.save_state()
        self.write_summary()

    def resume_run(self):
        st = self.state
        self.events("run_resume", run_id=self.run_id, last_completed=st["iteration"],
                    in_progress=st["in_progress"], config_sha=self.cfg["_config_sha"],
                    config_changed=self.cfg["_config_sha"] != st["config_sha"])
        if st["in_progress"] is not None:
            n = st["in_progress"]
            self.events("resume_interrupted_iteration", iteration=n,
                        note="restarting this iteration from current project state")
            with open(self.worklog, "a") as f:
                f.write(f"\n[harness] iteration {n} was interrupted before it finished; it restarts now "
                        f"from whatever state the files are in.\n")
            st["in_progress"] = None
        v = self.verify_protected()
        if v:
            self.events("protected_files_restored", count=len(v), files=[x["path"] for x in v][:10])
        st["status"] = "running"
        st["stop_reason"] = None
        st["config_sha"] = self.cfg["_config_sha"]
        results, raw = self.tests.run()
        st["tests_last"] = results
        (self.run_dir / f"tests-resume-{st['iteration']}.txt").write_text(raw)
        self.save_state()

    # ---------------- context ----------------
    def src_tree(self) -> str:
        rows = []
        for w in self.cfg["paths"]["writable"]:
            base = os.path.join(self.project, w.strip("/"))
            for dp, dns, fns in os.walk(base):
                dns[:] = sorted(d for d in dns if d != "__pycache__")
                for fn in sorted(fns):
                    if fn.endswith(".pyc"):
                        continue
                    p = os.path.join(dp, fn)
                    try:
                        nl = Path(p).read_bytes().count(b"\n")
                    except OSError:
                        nl = 0
                    rows.append(f"{os.path.relpath(p, self.project)} ({nl} lines)")
        if not rows:
            return "(empty)"
        if len(rows) > 400:
            rows = rows[:400] + [f"... {len(rows) - 400} more files"]
        return "\n".join(rows)

    def pending_replies(self) -> list[tuple[str, str]]:
        out = []
        for p in sorted(self.run_dir.glob("review-reply-*.md")):
            if p.name not in self.state["injected_replies"]:
                out.append((p.name, p.read_text(errors="replace")))
        return out

    def build_context(self, n: int, replies: list[tuple[str, str]]) -> str:
        L = self.L
        groups = [m["name"] for m in self.cfg["milestones"]]
        res = self.state["tests_last"]
        focus = next((g for g in groups if not (res.get(g, {}).get("total") and
                                                res[g]["passed"] == res[g]["total"])), None)
        parts = [f"# Iteration {n} (max {L['max_iterations']})",
                 f"Current focus group: {focus or 'all groups pass'}",
                 "## Test results at the start of this iteration",
                 self.tests.report(res, L["max_failures_shown"]),
                 "## Spec index (use read_spec to read a section)",
                 self.spec.index(L["spec_index_heading_depth"], L["spec_index_max_chars"]),
                 "## Worklog tail (WORKLOG.md, your memory across iterations)",
                 tail_text(self.worklog.read_text(errors="replace"), L["worklog_tail_chars"]),
                 "## Files under the writable paths",
                 self.src_tree()]
        for name, text in replies:
            parts += [f"## Frontier review reply ({name})",
                      cap_text(text, self.cfg["review"]["reply_max_chars"])]
        parts.append("Start by deciding what to work on, read what you need, then write code and run tests.")
        return "\n\n".join(parts)

    @staticmethod
    def est_tokens(messages: list[dict]) -> int:
        return int(len(json.dumps(messages, ensure_ascii=False)) / 3.5)

    def compact(self, messages: list[dict]) -> int:
        """Elide old tool results until the estimate fits the context budget."""
        budget = int(self.L["context_budget_tokens"] * 0.85)
        elided = 0
        for m in messages[2:-4]:
            if self.est_tokens(messages) <= budget:
                break
            if m["role"] == "tool" and not m["content"].startswith("[elided"):
                c = m["content"]
                m["content"] = f"[elided to save context; was {len(c)} chars] " + c[:200]
                elided += 1
        return elided

    # ---------------- logging ----------------
    def tlog(self, n: int, turn: int, kind: str, payload: dict):
        append_jsonl(self.f_trans, {"ts": now_iso(), "iteration": n, "turn": turn, "kind": kind, **payload})

    def write_summary(self):
        st = self.state
        rows = []
        if self.f_iter.exists():
            for line in self.f_iter.read_text().splitlines():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        mt = st["max_total"]

        def frac(c):
            return {g: (round(v["passed"] / max(mt.get(g, 0), v["total"], 1), 4)) for g, v in c.items()}
        series = [{"iteration": 0, "ts": st["created"], "pass_fraction": frac(st["baseline_tests"]),
                   "counts": st["baseline_tests"]}]
        for r in rows:
            series.append({"iteration": r["iteration"], "ts": r["ts_end"],
                           "pass_fraction": frac(r["tests_after"]), "counts": r["tests_after"]})
        summary = {
            "run_id": self.run_id, "model": st["model"], "endpoint": st["endpoint"],
            "project": st["project"], "status": st["status"], "stop_reason": st["stop_reason"],
            "iterations_completed": st["iteration"], "active_hours": round(st["active_s"] / 3600, 3),
            "endpoint_wait_s": round(st["endpoint_wait_s"], 1), "review_wait_s": round(st["review_wait_s"], 1),
            "tokens": st["tokens"], "milestones_passed": st["milestones_passed"],
            "violations": st["violations"], "sandbox": st["sandbox"],
            "current": {"pass_fraction": frac(counts(st["tests_last"])), "counts": counts(st["tests_last"])},
            "series": series, "updated": now_iso(),
        }
        atomic_write_json(self.f_summary, summary)

    # ---------------- review hook ----------------
    def review_hook(self, n: int, newly_passed: list[str]):
        rc = self.cfg["review"]
        periodic = rc["every_k"] and n % rc["every_k"] == 0
        milestone = rc["on_milestone"] and newly_passed
        if not (periodic or milestone):
            return
        sha = self.git.commit_all(f"iter {n}: review checkpoint") or self.git.head()
        diff = self.git.diff(self.state["last_review_sha"], sha)
        why = []
        if periodic:
            why.append(f"every {rc['every_k']} iterations")
        if milestone:
            why.append("milestone passed: " + ", ".join(newly_passed))
        doc = "\n\n".join([
            f"# Review request, iteration {n}",
            f"Run {self.run_id}; model {self.cfg['endpoint']['model']}; trigger: {'; '.join(why)}.",
            f"Reply by writing `review-reply-{n}.md` in {self.run_dir}. "
            + ("The run is paused until the reply appears." if rc["required"] else
               "The run is not paused; a reply is injected into the next iteration that starts after it appears."),
            "## Test summary", self.tests.report(self.state["tests_last"], self.L["max_failures_shown"]),
            "## Worklog tail", tail_text(self.worklog.read_text(errors="replace"), self.L["worklog_tail_chars"]),
            f"## Diff since last review ({(self.state['last_review_sha'] or '')[:10]}..{(sha or '')[:10]})",
            "```diff\n" + cap_text(diff, rc["diff_max_chars"]) + "\n```",
        ])
        path = self.run_dir / f"review-request-{n}.md"
        path.write_text(doc)
        self.state["last_review_sha"] = sha
        self.state["last_review_iter"] = n
        self.events("review_requested", iteration=n, file=str(path), required=rc["required"])
        if rc["required"]:
            reply = self.run_dir / f"review-reply-{n}.md"
            t0 = time.time()
            while not reply.exists():
                if self.stop_requested():
                    raise StopRequested()
                self.events("review_waiting", iteration=n, waited_s=round(time.time() - t0))
                time.sleep(rc["poll_interval_s"])
            self.state["review_wait_s"] += time.time() - t0
            self.events("review_reply_received", iteration=n, waited_s=round(time.time() - t0))

    # ---------------- one iteration ----------------
    def iteration(self, n: int) -> dict:
        L = self.L
        st = self.state
        t_start = time.time()
        wait_s = 0.0
        self.tools.iteration = n
        self.tools.reads_before_write = int(self.cfg["limits"].get("reads_before_write", 0) or 0)
        tests_before = st["tests_last"]
        hashes_before = self.writable_hashes()
        replies = self.pending_replies()
        groups = [m["name"] for m in self.cfg["milestones"]]
        system = SYSTEM_PROMPT.format(
            writable=", ".join(self.cfg["paths"]["writable"]), groups=", ".join(groups),
            turns=L["max_turns_per_iteration"], tokens=L["iteration_token_cap"],
            minutes=round(L["iteration_time_limit_s"] / 60), allow=", ".join(self.cfg["commands"]["allowlist"]))
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": self.build_context(n, replies)}]
        for m in messages:
            self.tlog(n, 0, "message", {"message": m})
        if replies:
            st["injected_replies"] += [r[0] for r in replies]
        prompt_tok = comp_tok = 0
        tool_rows = []
        end_reason = None
        nudged = False
        length_nudges = 0
        turn = 0
        violations_before = len(self.tools.violations)
        while True:
            turn += 1
            active = time.time() - t_start - wait_s
            if self.stop_requested():
                end_reason = "stop_file"
                break
            if turn > L["max_turns_per_iteration"]:
                end_reason = "turn_cap"
                break
            if comp_tok >= L["iteration_token_cap"]:
                end_reason = "token_cap"
                break
            if active >= L["iteration_time_limit_s"]:
                end_reason = "time_limit"
                break
            near = (comp_tok >= 0.85 * L["iteration_token_cap"] or turn >= L["max_turns_per_iteration"] - 1
                    or active >= 0.85 * L["iteration_time_limit_s"])
            if near and not nudged:
                nudged = True
                m = {"role": "user", "content": "Iteration budget nearly used. Call note() now with what you "
                     "tried, what you learned and the next step, then end_iteration."}
                messages.append(m)
                self.tlog(n, turn, "message", {"message": m})
            elided = self.compact(messages)
            if elided:
                self.tlog(n, turn, "compaction", {"elided_tool_results": elided})
            max_tok = int(max(256, min(self.cfg["endpoint"]["per_request_max_tokens"],
                                       L["iteration_token_cap"] - comp_tok)))
            payload = {"model": self.cfg["endpoint"]["model"], "messages": messages, "tools": self.tools.schemas,
                       "tool_choice": "auto", "max_tokens": max_tok,
                       "temperature": self.cfg["endpoint"]["temperature"], **self.cfg["endpoint"]["extra_params"]}
            try:
                resp, w = self.client.chat(payload)
            except EndpointError as e:
                wait_s += 0
                self.tlog(n, turn, "endpoint_error", {"error": str(e)})
                self.events("endpoint_error", iteration=n, error=str(e)[:300])
                if "context" in str(e).lower() or "too long" in str(e).lower() or "maximum" in str(e).lower():
                    # force a hard compaction once, then give up the iteration
                    for m in messages[2:-2]:
                        if m["role"] == "tool":
                            m["content"] = m["content"][:200]
                    try:
                        resp, w = self.client.chat(payload | {"messages": messages})
                    except EndpointError:
                        end_reason = "endpoint_error"
                        break
                else:
                    end_reason = "endpoint_error"
                    break
            wait_s += w
            usage = resp.get("usage") or {}
            prompt_tok += int(usage.get("prompt_tokens") or 0)
            comp_tok += int(usage.get("completion_tokens") or 0)
            choice = (resp.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            finish = choice.get("finish_reason")
            self.tlog(n, turn, "response", {"response": resp, "wait_s": round(w, 1)})
            tcs = msg.get("tool_calls") or []
            for i, tc in enumerate(tcs):
                if not tc.get("id"):
                    tc["id"] = f"call_{n}_{turn}_{i}"
                tc.setdefault("type", "function")
                fnc = tc.get("function") or {}
                if not isinstance(fnc.get("arguments"), str):
                    fnc["arguments"] = json.dumps(fnc.get("arguments") or {})
            amsg = {"role": "assistant", "content": msg.get("content") or ""}
            if tcs:
                amsg["tool_calls"] = tcs
            messages.append(amsg)
            if not tcs:
                if finish == "length" and length_nudges < 2:
                    length_nudges += 1
                    m = {"role": "user", "content": "Your reply was cut off by the token limit. Be brief and use tool calls."}
                    messages.append(m)
                    self.tlog(n, turn, "message", {"message": m})
                    continue
                end_reason = "model_done"
                break
            ended = False
            for tc in tcs:
                name = tc["function"].get("name", "")
                raw_args = tc["function"].get("arguments") or "{}"
                try:
                    args = json.loads(raw_args) if raw_args.strip() else {}
                    if not isinstance(args, dict):
                        raise ValueError("arguments must be a JSON object")
                    result, ok = self.tools.dispatch(name, args)
                except (json.JSONDecodeError, ValueError) as e:
                    args, result, ok = {}, f"error: could not parse tool arguments as JSON: {e}", False
                capped = cap_text(result, L["tool_result_max_chars"],
                                  "use read_file with start_line/end_line or a narrower query")
                tmsg = {"role": "tool", "tool_call_id": tc["id"], "content": capped}
                messages.append(tmsg)
                self.tlog(n, turn, "tool", {"tool_call_id": tc["id"], "name": name, "arguments": args,
                                            "result_full": result, "result_sent_chars": len(capped), "ok": ok})
                row = {"name": name, "args_sha": sha16(raw_args), "ok": ok, "result_chars": len(result)}
                if isinstance(args.get("path"), str):
                    row["path"] = args["path"]
                if name == "run_command" and isinstance(args.get("cmd"), str):
                    row["prog"] = (args["cmd"].split() or [""])[0]
                tool_rows.append(row)
                if name == "end_iteration":
                    ended = True
            if ended:
                end_reason = "end_iteration"
                break
        # ---- after the model's turns ----
        violations = self.verify_protected()
        refused = self.tools.violations[violations_before:]
        if violations:
            self.events("protected_files_restored", iteration=n, files=[v["path"] for v in violations][:10])
        results, raw = self.tests.run()
        (self.run_dir / f"tests-{n}.txt").write_text(raw)
        hashes_after = self.writable_hashes()
        changed = sorted({k for k in set(hashes_before) | set(hashes_after)
                          if hashes_before.get(k) != hashes_after.get(k)})
        before_c, after_c = counts(tests_before), counts(results)
        with open(self.worklog, "a") as f:
            f.write(f"\n[harness] iter {n} ended ({end_reason}); tests: "
                    + "; ".join(f"{g} {before_c.get(g, {}).get('passed', 0)}->{v['passed']}/{v['total']}"
                                for g, v in after_c.items())
                    + (f"; files changed: {', '.join(changed[:8])}" if changed else "; no file changes") + "\n")
        sha = None
        if moved(tests_before, results):
            msg = f"iter {n}: " + "; ".join(
                f"{g} {before_c.get(g, {}).get('passed', 0)}/{before_c.get(g, {}).get('total', 0)} -> {v['passed']}/{v['total']}"
                for g, v in after_c.items())
            sha = self.git.commit_all(msg)
        for g, r in results.items():
            st["max_total"][g] = max(st["max_total"].get(g, 0), r["total"])
        newly = [g for g, r in results.items()
                 if r["total"] and r["passed"] == r["total"] and g not in st["milestones_passed"]]
        st["milestones_passed"] = sorted(set(st["milestones_passed"]) |
                                         set(newly)) if newly else st["milestones_passed"]
        wall = time.time() - t_start
        # cap and stop checks break before the model call of the current turn
        if end_reason in ("stop_file", "turn_cap", "token_cap", "time_limit"):
            turn -= 1
        row = {
            "iteration": n, "attempt": st["attempts"].get(str(n), 1), "ts_start": datetime.fromtimestamp(t_start).astimezone().isoformat(timespec="seconds"),
            "ts_end": now_iso(), "wall_s": round(wall, 1), "endpoint_wait_s": round(wait_s, 1),
            "turns": turn, "prompt_tokens": prompt_tok, "completion_tokens": comp_tok,
            "end_reason": end_reason, "tools": tool_rows, "files_changed": changed,
            "tests_before": before_c, "tests_after": after_c, "commit": sha,
            "milestones_newly_passed": newly, "review_replies_injected": [r[0] for r in replies],
            "path_refusals": refused, "protected_restored": violations,
        }
        append_jsonl(self.f_iter, row)
        st["tests_last"] = results
        st["iteration"] = n
        st["in_progress"] = None
        st["tokens"]["prompt"] += prompt_tok
        st["tokens"]["completion"] += comp_tok
        st["endpoint_wait_s"] += wait_s
        excl = wait_s if self.L["wall_clock_excludes_waits"] else 0.0
        st["active_s"] += wall - excl
        st["violations"] += len(violations)
        self.save_state()
        self.events("iteration_done", iteration=n, end=end_reason, turns=turn, ptok=prompt_tok, ctok=comp_tok,
                    wall_s=round(wall), tests=" ".join(f"{g}={v['passed']}/{v['total']}" for g, v in after_c.items()),
                    commit=(sha or "-")[:10])
        self.review_hook(n, newly)
        self.save_state()
        self.write_summary()
        return row

    # ---------------- the loop ----------------
    def run(self, resume: bool) -> dict:
        if resume:
            self.resume_run()
        else:
            self.init_run()
        st = self.state
        session_start = time.time()
        reason = None
        try:
            while True:
                if self.stop_requested():
                    reason = "stop_file"
                elif all_pass(st["tests_last"]):
                    reason = "all_milestones_passed"
                elif st["iteration"] >= self.L["max_iterations"]:
                    reason = "max_iterations"
                elif st["active_s"] >= self.L["max_wall_hours"] * 3600:
                    reason = "wall_clock_cap"
                if reason:
                    break
                n = st["iteration"] + 1
                st["in_progress"] = n
                st["attempts"][str(n)] = st["attempts"].get(str(n), 0) + 1
                self.save_state()
                self.events("iteration_start", iteration=n, attempt=st["attempts"][str(n)])
                try:
                    self.iteration(n)
                except StopRequested:
                    reason = "stop_file"
                    st["in_progress"] = None
                    break
        except KeyboardInterrupt:
            reason = "interrupted"
            st["status"] = "interrupted"
            st["stop_reason"] = reason
            self.save_state()
            self.write_summary()
            self.events("run_interrupted", iteration=st.get("in_progress"))
            raise
        st["status"] = "stopped"
        st["stop_reason"] = reason
        self.git.commit_all(f"wl-builder: run {self.run_id} stopped ({reason}) after iteration {st['iteration']}")
        self.save_state()
        self.write_summary()
        self.events("run_stop", reason=reason, iterations=st["iteration"], tokens=st["tokens"],
                    session_s=round(time.time() - session_start))
        return st


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

TOY_SPEC = {
    "SPEC/index.md": """# Toy library spec

This project is a small pure-Python library with two modules. Implement them under `src/`.

- `src/roman.py`: Roman numeral conversion. See `roman.md`.
- `src/rle.py`: run-length encoding codec. See `rle.md`.

`src/__init__.py` already exists. Tests import `from src.roman import ...` and `from src.rle import ...`.
""",
    "SPEC/roman.md": """# Roman numerals

## to_roman(n)

`to_roman(n: int) -> str` returns the canonical upper-case Roman numeral for `n`.

- Valid range is 1 to 3999 inclusive. Anything else (including 0, negatives and 4000) raises `ValueError`.
- A non-int argument (for example a float or a string) raises `TypeError`. `bool` counts as non-int.
- Canonical form uses subtractive pairs: IV, IX, XL, XC, CD, CM. Examples: 4 is IV, 1994 is MCMXCIV, 3999 is MMMCMXCIX.

## from_roman(s)

`from_roman(s: str) -> int` parses a numeral and returns its value.

- Only canonical upper-case numerals are accepted. The rule: `s` is valid if and only if `to_roman(from_value) == s`.
- Invalid input raises `ValueError`. Examples of invalid input: "", "IIII", "VV", "IC", "XM", "abc", "iv", "MMMM".
""",
    "SPEC/rle.md": """# Run-length codec

## encode(s)

`encode(s: str) -> str` replaces each maximal run of a repeated character with the decimal run length
followed by the character. Every run gets a count, including runs of length 1.

- `encode("AAAB")` is `"3A1B"`; `encode("")` is `""`; `encode("W" * 12)` is `"12W"`.
- Characters are any non-digit characters, including spaces and punctuation.
- If `s` contains a decimal digit (0-9), raise `ValueError`.

## decode(s)

`decode(s: str) -> str` is the inverse of `encode`.

- The input is a sequence of (count, character) pairs; count is one or more digits with no leading zero.
- Malformed input raises `ValueError`: a trailing count with no character ("3"), a character with no count ("A"),
  a zero or leading-zero count ("0A", "03A").
- `decode(encode(s)) == s` for every valid `s`.
""",
}

TOY_TESTS = {
    "tests/test_roman.py": '''import pytest
from src.roman import to_roman, from_roman


def test_to_roman_small():
    assert [to_roman(i) for i in (1, 2, 3, 4, 5, 9, 14)] == ["I", "II", "III", "IV", "V", "IX", "XIV"]


def test_to_roman_large():
    assert to_roman(40) == "XL"
    assert to_roman(90) == "XC"
    assert to_roman(400) == "CD"
    assert to_roman(1994) == "MCMXCIV"
    assert to_roman(3999) == "MMMCMXCIX"


def test_from_roman_basic():
    assert from_roman("MCMXCIV") == 1994
    assert from_roman("XLII") == 42
    assert from_roman("I") == 1


def test_roundtrip_all():
    for i in range(1, 4000):
        assert from_roman(to_roman(i)) == i


def test_to_roman_range_and_type():
    for bad in (0, -1, 4000):
        with pytest.raises(ValueError):
            to_roman(bad)
    for bad in (1.5, "3", True):
        with pytest.raises(TypeError):
            to_roman(bad)


def test_from_roman_rejects_noncanonical():
    for bad in ("", "IIII", "VV", "IC", "XM", "abc", "iv", "MMMM"):
        with pytest.raises(ValueError):
            from_roman(bad)
''',
    "tests/test_rle.py": '''import pytest
from src.rle import encode, decode


def test_encode_basic():
    assert encode("AAAB") == "3A1B"
    assert encode("ab") == "1a1b"


def test_encode_empty():
    assert encode("") == ""
    assert decode("") == ""


def test_encode_long_runs():
    assert encode("W" * 12 + "B") == "12W1B"
    assert encode("  !!") == "2 2!"


def test_decode_basic():
    assert decode("3A1B") == "AAAB"
    assert decode("12W1B") == "W" * 12 + "B"


def test_roundtrip():
    for s in ("a", "hello  world", "zzzzzzzzzzzzzzzzzzzzzzzzzy", "x-y-z!!"):
        assert decode(encode(s)) == s


def test_invalid_inputs():
    with pytest.raises(ValueError):
        encode("a1")
    for bad in ("3", "A", "0A", "03A", "3A4"):
        with pytest.raises(ValueError):
            decode(bad)
''',
}


def make_toy_project(root: Path, endpoint: str, model: str, extra: dict | None = None) -> Path:
    proj = root / "project"
    for rel, text in {**TOY_SPEC, **TOY_TESTS}.items():
        p = proj / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    (proj / "src").mkdir(parents=True, exist_ok=True)
    (proj / "src" / "__init__.py").write_text("")
    (proj / "tests" / "fixtures-generated").mkdir(parents=True, exist_ok=True)
    extra = extra or {}
    toml = f'''# selftest config
[endpoint]
base_url = "{endpoint}"
model = "{model}"
temperature = 0.2
per_request_max_tokens = 6000
retry_window_s = 30
backoff_initial_s = 2
backoff_max_s = 8
poll_interval_s = 5

[project]
dir = "project"
runs_dir = "runs"
stop_file = "STOP"
test_timeout_s = 120

[limits]
max_iterations = {extra.get("max_iterations", 8)}
max_wall_hours = 1.0
iteration_token_cap = 24000
max_turns_per_iteration = 5
iteration_time_limit_s = 600
context_budget_tokens = 60000
tool_result_max_chars = 6000

[review]
every_k = 2
on_milestone = true
required = false

[[milestones]]
name = "roman"
select = "tests/test_roman.py"

[[milestones]]
name = "rle"
select = "tests/test_rle.py"
'''
    (root / "harness.toml").write_text(toml)
    return root / "harness.toml"


class _Proxy(http.server.BaseHTTPRequestHandler):
    upstream = ""

    def _fwd(self, method):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else None
        req = urllib.request.Request(self.upstream + self.path, data=body, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                data, code = r.read(), r.status
        except urllib.error.HTTPError as e:
            data, code = e.read(), e.code
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._fwd("GET")

    def do_POST(self):
        self._fwd("POST")

    def log_message(self, *a):
        pass


def selftest(harness_path: Path) -> int:
    endpoint = "http://127.0.0.1:1234/v1"
    model = "Qwen/Qwen3.6-35B-A3B"
    root = Path(os.path.realpath(tempfile.mkdtemp(prefix="wl-selftest-")))
    cfg_path = make_toy_project(root, endpoint, model)
    proj = root / "project"
    checks: list[tuple[str, bool, str]] = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{(' : ' + detail) if detail else ''}", flush=True)

    print(f"selftest root: {root}")
    print(f"endpoint: {endpoint} model: {model}")
    t_all = time.time()

    # 0. endpoint reachable
    ev0 = EventLog(None, echo=False)
    probe = LLMClient(deep_merge(DEFAULT_CONFIG["endpoint"], {"base_url": endpoint}), ev0)
    if not probe.alive():
        print("LM Studio is not answering at", endpoint)
        return 2

    # 1. path guard (no model involved)
    print("\n== path guard ==")
    cfg = load_config(cfg_path)
    guard = PathGuard(cfg["project"]["dir"], cfg["paths"]["writable"])
    sb = Sandbox("auto", [str(proj / "src"), str(proj / "tests" / "fixtures-generated"), str(root / "scratch")])
    os.makedirs(root / "scratch", exist_ok=True)
    tr = TestRunner(cfg, sb, str(root / "scratch"))
    tools = Tools(cfg, guard, Spec(cfg["project"]["dir"]), tr, sb, proj / "WORKLOG.md")
    spec_before = (proj / "SPEC" / "roman.md").read_text()
    attempts = {
        "write_file SPEC/roman.md": tools.dispatch("write_file", {"path": "SPEC/roman.md", "content": "hacked"}),
        "write_file SPEC/new.md": tools.dispatch("write_file", {"path": "SPEC/new.md", "content": "x"}),
        "apply_patch SPEC/roman.md": tools.dispatch("apply_patch", {"path": "SPEC/roman.md",
                                                                    "unified_diff": "@@ -1,1 +1,1 @@\n-# Roman numerals\n+# hacked\n"}),
        "write_file tests/test_roman.py": tools.dispatch("write_file", {"path": "tests/test_roman.py", "content": "x"}),
        "write_file ../escape.txt": tools.dispatch("write_file", {"path": "../escape.txt", "content": "x"}),
        "write_file src/../SPEC/x.md": tools.dispatch("write_file", {"path": "src/../SPEC/x.md", "content": "x"}),
        "run_command curl": tools.dispatch("run_command", {"cmd": "curl http://example.com"}),
        "run_command cat /etc/hosts": tools.dispatch("run_command", {"cmd": "cat /etc/hosts"}),
    }
    refused_all = all((not ok) and "refused" in res for res, ok in attempts.values())
    unchanged = (proj / "SPEC" / "roman.md").read_text() == spec_before and not (proj / "SPEC" / "new.md").exists() \
        and not (root / "escape.txt").exists()
    bad = [k for k, (res, ok) in attempts.items() if ok or "refused" not in res]
    check("path guard refuses writes to SPEC/, tests/, outside the project, and off-allowlist commands",
          refused_all and unchanged, "all 8 refused, files untouched" if not bad else f"not refused: {bad}")
    res_ok, ok = tools.dispatch("write_file", {"path": "src/_probe.py", "content": "x = 1\n"})
    patch_res, pok = tools.dispatch("apply_patch", {"path": "src/_probe.py", "unified_diff": "@@ -1,1 +1,2 @@\n x = 1\n+y = 2\n"})
    check("path guard allows src/ writes and apply_patch works",
          ok and pok and (proj / "src" / "_probe.py").read_text() == "x = 1\ny = 2\n", patch_res)
    os.unlink(proj / "src" / "_probe.py")
    # sandbox: model-run python cannot write outside src or reach the network
    esc, _ = tools.dispatch("run_command", {"cmd": f"python3 -c \"open('SPEC/evil.md','w').write('x')\""})
    net, _ = tools.dispatch("run_command", {"cmd": "python3 -c \"import urllib.request as u; u.urlopen('http://127.0.0.1:1234/v1/models', timeout=3); print('NETWORK' + '-OK')\""})
    # the marker is built at runtime because Python 3.14 echoes the -c source in tracebacks
    wrote = (proj / "SPEC" / "evil.md").exists()
    reached = "NETWORK-OK" in net
    check(f"sandbox ({sb.kind}) blocks python writes to SPEC/ and network from tools",
          sb.kind != "none" and not wrote and not reached and "Operation not permitted" in esc,
          f"write denied={not wrote}, network denied={not reached}")

    # 2. stop file
    print("\n== stop file ==")
    (root / "STOP").write_text("stop")
    b = Builder(load_config(cfg_path), run_id="stopcheck", echo=False)
    st = b.run(resume=False)
    os.unlink(root / "STOP")
    check("stop file halts the loop before any model call", st["stop_reason"] == "stop_file" and st["iteration"] == 0,
          f"stop_reason={st['stop_reason']}")

    # 3. main run, interrupted mid-iteration, then resumed
    print("\n== main run (interrupted, then resumed) ==")
    run_id = "selftest-main"
    run_dir = root / "runs" / run_id
    log1 = open(root / "phase1.log", "w")
    p = subprocess.Popen([sys.executable, str(harness_path), "--config", str(cfg_path), "--run-id", run_id],
                         stdout=log1, stderr=subprocess.STDOUT)
    killed = False
    t0 = time.time()
    while p.poll() is None and time.time() - t0 < 1200:
        trans = run_dir / "transcript.jsonl"
        if trans.exists():
            tool_rows = sum(1 for line in trans.read_text().splitlines() if '"kind": "tool"' in line)
            if tool_rows >= 3:
                p.send_signal(signal.SIGKILL)
                p.wait()
                killed = True
                break
        time.sleep(0.5)
    log1.close()
    st_mid = json.loads((run_dir / "state.json").read_text()) if (run_dir / "state.json").exists() else {}
    check("run was killed mid-iteration (SIGKILL after 3 tool calls)",
          killed and st_mid.get("in_progress") is not None,
          f"in_progress={st_mid.get('in_progress')} after {round(time.time() - t0)} s")
    log2 = open(root / "phase2.log", "w")
    p2 = subprocess.run([sys.executable, str(harness_path), "--config", str(cfg_path), "--resume", run_id],
                        stdout=log2, stderr=subprocess.STDOUT, timeout=6 * 3600)
    log2.close()
    st = json.loads((run_dir / "state.json").read_text())
    events = [json.loads(l) for l in (run_dir / "events.jsonl").read_text().splitlines()]
    iters = [json.loads(l) for l in (run_dir / "iterations.jsonl").read_text().splitlines()] \
        if (run_dir / "iterations.jsonl").exists() else []
    resumed_evt = any(e["event"] == "resume_interrupted_iteration" for e in events)
    check("resume continues after the interrupted iteration",
          p2.returncode == 0 and resumed_evt and st["status"] == "stopped" and iters and iters[0]["iteration"] == 1
          and iters[0]["attempt"] == 2,
          f"exit={p2.returncode} stop_reason={st['stop_reason']} iterations={st['iteration']} "
          f"first_row_attempt={iters[0]['attempt'] if iters else None}")

    # 4. edited only allowed paths
    g = Git(str(proj))
    changed = [l for l in g.run("diff", "--name-only", st["baseline_sha"], "HEAD").splitlines() if l]
    untracked = [l[3:] for l in g.run("status", "--porcelain").splitlines()]
    outside = [f for f in changed + untracked if not (f.startswith("src/") or f.startswith("tests/fixtures-generated/")
                                                      or f == "WORKLOG.md")]
    refusals = sum(len(r["path_refusals"]) for r in iters)
    check("model edited only src/ (plus the harness-managed WORKLOG.md)",
          not outside and st["violations"] == 0 and any(f.startswith("src/") for f in changed),
          f"changed={changed} outside={outside} protected_restores={st['violations']} refused_writes={refusals}")

    # 5. improvement
    base = st["baseline_tests"]
    final = counts(st["tests_last"])
    improved = [gname for gname in final if final[gname]["passed"] > base.get(gname, {}).get("passed", 0)]
    check("at least one milestone group improved",
          bool(improved),
          "; ".join(f"{k} {base.get(k, {}).get('passed', 0)}/{base.get(k, {}).get('total', 0)} -> "
                    f"{v['passed']}/{v['total']}" for k, v in final.items()))

    # 6. logs and commits
    commits = g.run("log", "--oneline").splitlines()
    need = ["iterations.jsonl", "transcript.jsonl", "summary.json", "events.jsonl", "state.json", "tests-0.txt"]
    missing = [f for f in need if not (run_dir / f).exists()]
    per_iter = [f"tests-{r['iteration']}.txt" for r in iters if not (run_dir / f"tests-{r['iteration']}.txt").exists()]
    summ = json.loads((run_dir / "summary.json").read_text())
    trans_rows = len((run_dir / "transcript.jsonl").read_text().splitlines())
    iter_commits = [c for c in commits if " iter " in c or c.split(" ", 1)[1].startswith("iter ")]
    check("logs exist (iterations, transcript, per-iteration tests, summary series)",
          not missing and not per_iter and len(summ["series"]) == len(iters) + 1 and trans_rows > 0,
          f"iterations={len(iters)} transcript_rows={trans_rows} series_points={len(summ['series'])}")
    check("git commits exist in the project repo for iterations whose tests moved",
          len(iter_commits) >= 1 and all(r["commit"] for r in iters if moved_counts(r)),
          f"{len(commits)} commits, {len(iter_commits)} iteration commits")
    reviews = sorted(x.name for x in run_dir.glob("review-request-*.md"))
    check("review requests written (every 2 iterations or on milestone pass)", bool(reviews), ", ".join(reviews))

    # 7. endpoint outage: dead port for 20 s, short backoff, then a proxy to LM Studio comes up
    print("\n== endpoint outage ==")
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    ev = EventLog(root / "outage-events.jsonl", echo=True)
    ecfg = deep_merge(DEFAULT_CONFIG["endpoint"], {"base_url": f"http://127.0.0.1:{port}/v1",
                                                   "retry_window_s": 6, "backoff_initial_s": 1,
                                                   "backoff_max_s": 2, "poll_interval_s": 3,
                                                   "request_timeout_s": 300})
    client = LLMClient(ecfg, ev)
    out: dict = {}

    def call():
        try:
            out["resp"], out["wait"] = client.chat({"model": model, "max_tokens": 64, "messages": [
                {"role": "user", "content": "Reply with the single word: ready"}]})
        except Exception as e:
            out["err"] = repr(e)
    th = threading.Thread(target=call)
    t_out = time.time()
    th.start()
    time.sleep(20)
    _Proxy.upstream = endpoint.rsplit("/v1", 1)[0]
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), _Proxy)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    th.join(timeout=300)
    srv.shutdown()
    kinds = [e["event"] for e in ev.rows]
    ok = "resp" in out and "endpoint_retry" in kinds and "endpoint_paused" in kinds and "endpoint_recovered" in kinds
    check("endpoint outage: retries, pauses (sleep-poll), recovers when the endpoint returns",
          ok, f"events: {kinds.count('endpoint_retry')} retry, {kinds.count('endpoint_paused')} paused, "
              f"{kinds.count('endpoint_waiting')} waiting, {kinds.count('endpoint_recovered')} recovered; "
              f"waited {round(out.get('wait', 0), 1)} s; total {round(time.time() - t_out, 1)} s"
              + (f"; error {out['err']}" if "err" in out else ""))

    # report
    print("\n== token usage (main run) ==")
    print(f"  iterations: {len(iters)} (plus 1 interrupted attempt)")
    print(f"  prompt tokens: {st['tokens']['prompt']}  completion tokens: {st['tokens']['completion']}")
    killed_turns = [json.loads(l) for l in (run_dir / "transcript.jsonl").read_text().splitlines()
                    if '"kind": "response"' in l]
    k_p = sum((r["response"].get("usage") or {}).get("prompt_tokens", 0) for r in killed_turns if r["iteration"] == 1)
    k_c = sum((r["response"].get("usage") or {}).get("completion_tokens", 0) for r in killed_turns if r["iteration"] == 1)
    print(f"  iteration 1 across both attempts (from transcript): prompt {k_p}, completion {k_c}")
    print(f"  stop reason: {st['stop_reason']}; active {round(st['active_s'])} s; selftest wall {round(time.time() - t_all)} s")
    print(f"  run dir: {run_dir}")
    npass = sum(1 for c in checks if c[1])
    print(f"\nSELFTEST {'PASSED' if npass == len(checks) else 'FAILED'}: {npass}/{len(checks)} checks passed")
    return 0 if npass == len(checks) else 1


def moved_counts(row: dict) -> bool:
    a = {k: (v["passed"], v["total"]) for k, v in row["tests_before"].items()}
    b = {k: (v["passed"], v["total"]) for k, v in row["tests_after"].items()}
    return a != b


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Unattended builder loop for a local model.")
    ap.add_argument("--config", default="harness.toml", help="harness.toml or .json")
    ap.add_argument("--resume", nargs="?", const="", default=None, metavar="RUN_ID",
                    help="continue the given run (default: the most recent run)")
    ap.add_argument("--run-id", default=None, help="name for a new run (default: timestamp-model)")
    ap.add_argument("--selftest", action="store_true", help="run the self-test against LM Studio")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(Path(__file__).resolve())
    cfg = load_config(a.config)
    resume = a.resume is not None
    b = Builder(cfg, run_id=(a.resume or None) if resume else a.run_id, resume=resume)

    def on_term(signum, frame):
        raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, on_term)
    try:
        st = b.run(resume=resume)
    except KeyboardInterrupt:
        print("interrupted; continue with --resume " + b.run_id, flush=True)
        return 130
    print(json.dumps({"run_id": b.run_id, "stop_reason": st["stop_reason"], "iterations": st["iteration"],
                      "tokens": st["tokens"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
