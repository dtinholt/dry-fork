"""Probe 323: search the JSON map for image 28 cells; check other look tests.

Run: python3 tests/fixtures-generated/probe323.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCEN = os.path.join(ROOT, "SPEC", "scenario")
j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
tiles = j["tiles"]
ac = j["action_class"]

print("cells with tile 18 (image 28):")
for y in range(32):
    for x in range(32):
        if tiles[y][x] == 18:
            print("   tiles[y][x] ->", (x, y), "ac", ac[y][x])
print("cells with tiles[x][y] == 18 (transposed):")
for x in range(32):
    for y in range(32):
        if tiles[x][y] == 18:
            print("   tiles[x][y] ->", (x, y), "ac", ac[x][y])

print()
print("tiles[15] =", tiles[15])
print("tiles[19] =", tiles[19])
print("tiles[20] =", tiles[20])
print("tiles[21] =", tiles[21])
print("tiles[14] =", tiles[14])
print("tiles[16] =", tiles[16])

# other look tests
import subprocess  # noqa: E402

r = subprocess.run(["grep", "-rn", "look", os.path.join(ROOT, "tests")], capture_output=True, text=True)
print(r.stdout[:6000])
