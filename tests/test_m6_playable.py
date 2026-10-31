"""M6: playable (SPEC-05 section 14, SPEC-06). Headless replay of
SPEC/scenario/walkthrough.json against walkthrough-reference-log.json and the
`expected` blocks, plus one curses-free render of the first frame.
API: SPEC-07 sections 2.10 and 2.11."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

import wl_support as W
from wl_support import call, check_eq, expect_error, fail

pytestmark = pytest.mark.milestone("M6")

SEED = 20261021
WT = W.load_json(W.SCENARIO / "walkthrough.json")
CP_NAMES = [c["name"] for c in WT["checkpoints"]]
ITEM_TYPE = {it["id"]: it["type_byte"] >> 3 for it in W.load_json(W.SCENARIO / "items.json")["items"]}
GLYPHS = '.:"=,so~^bTYH*O%#_;/+nhPp|w`XGK>'  # SPEC-06 section 2.3, tiles 0 to 31


def strip(e):
    return {k: v for k, v in e.items() if k != "seq"}


def full_run(runner, seed):
    return runner.run("walkthrough", {"seed": seed, "script": WT["script"]}, seed)[0]


def checkpoints(events) -> dict:
    return {e.get("name"): e.get("state") for e in events if e.get("type") == "checkpoint"}


def _cp(events, name, what):
    cps = checkpoints(events)
    if name not in cps or not isinstance(cps[name], dict):
        fail("%s: the engine log has no checkpoint %r" % (what, name))
    return cps[name]


# ---- the walkthrough, seed 20261021 ------------------------------------------

def test_walkthrough_wins(runner):
    ev = full_run(runner, SEED)
    st = _cp(ev, "CP10", "seed %d" % SEED)
    check_eq("mode at CP10, seed %d" % SEED, st.get("mode"), "won")
    win = [strip(e) for e in ev if e.get("type") == "win"]
    check_eq("win event, seed %d (LR-24, SPEC-06 6.2)" % SEED, win,
             [{"type": "win", "steps": 358, "day": 2, "minutes": 428}])


@pytest.mark.parametrize("name", CP_NAMES)
def test_checkpoint_matches_reference(runner, reference_log, name):
    ev = full_run(runner, SEED)
    want = checkpoints(reference_log)[name]
    check_eq("checkpoint %s, seed %d, full snapshot against the reference log" % (name, SEED),
             _cp(ev, name, "seed %d" % SEED), want)


def test_cp5_equals_pre_save(runner):
    ev = full_run(runner, SEED)
    check_eq("CP5 (after save and load) against CP5-pre-save, seed %d (LR-56)" % SEED,
             _cp(ev, "CP5", "seed %d" % SEED), _cp(ev, "CP5-pre-save", "seed %d" % SEED))


def _segments(events):
    out, cur = {}, []
    for e in events:
        cur.append(strip(e))
        if e.get("type") == "checkpoint":
            out[e.get("name")] = cur
            cur = []
    return out


@pytest.mark.parametrize("name", CP_NAMES)
def test_log_segment(runner, reference_log, name):
    ev = full_run(runner, SEED)
    got = _segments(ev)
    want = _segments(reference_log)[name]
    if name not in got:
        fail("log segment ending at %s: the engine log has no checkpoint %r" % (name, name))
    g = got[name]
    for i, (a, b) in enumerate(zip(g, want)):
        if a != b:
            fail("log segment ending at %s, event %d of the segment: expected %s, got %s"
                 % (name, i, W.short(b, 400), W.short(a, 400)))
    if len(g) != len(want):
        fail("log segment ending at %s: expected %d events, got %d" % (name, len(want), len(g)))


def test_full_log_equality(runner, reference_log):
    ev = full_run(runner, SEED)
    for i, (a, b) in enumerate(zip(ev, reference_log)):
        if a != b:
            fail("full event log, seed %d: event %d differs: expected %s, got %s"
                 % (SEED, i, W.short(b, 400), W.short(a, 400)))
    if len(ev) != len(reference_log):
        fail("full event log, seed %d: expected %d events, got %d" % (SEED, len(reference_log), len(ev)))


# ---- the walkthrough for other seeds: the expected blocks ---------------------

def _view(state):
    v = dict(state)
    party = []
    for m in state.get("party") or []:
        mm = dict(m)
        mm["items_excluding_ammo"] = sorted(i for i, _ in (m.get("items") or []) if ITEM_TYPE.get(i) != 3)
        party.append(mm)
    v["party"] = party
    return v


@pytest.mark.parametrize("seed", [SEED] + list(range(1, 21)))
def test_expected_blocks(runner, seed):
    ev = full_run(runner, seed)
    for cp in WT["checkpoints"]:
        st = _view(_cp(ev, cp["name"], "seed %d" % seed))
        exp = cp["expected"]
        top = {k: v for k, v in exp.items() if k != "party"}
        check_eq("seed %d checkpoint %s" % (seed, cp["name"]), {k: st.get(k, "<missing>") for k in top}, top)
        got_party = st.get("party") or []
        if len(got_party) != len(exp["party"]):
            fail("seed %d checkpoint %s: expected %d party members, got %d"
                 % (seed, cp["name"], len(exp["party"]), len(got_party)))
        for g, w in zip(got_party, exp["party"]):
            check_eq("seed %d checkpoint %s slot %d" % (seed, cp["name"], w["slot"]),
                     {k: g.get(k, "<missing>") for k in w}, w)
    check_eq("seed %d: CP5 equals CP5-pre-save (LR-56)" % seed, _cp(ev, "CP5", "seed %d" % seed),
             _cp(ev, "CP5-pre-save", "seed %d" % seed))


# ---- headless driver behaviour (SPEC-06 sections 3 to 5) ----------------------

def test_ignored_key(runner):
    ev, _ = runner.run("ignored", {"seed": SEED, "script": ["Z", {"checkpoint": "a"}]})
    got = [strip(e) for e in ev if e.get("type") in ("input", "ignored")]
    check_eq("an unlisted key in map mode (SPEC-06 section 4)", got,
             [{"type": "input", "key": "Z"}, {"type": "ignored", "key": "Z"}])


def test_look(runner):
    ev, _ = runner.run("look", {"seed": SEED, "script": ["L", "LEFT", {"checkpoint": "a"}]})
    got = [strip(e) for e in ev if e.get("type") == "look"]
    # Addendum 7 (2026-10-31): (14, 20) is tile 0 (sand, image 10) under the map file's [y][x]
    # convention; the frozen value 28 was the image of the party's own cell (15, 20).
    check_eq("look west from (15, 20) (SPEC-06 section 3)", got,
             [{"type": "look", "x": 14, "y": 20, "image": 10, "action_class": 0}])
    st = _cp(ev, "a", "look")
    check_eq("look takes no step and no time", [st.get("steps"), st.get("minute"), st.get("rng_state")], [0, 0, SEED])


def test_repeat_limit(compiled, tmp_path_factory):
    dd = compiled.copy(tmp_path_factory)
    expect_error("RepeatLimitError", "headless.run", str(dd),
                 {"seed": SEED, "script": [{"repeat_until": "cell:0,0,0", "keys": ["Z"], "max": 3}]}, None,
                 what="repeat_until never true (SPEC-06 5.1 exit code 2)")


def test_malformed_script(compiled, tmp_path_factory):
    dd = compiled.copy(tmp_path_factory)
    expect_error("ScriptError", "headless.run", str(dd), {"seed": SEED, "script": ["JUMP"]}, None,
                 what="token 'JUMP' (SPEC-06 5.1 exit code 4)")


def _cli(args, cwd):
    env = dict(os.environ, PYTHONPATH=str(W.SRC), PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-m", "wlengine"] + args, capture_output=True, text=True, cwd=str(cwd),
                          env=env, timeout=300, stdin=subprocess.DEVNULL)


def test_cli_headless(runner, compiled, tmp_path_factory):
    ev = full_run(runner, SEED)
    dd = compiled.copy(tmp_path_factory)
    out = tmp_path_factory.mktemp("cli")
    script = out / "script.json"
    script.write_text(json.dumps({"seed": 1, "script": WT["script"]}))
    log = out / "out.jsonl"
    r = _cli(["--headless", "--data", str(dd), "--script", str(script), "--seed", str(SEED), "--log", str(log)], out)
    check_eq("exit code of wl --headless on the walkthrough (SPEC-06 5.1)", r.returncode, 0)
    if not log.is_file():
        fail("wl --headless wrote no log file at --log")
    lines = log.read_text(encoding="utf-8").splitlines()
    bad = next((i for i, l in enumerate(lines) if l != l.rstrip()), None)
    if bad is not None:
        fail("log line %d has trailing spaces (SPEC-06 5.3)" % bad)
    try:
        got = [json.loads(l) for l in lines]
    except ValueError as e:
        fail("log is not JSON Lines: %s" % e)
    for i, (a, b) in enumerate(zip(got, ev)):
        if a != b:
            fail("CLI log event %d differs from headless.run: expected %s, got %s" % (i, W.short(b, 300), W.short(a, 300)))
    check_eq("CLI log length against headless.run", len(got), len(ev))


# ---- front end: first frame (SPEC-06 sections 2 and 7) ------------------------

def _frame(compiled):
    dd = compiled.need()
    fr = call("ui.render_frame", str(dd))
    if not (isinstance(fr, list) and len(fr) == 25 and all(isinstance(r, str) and len(r) == 80 for r in fr)):
        fail("ui.render_frame must return 25 strings of 80 characters, got %s" % W.short(
            [len(r) if isinstance(r, str) else type(r).__name__ for r in fr] if isinstance(fr, list) else fr))
    return fr


def test_render_frame_party(compiled):
    fr = _frame(compiled)
    check_eq("row 6 columns 18 to 20 of the first frame (SPEC-06 7)", fr[6][18:21], ".@.")
    check_eq("row 0 starts with the location name", fr[0][:8], "Saltwell")


def test_render_status_line(compiled):
    fr = _frame(compiled)
    check_eq("status line (SPEC-06 2.1)", fr[0].rstrip(), "Saltwell  Day 1  08:00  (15,20)  Steps 0  map")


def test_render_viewport(compiled):
    fr = _frame(compiled)
    m = W.load_json(W.SCENARIO / "map1-saltwell.json")
    border = GLYPHS[m["info"]["border_image"] - 10]
    want = []
    for j in range(11):
        row = ""
        for i in range(39):
            x, y = 15 - 19 + i, 20 - 5 + j
            if (i, j) == (19, 5):
                row += "@"
            elif 0 <= x < 32 and 0 <= y < 32:
                row += GLYPHS[m["tiles"][y][x]]
            else:
                row += border
        want.append(row)
    got = [fr[1 + j][0:39] for j in range(11)]
    for j, (g, w) in enumerate(zip(got, want)):
        if g != w:
            fail("map viewport row %d (screen row %d, columns 0 to 38): expected %r, got %r" % (j, j + 1, w, g))


def test_cli_render_frame(compiled, tmp_path_factory):
    dd = compiled.copy(tmp_path_factory)
    r = _cli(["--data", str(dd), "--render-frame"], dd)
    check_eq("exit code of wl --data DIR --render-frame (SPEC-06 7)", r.returncode, 0)
    lines = r.stdout.splitlines()
    check_eq("printed frame: 25 lines, row 0 starts with Saltwell, row 6 column 19 is @",
             [len(lines), lines[0][:8] if lines else None, lines[6][19:20] if len(lines) > 6 else None],
             [25, "Saltwell", "@"])
