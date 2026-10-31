"""probe356: render the JSON map1 as glyphs and diff it against the ASCII art
in SPEC-05 section 5.2, row by row, to find where they disagree.

Run: python3 tests/fixtures-generated/probe356.py
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

spec = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")).read()
# find the art block: lines that start with two spaces, a number, two spaces, '|'
lines = spec.splitlines()
art = {}
for ln in lines:
    m = re.match(r"^  (\d+)  \|(.*)\|$", ln)
    if m:
        art[int(m.group(1))] = m.group(2)
print("art rows found:", sorted(art)[:5], "...", len(art))

for y in sorted(art):
    row = art[y]
    got = "".join(GLYPHS[t[y][x]] for x in range(32))
    if got != row:
        # find first difference
        diff = [i for i in range(32) if got[i] != row[i]]
        print("row %2d differs at %s" % (y, diff))
        print("   art:", row)
        print("   json:", got)
        for i in diff:
            print("      x=%d art=%r json=%r (tile %d class %d)" % (i, row[i], got[i], t[y][x] if False else t[y][i], ac[y][i]))
