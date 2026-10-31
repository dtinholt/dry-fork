"""Probe 289: raw SPEC-05 5.2 art lines (repr) and a full art-vs-JSON compare."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC", "scenario")
SPECMD = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")

lines = open(SPECMD).read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("### 5.2 Saltwell"))
end = next(i for i, l in enumerate(lines) if i > start and l.startswith("### 5.3"))
for i in range(start, min(end, start + 45)):
    print(i, repr(lines[i]))

art = {}
for l in lines[start:end]:
    m2 = re.match(r"^\s*(\d+)\s\s(.*)$", l)
    if m2:
        art[int(m2.group(1))] = m2.group(2)
print("art rows found:", len(art))

m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
tiles = m["tiles"]
GLYPH = {"|": 25, ".": 0, ";": 18, "Y": 11, "T": 10, "b": 9, "w": 26, "p": 24, "P": 23,
         "#": 16, "_": 17, "/": 19, "n": 21, "h": 22}
for y in sorted(art):
    row = art[y]
    bad = [(x, row[x], GLYPH.get(row[x]), tiles[y][x]) for x in range(min(32, len(row)))
           if GLYPH.get(row[x]) != tiles[y][x]]
    print("y=%2d len=%2d mismatches=%s" % (y, len(row), bad))
