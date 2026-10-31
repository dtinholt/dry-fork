"""Probe 269: reference log around class-4 cell changes (seq 515-545, 805-855).

Run: python3 tests/fixtures-generated/probe269.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json"


def main():
    log = json.load(open(REF))["events"]
    for lo, hi in ((515, 545), (805, 855)):
        print("=== %d..%d" % (lo, hi))
        for i in range(lo, hi):
            print(i, json.dumps(log[i]))


main()
