"""probe355: brute force which cell yields image 28 / class 0 near (15,20) in
map1 under the normal and transposed readings.

Run: python3 tests/fixtures-generated/probe355.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")
d = json.load(open(os.path.join(SC, "map1-saltwell.json")))
t = d["tiles"]
ac = d["action_class"]
av = d["action_value"]
W = d["width"]
H = d["height"]

print("rows 14,15,19,20,21 (JSON, index = x):")
for y in (14, 15, 19, 20, 21):
    print("  y=%2d" % y, t[y])

print()
print("cells with tile 18 (image 28):")
for y in range(H):
    for x in range(W):
        if t[y][x] == 18:
            print("   normal (x=%d,y=%d) class=%s action=%s" % (x, y, ac[y][x], av[y][x]))

print()
print("neighbours of (15,20) in the normal reading:")
for (dx, dy, nm) in [(0, -1, "N"), (0, 1, "S"), (-1, 0, "W"), (1, 0, "E")]:
    x, y = 15 + dx, 20 + dy
    print("   %s (x=%d,y=%d) tile=%s class=%s action=%s" % (nm, x, y, t[y][x], ac[y][x], av[y][x]))

print()
print("neighbours of (15,20) in the transposed reading (array[x][y]):")
for (dx, dy, nm) in [(0, -1, "N"), (0, 1, "S"), (-1, 0, "W"), (1, 0, "E")]:
    x, y = 15 + dx, 20 + dy
    print("   %s (x=%d,y=%d) tile=%s class=%s action=%s" % (nm, x, y, t[x][y], ac[x][y], av[x][y]))

print()
print("party start cell (15,20): normal tile=%s class=%s ; transposed tile=%s class=%s"
      % (t[20][15], ac[20][15], t[15][20], ac[15][20]))
