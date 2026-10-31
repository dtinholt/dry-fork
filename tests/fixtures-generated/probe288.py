"""Probe 288: compare the SPEC-05 5.2 ASCII art with the JSON tile map row by
row, and check the reference log's bump cells against the JSON."""
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
art = {}
for l in lines[start:end]:
    m2 = re.match(r"^\s{2}(\d+)\s{2}(.*)$", l)
    if m2:
        art[int(m2.group(1))] = m2.group(2)

m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
tiles = m["tiles"]
cls = m["action_class"]

GLYPH = {"|": 25, ".": 0, ";": 18, "Y": 11, "T": 10, "b": 9, "w": 26, "p": 24, "P": 23,
         "#": 16, "_": 27, "/": 19, "n": 22, "h": 22}

print("row | art vs json tiles (mismatch columns)")
for y in sorted(art):
    row = art[y]
    bad = []
    for x in range(32):
        g = row[x]
        want = GLYPH.get(g)
        got = tiles[y][x]
        if want is None:
            bad.append((x, g, "unknown glyph", got))
        elif want != got:
            bad.append((x, g, want, got))
    if bad:
        print("y=%2d %s" % (y, bad))

print()
print("json tiles rows 20,21,25:", tiles[20], tiles[21], tiles[25])
print("json class rows 20,21,25:", cls[20], cls[21], cls[25])

ref = json.load(open(os.path.join(SPEC, "walkthrough-reference-log.json")))["events"]
print()
print("--- reference log around each bump ---")
for i, e in enumerate(ref):
    if e.get("type") == "bump":
        print("seq", e["seq"], e)
        for j in range(max(0, i - 3), min(len(ref), i + 3)):
            print("   ", ref[j])
