"""Probe 324: which map has image 28 at (14,20)? Dump all maps' neighbourhoods.

Run: python3 tests/fixtures-generated/probe324.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCEN = os.path.join(ROOT, "SPEC", "scenario")

for name in sorted(os.listdir(SCEN)):
    if not name.startswith("map") or not name.endswith(".json"):
        continue
    j = json.load(open(os.path.join(SCEN, name)))
    tiles = j["tiles"]
    ac = j["action_class"]
    loc = j.get("location")
    print("==", name, "location", loc, "size", j.get("width"), j.get("height"))
    print("   tiles[20][14] =", tiles[20][14], "ac", ac[20][14])
    print("   tiles[14][20] =", tiles[14][20], "ac", ac[14][20])
    print("   tiles[20][15] =", tiles[20][15], "ac", ac[20][15])
    print("   tiles[19][15] =", tiles[19][15], "ac", ac[19][15])
    print("   tiles[15][20] =", tiles[15][20], "ac", ac[15][20])
    # any cell with tile 18 at (14,20)?
    print("   row20:", tiles[20])
    print("   row19:", tiles[19])
