"""Probe 327: is the M6 `look` expectation consistent with a transposed map?

`test_look` expects `look` west from (15,20) to report `x=14, y=20, image=28,
action_class=0`.  The engine's decoded map has image[20][14] == 10 (sand).
Print the engine's image array both ways round, and the JSON tiles array both
ways round, to see which indexing yields 28 at (14,20).
"""

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(PROJ, "src")
SCEN = os.path.join(PROJ, "SPEC", "scenario")
sys.path.insert(0, SRC)

from wlengine import scenario as scen_mod  # noqa: E402

d = tempfile.mkdtemp(prefix="probe327-")
scen_mod.compile(SCEN, d)
sc = scen_mod.load(d)
m = sc.map(1)
img = m["cells"]["image"]
ac = m["cells"]["actionClass"]
j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
tiles = j["tiles"]
jac = j["action_class"]

print("engine image[20][14] =", img[20][14], " image[14][20] =", img[14][20])
print("engine image[20][15] =", img[20][15], " image[15][20] =", img[15][20])
print("engine ac[20][14]    =", ac[20][14], " ac[14][20]    =", ac[14][20])
print("json tiles[20][14]   =", tiles[20][14], " tiles[14][20]   =", tiles[14][20])
print("json tiles[20][15]   =", tiles[20][15], " tiles[15][20]   =", tiles[15][20])
print("json ac[20][14]      =", jac[20][14], " ac[14][20]      =", jac[14][20])
print()
print("engine image row 20 :", img[20])
print("engine image col 20 :", [img[y][20] for y in range(32)])
print("json tiles row 20   :", tiles[20])
print("json tiles col 20   :", [tiles[y][20] for y in range(32)])
print()
# where does image 28 appear in row 20 and column 20?
print("image 28 in row 20 at x =", [x for x in range(32) if img[20][x] == 28])
print("image 28 in col 20 at y =", [y for y in range(32) if img[y][20] == 28])
print()
# the M5 bump case: (2,20) and (3,20)
print("M5: ac[20][2] =", ac[20][2], "ac[20][3] =", ac[20][3])
print("M5: ac[2][20] =", ac[2][20], "ac[3][20] =", ac[3][20])
print("M5: img[20][2] =", img[20][2], "img[20][3] =", img[20][3])
print("M5: img[2][20] =", img[2][20], "img[3][20] =", img[3][20])
print()
print("is the map symmetric? tiles[y][x] == tiles[x][y] for all:",
      all(tiles[y][x] == tiles[x][y] for y in range(32) for x in range(32)))
print("action_class symmetric:",
      all(jac[y][x] == jac[x][y] for y in range(32) for x in range(32)))
