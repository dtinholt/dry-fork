"""Probe 343: print column 20 and row 20 of map1 in both index orders, plus the
transposed walk west from (15,20) under several interpretations.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"
m = json.loads((SCEN / "map1-saltwell.json").read_text())
t = m["tiles"]
ac = m["action_class"]

print("tiles[y][20] for y=0..31 (column 20):")
print([t[y][20] for y in range(32)])
print("ac[y][20]:")
print([ac[y][20] for y in range(32)])
print("tiles[20][x] for x=0..31 (row 20):")
print(t[20])
print("ac[20][x]:")
print(ac[20])

print()
print("transposed walk west from (15,20): cell(x,y) = tiles[x][y]")
for x in range(15, 0, -1):
    print("  x=%2d tiles[x][20]=%3d ac=%2d" % (x, t[x][20], ac[x][20]))

print()
print("normal walk west from (15,20): cell(x,y) = tiles[y][x]")
for x in range(15, 0, -1):
    print("  x=%2d tiles[20][x]=%3d ac=%2d" % (x, t[20][x], ac[20][x]))

print()
print("transposed walk west from (15,20) with y as first index: cell(x,y)=tiles[y][x] but x,y swapped in report")
for y in range(20, 0, -1):
    print("  y=%2d tiles[15][y]=%3d ac=%2d" % (y, t[15][y], ac[15][y]))
