"""probe358: print art rows vs JSON rows for map1 with offsets, and the gate
row 31 in detail.

Run: python3 tests/fixtures-generated/probe358.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")
GLYPHS = '.:"=,so~^bTYH*O%#_;/+nhPp|w`XGK>'

d = json.load(open(os.path.join(SC, "map1-saltwell.json")))
t = d["tiles"]
ac = d["action_class"]

spec = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")).read().splitlines()
art = {}
for ln in spec:
    m = re.match(r"^\s*(\d+)\s+\|(.*)\|\s*$", ln)
    if m:
        art[int(m.group(1))] = m.group(2)

for y in (0, 20, 30, 31):
    print("row", y)
    print("   art      :", art.get(y))
    print("   json x0-31:", "".join(GLYPHS[t[y][x]] for x in range(32)))
    print("   json x1-30:", "".join(GLYPHS[t[y][x]] for x in range(1, 31)))
    print("   json x0-29:", "".join(GLYPHS[t[y][x]] for x in range(0, 30)))

print()
print("row 31 tiles:", [(x, t[31][x], ac[31][x]) for x in range(12, 20)])
print("row 30 tiles:", [(x, t[30][x], ac[30][x]) for x in range(12, 20)])
print("col 15 tiles:", [(y, t[y][15], ac[y][15]) for y in range(28, 32)])
print("col 16 tiles:", [(y, t[y][16], ac[y][16]) for y in range(28, 32)])
print("col 14 tiles:", [(y, t[y][14], ac[y][14]) for y in range(28, 32)])
