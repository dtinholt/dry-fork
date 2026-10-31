"""Probe 264: reference log around seq 275-300 (the (0,31,41) cell change).

Run: python3 tests/fixtures-generated/probe264.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json"


def main():
    log = json.load(open(REF))["events"]
    for i in range(270, 300):
        print(i, json.dumps(log[i]))


main()
