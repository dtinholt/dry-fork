"""Probe 250: locate compiled scenario data, dump map1 cells near (2..6, 20),
and dump the party start position; also dump LABSTATE-related state.

Run: python3 tests/fixtures-generated/probe250.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))


def find(name_parts, roots):
    hits = []
    for r in roots:
        if not r.exists():
            continue
        for p in r.rglob("*"):
            if p.is_file() and all(np in p.name.lower() for np in name_parts):
                hits.append(p)
    return hits


roots = [ROOT / "SPEC", ROOT / "tests", ROOT / "src", ROOT / "build", ROOT / "out"]
print("=== candidate saltwell/map json files ===")
for p in find(["saltwell"], roots)[:20]:
    print(" ", p.relative_to(ROOT), p.stat().st_size)
for p in find(["map1"], roots)[:20]:
    print(" ", p.relative_to(ROOT), p.stat().st_size)

print("=== top-level dirs ===")
for p in sorted(ROOT.iterdir()):
    print(" ", p.name, "dir" if p.is_dir() else "file")

print("=== tests/fixtures-generated/dd listing ===")
dd = ROOT / "tests" / "fixtures-generated" / "dd"
if dd.exists():
    for p in sorted(dd.iterdir()):
        print(" ", p.name, p.stat().st_size)

# Try to load the compiled scenario via wlengine.scenario
try:
    import wlengine.scenario as sc
    print("=== wlengine.scenario attrs ===")
    print([a for a in dir(sc) if not a.startswith("_")])
except Exception as e:  # noqa: BLE001
    print("scenario import failed:", e)

# Try the test support module for the scenario path
try:
    import wl_support as W
    print("=== wl_support paths ===")
    for a in dir(W):
        if a.isupper():
            print(" ", a, getattr(W, a))
except Exception as e:  # noqa: BLE001
    print("wl_support import failed:", e)
