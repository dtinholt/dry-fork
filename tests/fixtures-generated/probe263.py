"""Probe 263: reference log around CP5-pre-save.

Run: python3 tests/fixtures-generated/probe263.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

REF = ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json"


def main():
    log = json.load(open(REF))["events"]
    print("type", type(log), "len", len(log))
    # find checkpoints
    cps = [e for e in log if e.get("type") == "checkpoint"]
    print("checkpoints:", [c["name"] for c in cps])
    for c in cps:
        if c["name"] in ("CP4", "CP5-pre-save", "CP5"):
            print("=== ", c["name"])
            print(json.dumps(c["state"].get("cell_changes")))
    # find index of CP5-pre-save
    idx = None
    for i, e in enumerate(log):
        if e.get("type") == "checkpoint" and e.get("name") == "CP5-pre-save":
            idx = i
    print("CP5-pre-save at index", idx)
    lo = max(0, idx - 40)
    for i in range(lo, min(len(log), idx + 6)):
        print(i, json.dumps(log[i]))
    print("=== all cell_change events in reference ===")
    for i, e in enumerate(log):
        if e.get("type") == "cell_change":
            print(i, json.dumps(e))


main()
