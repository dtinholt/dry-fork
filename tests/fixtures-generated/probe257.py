"""Probe 257: print the reference log's raider fight (encounter_start to
combat_end) in full, and the engine's, so the two can be diffed.

Run: python3 tests/fixtures-generated/probe257.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402
import wl_support as W  # noqa: E402

SEED = 20261021


def fight(events):
    out = []
    started = False
    for e in events:
        if e.get("type") == "encounter_start":
            started = True
        if started:
            out.append(e)
        if e.get("type") == "combat_end":
            break
    return out


def main():
    ref = W.load_json(W.SCENARIO / "walkthrough-reference-log.json")["events"]
    rf = fight(ref)
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    ef = fight(ev)
    print("ref fight events:", len(rf), "engine fight events:", len(ef))
    for i in range(max(len(rf), len(ef))):
        a = json.dumps(rf[i]) if i < len(rf) else "<none>"
        b = json.dumps(ef[i]) if i < len(ef) else "<none>"
        mark = "  " if a == b else "!!"
        print("%s %3d ref %s" % (mark, i, a))
        if a != b:
            print("      eng %s" % b)


main()
