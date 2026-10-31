"""Probe 424: compare SPEC/scenario/map1-saltwell.json with the compiled map."""
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

src = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
print("json keys:", sorted(src.keys()))
tiles = src["tiles"]
ac = src["action_class"]
act = src["action"]
print("tiles rows:", len(tiles), "cols:", len(tiles[0]))
for y in (4, 5, 11, 20, 21):
    print("json tiles y=%d:" % y, tiles[y])
    print("json aclass y=%d:" % y, ac[y])
    print("json action y=%d:" % y, act[y])

import wlengine.scenario as S
import wlengine.maps as M

dd = os.path.join(ROOT, "tests", "fixtures-generated", "dd")
sc = S.load(dd)
m = sc.map(1)
cells = m["cells"]
for y in (4, 5, 11, 20, 21):
    print("compiled aclass y=%d:" % y, cells["actionClass"][y])
    print("compiled image  y=%d:" % y, cells["image"][y])

# fresh compile
import tempfile
tmp = tempfile.mkdtemp()
try:
    S.compile(os.path.join(ROOT, "SPEC", "scenario"), tmp)
    sc2 = S.load(tmp)
    m2 = sc2.map(1)
    c2 = m2["cells"]
    print("FRESH compiled aclass y=20:", c2["actionClass"][20])
    print("FRESH compiled image  y=20:", c2["image"][20])
    print("FRESH compiled aclass y=5:", c2["actionClass"][5])
    print("FRESH compiled image  y=5:", c2["image"][5])
    print("FRESH compiled aclass y=11:", c2["actionClass"][11])
except Exception as e:
    import traceback
    traceback.print_exc()
