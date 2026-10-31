"""probe468: dump tiles.json, map1 tiles rows, SPEC-06 glyph table, SPEC-05 saltwell ascii.

Also: compare the frozen SPEC-05 ASCII art of Saltwell against the frozen
map1-saltwell.json arrays column by column, and print the engine's own view of
the map (via wlengine.scenario compile) so we can see where the road column
lands.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")
sys.path.insert(0, os.path.join(ROOT, "src"))

tiles = json.load(open(os.path.join(SPEC, "scenario", "tiles.json")))
print("=== tiles.json keys:", list(tiles.keys()))
tl = tiles.get("tiles", tiles)
for t in tl:
    print("tile", t)

m1 = json.load(open(os.path.join(SPEC, "scenario", "map1-saltwell.json")))
print("=== map1 keys:", list(m1.keys()))
print("width", m1.get("width"), "height", m1.get("height"), "tileset", m1.get("tileset"))
tiles_arr = m1["tiles"]
print("=== tiles rows 19..21 (len %d)" % len(tiles_arr))
for y in (19, 20, 21):
    print(y, tiles_arr[y])
print("=== action_class rows 19..21")
for y in (19, 20, 21):
    print(y, m1["action_class"][y])
print("=== action_value rows 19..21")
for y in (19, 20, 21):
    print(y, m1["action_value"][y])
print("=== action_cells")
print(json.dumps(m1["action_cells"], indent=1)[:3000])

# SPEC-06 glyph table
txt = open(os.path.join(SPEC, "SPEC-06-ui.md")).read()
i = txt.find("2.3")
print("=== SPEC-06 2.3 excerpt ===")
print(txt[i:i + 2500])

# SPEC-05 saltwell ascii
s5 = open(os.path.join(SPEC, "SPEC-05-scenario.md")).read()
j = s5.find("### 5.2 Saltwell")
k = s5.find("### 5.3", j)
block = s5[j:k]
print("=== SPEC-05 5.2 block (first 3000) ===")
print(block[:3000])

# parse the ascii art rows
rows = {}
for line in block.splitlines():
    mm = re.match(r"^\s*(\d+)\s+(.*)$", line)
    if mm:
        y = int(mm.group(1))
        rows[y] = mm.group(2)
print("=== parsed ascii rows:", sorted(rows.keys()))
for y in sorted(rows):
    print(y, repr(rows[y]))

# compare ascii vs json tiles: ascii char -> tile id via tiles.json glyphs
glyph = {}
for t in tl:
    g = t.get("glyph")
    if g:
        glyph[g] = t["id"]
print("=== glyph map:", glyph)

print("=== column diff ascii vs json (tile ids) ===")
for y in sorted(rows):
    art = rows[y]
    jrow = tiles_arr[y]
    diffs = []
    for x, ch in enumerate(art):
        want = glyph.get(ch)
        got = jrow[x] if x < len(jrow) else None
        if want is not None and want != got:
            diffs.append((x, ch, want, got))
    if diffs:
        print("row", y, diffs)
