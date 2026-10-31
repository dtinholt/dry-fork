"""probe357: extract the SPEC-05 5.2 ASCII art properly and compare with the
JSON map, trying the offset that makes them agree.

Run: python3 tests/fixtures-generated/probe357.py
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
print("rows:", len(art), "widths:", sorted({len(v) for v in art.values()}))

for y in sorted(art):
    row = art[y]
    got = "".join(GLYPHS[t[y][x]] for x in range(32))
    if got != row:
        print("row %2d len(art)=%d" % (y, len(row)))
        print("   art :", row)
        print("   json:", got)
        break

# try offset 1 (art index i = x - 1)
ok = 0
bad = []
for y in sorted(art):
    row = art[y]
    got = "".join(GLYPHS[t[y][x]] for x in range(1, 31))
    if got == row:
        ok += 1
    else:
        bad.append(y)
print("offset 1: rows matching", ok, "of", len(art), "bad", bad[:10])
for y in bad[:3]:
    print("  row", y)
    print("   art :", art[y])
    print("   json:", "".join(GLYPHS[t[y][x]] for x in range(1, 31)))
