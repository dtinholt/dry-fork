"""Probe: neighbourhood of (15,20) in map1, both orientations, and where image 28 is."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "..", "SPEC", "scenario")
m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
t = m["tiles"]
c = m["action_class"]
print("non-transposed tiles[y][x]:")
for y in range(18, 23):
    print(y, [(x, t[y][x], c[y][x]) for x in range(12, 19)])
print()
print("transposed tiles[x][y]:")
for x in range(12, 19):
    print(x, [(y, t[x][y], c[x][y]) for y in range(18, 23)])
print()
print("cells with image 28 (tile 18):")
for y in range(32):
    for x in range(32):
        if t[y][x] == 18:
            print("  (x=%d,y=%d) cls=%d" % (x, y, c[y][x]))
