"""Probe 277: dump engine vs reference events in a seq window, with combat state.

Usage: python3 tests/fixtures-generated/probe277.py [lo] [hi]

Prints, for each seq in the window, the reference event and (when it differs)
the engine event.  Also prints the engine's combat band/groups state whenever a
combat event is emitted, so the band bookkeeping can be checked against the
reference's ``group_closes`` / ``advance`` events.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402

SEED = 20261021


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 700
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]
    wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    by = {e.get("seq"): e for e in ev}
    for i in range(lo, hi + 1):
        a = by.get(i)
        b = ref[i] if i < len(ref) else None
        mark = "  " if a == b else "!!"
        print("%s %4d ref=%s" % (mark, i, json.dumps(b)[:220]))
        if a != b:
            print("        eng=%s" % json.dumps(a)[:220])


def dump_bands(lo, hi):
    """Print the engine's combat band bookkeeping for the window."""
    ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]
    wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    for e in ev:
        s = e.get("seq")
        if s is None or not (lo <= s <= hi):
            continue
        if e.get("type") in ("round_orders", "round_start", "group_closes", "advance",
                             "attack", "monster_dies", "combat_end", "reload", "jam",
                             "unjam", "click"):
            print("eng %4d %s" % (s, json.dumps(e)[:200]))
        r = ref[s] if s < len(ref) else None
        if r is not None and r.get("type") in ("round_orders", "round_start",
                                               "group_closes", "advance", "attack",
                                               "monster_dies", "combat_end"):
            print("ref %4d %s" % (s, json.dumps(r)[:200]))


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[3] == "bands":
        dump_bands(int(sys.argv[1]), int(sys.argv[2]))
    else:
        main()
