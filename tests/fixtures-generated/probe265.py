"""Probe 265: engine log around the move to (31,41) vs reference.

Run: python3 tests/fixtures-generated/probe265.py
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

SEED = 20261021


def main():
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP5-pre-save":
            break
    ev = hl.run(str(d), {"seed": SEED, "script": script}, SEED)
    ref = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json"))["events"]
    # print engine events 280..300
    for e in ev:
        if 280 <= e["seq"] <= 300:
            print("ENG", json.dumps(e))
    print("---- ref")
    for e in ref:
        if 280 <= e["seq"] <= 300:
            print("REF", json.dumps(e))
    # first difference overall
    for i, (a, b) in enumerate(zip(ev, ref)):
        if a != b:
            print("first diff at index", i)
            print("ENG", json.dumps(a))
            print("REF", json.dumps(b))
            break
    else:
        print("no diff in zip; lens", len(ev), len(ref))


main()
