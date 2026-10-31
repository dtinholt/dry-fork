"""Probe 254: run the raider fight (walkthrough to CP4) for seed 3 and dump
combat events; also run the reference consistency checker and print issues.

Run: python3 tests/fixtures-generated/probe254.py
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
import wl_combat_ref as CR  # noqa: E402

d = Path(tempfile.mkdtemp())
sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))

wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
script = []
for item in wt["script"]:
    script.append(item)
    if isinstance(item, dict) and item.get("checkpoint") == "CP4":
        break

for seed in (3,):
    ev = hl.run(str(d), {"seed": seed, "script": script}, seed)
    print("=== seed", seed, "issues ===")
    for c, m in CR.consistency(ev):
        print(" ", c, m)
    print("=== combat events ===")
    started = False
    for e in ev:
        if e.get("type") == "encounter_start":
            started = True
        if started:
            print(json.dumps(e))
        if e.get("type") == "combat_end":
            break
