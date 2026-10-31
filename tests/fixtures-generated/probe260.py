"""Probe 260: print the reference log's raider fight orders/reload/jam events
and the engine's, plus the reference log's full fight event list after the
first unjammed.

Run: python3 tests/fixtures-generated/probe260.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402


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
    print("=== reference fight, all events ===")
    for e in rf:
        print(json.dumps(e))


main()
