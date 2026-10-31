"""probe467: dump tiles.json, map1 tiles rows, SPEC-06 glyph table, SPEC-05 saltwell ascii."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")

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
