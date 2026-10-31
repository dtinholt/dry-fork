"""Shared helpers for the PREREG-W1 acceptance tests (SPEC-07).

This module is test infrastructure, not an oracle for any single answer:

- `api()` / `call()` reach into the builder's `wlengine` package and turn every
  engine-side problem (missing module, missing function, NotImplementedError,
  any other exception) into a clean test failure with a one-line message.
- `check_eq()` and friends report the first difference only, so a failure never
  prints more of the expected data than the single case being checked.
- The `ref_*` functions and `RefRng` are independent restatements of SPEC-04
  formulas, used to compute expected values. They are not the engine.

Frozen with the tests. The engine must not import this module.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
PROJECT = TESTS.parent
SRC = PROJECT / "src"
SPEC = PROJECT / "SPEC"
SCENARIO = SPEC / "scenario"
REFERENCE = SPEC / "reference"
REFERENCE_LOG = SCENARIO / "walkthrough-reference-log.json"

# Paths the engine must never open while it is under test (set up by conftest).
FORBIDDEN_PREFIXES: list[str] = [str(REFERENCE) + os.sep, str(REFERENCE_LOG)]

_STATE = {"armed": 0, "violations": [], "allow_reference_log": False}


# ---------------------------------------------------------------------------
# Failure helpers
# ---------------------------------------------------------------------------

def fail(msg: str) -> None:
    """Fail the current test with exactly `msg` and no traceback."""
    pytest.fail(msg, pytrace=False)


def short(v, limit: int = 160) -> str:
    if isinstance(v, (bytes, bytearray)):
        h = bytes(v).hex(" ").upper()
        s = "bytes[%d] %s" % (len(v), h)
    else:
        s = repr(v)
    return s if len(s) <= limit else s[:limit] + "..."


def norm(v):
    """Normalise an engine value for comparison: tuples become lists, integer
    dict keys become strings, bytearray becomes bytes. Values are untouched."""
    if isinstance(v, dict):
        return {(str(k) if isinstance(k, int) else k): norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    if isinstance(v, bytearray):
        return bytes(v)
    return v


def first_diff(got, want, path: str = ""):
    """Return (path, got_part, want_part) of the first difference, or None."""
    if isinstance(want, dict):
        if not isinstance(got, dict):
            return (path or "<root>", got, "a dict")
        for k in want:
            if k not in got:
                return ("%s.%s" % (path, k) if path else k, "<missing key>", want[k])
            d = first_diff(got[k], want[k], "%s.%s" % (path, k) if path else str(k))
            if d:
                return d
        extra = [k for k in got if k not in want]
        if extra:
            return ("%s.%s" % (path, extra[0]) if path else str(extra[0]), got[extra[0]], "<no such key>")
        return None
    if isinstance(want, list):
        if not isinstance(got, list):
            return (path or "<root>", got, "a list of %d items" % len(want))
        for i, (g, w) in enumerate(zip(got, want)):
            d = first_diff(g, w, "%s[%d]" % (path, i))
            if d:
                return d
        if len(got) != len(want):
            return ("%s (length)" % (path or "<root>"), len(got), len(want))
        return None
    return None if got == want else (path or "<root>", got, want)


def check_eq(what: str, got, want) -> None:
    """Compare after normalising; report only the first differing element."""
    g = norm(got)
    if g == want:
        return
    d = first_diff(g, want)
    if d is None:  # equal under first_diff's rules but not ==, report whole case
        fail("%s: expected %s, got %s" % (what, short(want), short(g)))
    p, gv, wv = d
    if p in ("<root>", ""):
        fail("%s: expected %s, got %s" % (what, short(wv), short(gv)))
    fail("%s: first difference at %s: expected %s, got %s" % (what, p, short(wv), short(gv)))


def check_bytes(what: str, got, want: bytes) -> None:
    if not isinstance(got, (bytes, bytearray)):
        fail("%s: expected bytes, got %s" % (what, type(got).__name__))
    got = bytes(got)
    if got == want:
        return
    n = min(len(got), len(want))
    i = next((k for k in range(n) if got[k] != want[k]), n)
    if i == n:
        fail("%s: expected %d bytes, got %d (common prefix identical)" % (what, len(want), len(got)))
    fail("%s: first differing byte at offset %d: expected %02X, got %02X (lengths: expected %d, got %d)"
         % (what, i, want[i], got[i], len(want), len(got)))


# ---------------------------------------------------------------------------
# Engine access
# ---------------------------------------------------------------------------

_ENGINE = {"checked": False, "error": None}

ORACLE_NAMES = ("codecs_ref", "fixtures_gen", "_wl_oracle", "oracle_tool", "wl_support",
                "wl_combat_ref", "walkthrough-reference-log", "reference-log", "reference_log")


def _scan_sources() -> str | None:
    """SPEC-07 section 6: src/ must not name the oracle modules or files."""
    if not SRC.is_dir():
        return None
    for p in sorted(SRC.rglob("*.py")):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for name in ORACLE_NAMES:
                if name in line:
                    return "%s line %d names %r" % (p.relative_to(PROJECT), lineno, name)
    return None


def engine_ready() -> None:
    """Fail the test unless `wlengine` imports cleanly and src/ is clean."""
    if not _ENGINE["checked"]:
        _ENGINE["checked"] = True
        bad = _scan_sources()
        if bad:
            _ENGINE["error"] = ("SPEC-07 rule 6.1: src/ must not reference the oracle modules or the "
                                "reference log (%s)" % bad)
        else:
            try:
                _armed(lambda: importlib.import_module("wlengine"))
            except Exception as e:  # noqa: BLE001
                _ENGINE["error"] = "cannot import wlengine from src/: %s: %s" % (type(e).__name__, e)
    if _ENGINE["error"]:
        fail(_ENGINE["error"])


def _armed(fn, *a, allow_reference_log=False, **k):
    _STATE["armed"] += 1
    prev = _STATE["allow_reference_log"]
    _STATE["allow_reference_log"] = allow_reference_log
    try:
        return fn(*a, **k)
    finally:
        _STATE["armed"] -= 1
        _STATE["allow_reference_log"] = prev


def audit_hook(event, args):
    if not _STATE["armed"] or event != "open" or not args:
        return
    p = args[0]
    if isinstance(p, int):
        return
    try:
        p = os.fspath(p)
        if isinstance(p, bytes):
            p = p.decode("utf-8", "replace")
        p = os.path.abspath(p)
    except Exception:  # noqa: BLE001
        return
    for pref in FORBIDDEN_PREFIXES:
        if _STATE["allow_reference_log"] and pref == str(REFERENCE_LOG):
            continue
        if p == pref.rstrip(os.sep) or p.startswith(pref):
            _STATE["violations"].append(p)


def _module_violation() -> str | None:
    spec_dir = str(SPEC) + os.sep
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if f and str(f).startswith(spec_dir) and not name.startswith("_wl_oracle_"):
            return "module %r loaded from %s" % (name, f)
    return None


def api(dotted: str):
    """Resolve 'module.function' inside wlengine, failing cleanly if absent."""
    engine_ready()
    mod_name, _, attr = dotted.rpartition(".")
    full = "wlengine." + mod_name if mod_name else "wlengine"
    try:
        mod = _armed(importlib.import_module, full)
    except Exception as e:  # noqa: BLE001
        fail("cannot import %s (SPEC-07 API): %s: %s" % (full, type(e).__name__, e))
    if not hasattr(mod, attr):
        fail("%s has no attribute %r (SPEC-07 API)" % (full, attr))
    return getattr(mod, attr)


def error_class(name: str):
    cls = api("errors." + name)
    if not (isinstance(cls, type) and issubclass(cls, Exception)):
        fail("wlengine.errors.%s must be an exception class" % name)
    if name in ("FormatError", "ChecksumError") and not issubclass(cls, ValueError):
        fail("wlengine.errors.%s must subclass ValueError (SPEC-07 section 3)" % name)
    if name == "ChecksumError" and not issubclass(cls, api("errors.FormatError")):
        fail("wlengine.errors.ChecksumError must subclass FormatError (SPEC-07 section 3)")
    if cls in (Exception, ValueError, BaseException) or issubclass(NotImplementedError, cls):
        fail("wlengine.errors.%s must be a dedicated class (SPEC-07 section 3)" % name)
    return cls


def _after_call(label: str) -> None:
    if _STATE["violations"]:
        p = _STATE["violations"][0]
        _STATE["violations"].clear()
        fail("%s opened a file the engine must not read (SPEC-07 rule 6.1): %s" % (label, p))
    bad = _module_violation()
    if bad:
        fail("%s: the engine loaded an oracle module (SPEC-07 rule 6.1): %s" % (label, bad))


def call(dotted: str, *args, allow_reference_log=False, **kw):
    """Call wlengine.<dotted>(*args, **kw); any exception becomes a clean failure."""
    fn = api(dotted)
    label = "wlengine." + dotted
    try:
        out = _armed(fn, *args, allow_reference_log=allow_reference_log, **kw)
    except NotImplementedError as e:
        _after_call(label)
        fail("%s: not implemented (%s)" % (label, e or "NotImplementedError"))
    except Exception as e:  # noqa: BLE001
        _after_call(label)
        fail("%s raised %s: %s" % (label, type(e).__name__, short(str(e), 200)))
    _after_call(label)
    return out


def call_capture(dotted: str, *args, allow_reference_log=False, **kw):
    """Like call() but returns (value, exception) instead of failing on an
    exception other than NotImplementedError or a missing API."""
    fn = api(dotted)
    label = "wlengine." + dotted
    try:
        out = _armed(fn, *args, allow_reference_log=allow_reference_log, **kw)
    except NotImplementedError as e:
        _after_call(label)
        fail("%s: not implemented (%s)" % (label, e or "NotImplementedError"))
    except Exception as e:  # noqa: BLE001
        _after_call(label)
        return None, e
    _after_call(label)
    return out, None


def expect_error(err_name: str, dotted: str, *args, what: str = "", **kw) -> None:
    """Pass only if wlengine.<dotted> raises wlengine.errors.<err_name>."""
    cls = error_class(err_name)
    out, exc = call_capture(dotted, *args, **kw)
    label = "wlengine." + dotted + (" (%s)" % what if what else "")
    if exc is None:
        fail("%s: expected %s, but it returned %s" % (label, err_name, short(out)))
    if not isinstance(exc, cls):
        fail("%s: expected %s, got %s: %s" % (label, err_name, type(exc).__name__, short(str(exc), 160)))


# ---------------------------------------------------------------------------
# Oracle helpers (in-process codecs_ref only; fixtures_gen runs in a subprocess)
# ---------------------------------------------------------------------------

_ORACLE = {}


def codecs_oracle():
    """SPEC/reference/codecs_ref.py loaded under a private module name."""
    if "c" not in _ORACLE:
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("_wl_oracle_codecs_ref", REFERENCE / "codecs_ref.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_wl_oracle_codecs_ref"] = mod
        spec.loader.exec_module(mod)
        _ORACLE["c"] = mod
    return _ORACLE["c"]


def load_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Independent restatements of SPEC-04 formulas (expected values only)
# ---------------------------------------------------------------------------

class RefRng:
    """SPEC-04 LR-1 and LR-2, restated for computing expected values."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF or 0x6D2B79F5

    def next(self) -> int:
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x
        return x

    def roll(self, n: int) -> int:
        return 1 + self.next() % n

    def rnd(self, n: int) -> int:
        if n == 0:
            return 0
        if n == 1:
            return 1
        return self.roll(n)

    def dice(self, n: int, s: int) -> int:
        return sum(self.roll(s) for _ in range(n))

    def d100(self) -> int:
        return self.roll(100)


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def ref_check_need(level: int, attr: int, difficulty: int, tool: bool = False) -> int:
    return 20 + 15 * level + 2 * attr - difficulty + (20 if tool else 0)


def ref_skill_check(rng: RefRng, level, attr, difficulty, tool=False) -> dict:
    need = ref_check_need(level, attr, difficulty, tool)
    if need >= 100:
        return {"need": need, "roll": None, "success": True}
    if need <= 0:
        return {"need": need, "roll": None, "success": False}
    r = rng.d100()
    return {"need": need, "roll": r, "success": r <= need}


def ref_max_hp(strength: int, level: int) -> int:
    return 10 + strength + (level - 1) * (2 + strength // 5)


def ref_ac(agility: int, armour_bonus: int, evasion: int) -> int:
    return agility // 5 + armour_bonus + evasion


def ref_ranged_need(level, agility, target_ac, band) -> int:
    return clamp(35 + 12 * level + agility - 6 * target_ac - 5 * (band - 1), 5, 95)


def ref_melee_need(level, agility, target_ac) -> int:
    return clamp(35 + 12 * level + agility - 6 * target_ac, 5, 95)


def ref_monster_need(combat_rating, member_ac, band) -> int:
    return clamp(20 + 5 * combat_rating - 6 * member_ac - 5 * (band - 1), 5, 95)


def ref_flee_need(best_spd, best_monster_speed, command) -> int:
    return clamp(40 + 5 * (best_spd - best_monster_speed) + 5 * command, 5, 95)


def ref_jam_chance(gunsmithing: int) -> int:
    return max(1, 4 - gunsmithing)


def ref_xp_threshold(level: int) -> int:
    return 50 * level * (level + 1)


def ref_level_after(level: int, xp: int) -> int:
    while xp >= ref_xp_threshold(level):
        level += 1
    return level


def ref_buy_price(price: int, haggling: int) -> int:
    h = min(5, haggling)
    return price * (100 - 5 * h) // 100


def ref_sell_price(price: int, haggling: int) -> int:
    h = min(5, haggling)
    return price * (50 + 5 * h) // 100


def ref_monster_hp(rng: RefRng, sturdiness: int) -> int:
    hi = rng.rnd(sturdiness >> 8)
    lo = rng.rnd(sturdiness & 0xFF)
    return sturdiness // 4 + ((hi << 8) | lo)


def ref_damage_member(hp: int, d: int) -> dict:
    prev = hp
    hp -= d
    if hp > 0:
        return {"hp": hp, "cond": 0, "last_hp": None}
    over = d - prev
    return {"hp": 0, "cond": 2 if over >= 5 else 1, "last_hp": prev}


def ref_pay(moneys: list[int], first_slot: int, price: int):
    if sum(moneys) < price:
        return None
    out = list(moneys)
    order = [first_slot - 1] + [i for i in range(len(moneys)) if i != first_slot - 1]
    left = price
    for i in order:
        take = min(out[i], left)
        out[i] -= take
        left -= take
        if left == 0:
            break
    return out


def ref_advance_clock(clock: dict, minutes: int, seconds: int):
    day, minute, second = clock["day"], clock["minute"], clock["second"]
    total_s = second + seconds
    second = total_s % 60
    add_min = minutes + total_s // 60
    hours = []
    for _ in range(add_min):
        minute += 1
        if minute == 1440:
            minute = 0
        if minute % 60 == 0:
            h = minute // 60
            hours.append(h)
            if h == 0:
                day += 1
    return {"day": day, "minute": minute, "second": second}, hours


def ref_build_groups(rng: RefRng, mobs: list[dict], record: dict) -> list[dict]:
    counts = []
    for mob_index, rnd_flag, size in record["groups"]:
        if mob_index == 0:
            continue
        mob = mobs[mob_index - 1]
        s = size if size else mob["maxGroup"]
        counts.append((mob_index, rng.rnd(s) if rnd_flag else s))
    out = []
    for mob_index, count in counts:
        if count <= 0:
            continue
        mob = mobs[mob_index - 1]
        hp = [ref_monster_hp(rng, mob["sturdiness"]) for _ in range(count)]
        band = 3 if mob["weaponType"] >= 3 else 2
        out.append({"monster": mob_index, "count": count, "band": band, "hp": hp})
    return out


def ref_speed_order(actors: list[dict]) -> list[dict]:
    def key(a):
        party = a["side"] == "party"
        return (-a["speed"], 0 if party else 1,
                a.get("slot", 0) if party else 0,
                0 if party else a["group"], 0 if party else a["index"])
    return sorted(actors, key=key)


def ref_labstate(blob: bytes) -> dict:
    """Independent LABSTATE.BIN reader (SPEC-04 LR-57)."""
    if blob[:8] != b"WLLABSV1":
        raise ValueError("bad magic")
    n = int.from_bytes(blob[0x14:0x16], "little")
    end = 0x16 + 6 * n
    if len(blob) != end + 2:
        raise ValueError("bad length")
    if sum(blob[:end]) & 0xFFFF != int.from_bytes(blob[end:end + 2], "little"):
        raise ValueError("bad sum")
    cc = [list(blob[0x16 + 6 * i:0x16 + 6 * i + 6]) for i in range(n)]
    return {"steps": int.from_bytes(blob[8:12], "little"), "day": int.from_bytes(blob[12:14], "little"),
            "seconds": blob[14], "pad": blob[15], "rng_state": int.from_bytes(blob[16:20], "little"),
            "cell_changes": cc}


def ref_encode_labstate(state: dict) -> bytes:
    cc = sorted(state["cell_changes"], key=lambda c: (c[0], c[2], c[1]))
    b = bytearray(b"WLLABSV1")
    b += state["steps"].to_bytes(4, "little") + state["day"].to_bytes(2, "little")
    b += bytes((state["seconds"], 0)) + state["rng_state"].to_bytes(4, "little")
    b += len(cc).to_bytes(2, "little")
    for c in cc:
        b += bytes(c)
    b += (sum(b) & 0xFFFF).to_bytes(2, "little")
    return bytes(b)


def pack4(rows: list[list[int]]) -> bytes:
    out = bytearray()
    for row in rows:
        for x in range(0, len(row), 2):
            out.append((row[x] << 4) | row[x + 1])
    return bytes(out)


def unpack4(data: bytes, width: int) -> list[list[int]]:
    stride = width // 2
    return [[v for b in data[y * stride:(y + 1) * stride] for v in (b >> 4, b & 15)]
            for y in range(len(data) // stride)]
