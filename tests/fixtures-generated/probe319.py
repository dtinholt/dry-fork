"""Probe 319: compare the engine's loaded map with the scenario JSON, both ways.

Run: python3 tests/fixtures-generated/probe319.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wlengine.scenario as S  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")
j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))

print("json keys:", sorted(j.keys()))
print("width/height:", j.get("width"), j.get("height"))
print("tiles[20]:", j["tiles"][20])
print("tiles[14]:", j["tiles"][14])
print("tiles[3]:", j["tiles"][3])
print("tiles[2]:", j["tiles"][2])
print("col20 (tiles[x][20]):", [j["tiles"][x][20] for x in range(32)])
print("ac col20:", [j["action_class"][x][20] for x in range(32)])
print("ac row20:", j["action_class"][20])

# find a compiled data dir
cands = []
for base in (os.path.join(ROOT, "tests"), ROOT, "/tmp"):
    if os.path.isdir(base):
        for name in os.listdir(base):
            p = os.path.join(base, name)
            if os.path.isdir(p) and os.path.exists(os.path.join(p, "LABTABLES.BIN")):
                cands.append(p)
print("compiled candidates:", cands[:10])

if cands:
    dd = cands[0]
    sc = S.load(dd)
    m = sc.map(1)
    print("engine map keys:", sorted(m.keys()))
    cells = m["cells"]
    print("cells keys:", sorted(cells.keys()))
    img = cells["image"]
    print("engine image[20]:", img[20])
    print("engine image col20:", [img[y][20] for y in range(32)])
    print("engine ac[20]:", cells["actionClass"][20])
    print("engine ac col20:", [cells["actionClass"][y][20] for y in range(32)])
    print("engine size:", m["size"])
    print("engine info:", m["info"])
