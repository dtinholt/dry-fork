"""Probe 328: which map/array has image 28 (tile 18, street) at (14,20)?

`test_look` expects `look` west from (15,20) to report image 28 at (14,20).
Print, for every scenario map, the tile at (14,20), (20,14), (15,20), (15,19)
and the transposed variants, to see where 18 lives.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SCEN = os.path.join(PROJ, "SPEC", "scenario")

for name in ("map0-overworld.json", "map1-saltwell.json", "map2-ninemile.json",
             "map3-pumphouse.json"):
    j = json.load(open(os.path.join(SCEN, name)))
    t = j["tiles"]
    ac = j["action_class"]
    print("==", name, "location", j["location"], "size", j["width"], j["height"])
    for (x, y) in ((14, 20), (20, 14), (15, 20), (15, 19), (15, 21), (13, 20)):
        print("   tiles[%d][%d]=%d  tiles[%d][%d]=%d  ac[%d][%d]=%d ac[%d][%d]=%d"
              % (y, x, t[y][x], x, y, t[x][y], y, x, ac[y][x], x, y, ac[x][y]))
    print("   tile 18 positions:", [(x, y) for y in range(len(t)) for x in range(len(t[y])) if t[y][x] == 18][:12])
    print()
