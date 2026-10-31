"""Probe 267: reference log around seq 300-340 and engine equivalent.

Run: python3 tests/fixtures-generated/probe267.py
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
    for i in range(300, 340):
        print("REF", i, json.dumps(ref[i]))
    print("----")
    for e in ev:
        if 300 <= e["seq"] <= 340:
            print("ENG", json.dumps(e))


main()
