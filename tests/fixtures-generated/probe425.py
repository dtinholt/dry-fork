"""Probe 425: compare SPEC/scenario/map1-saltwell.json with the compiled map."""
import os
import sys
import json
import tempfile
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

src = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
tiles = src["tiles"]
ac = src["action_class"]
av = src["action_value"]
print("tiles rows:", len(tiles), "cols:", len(tiles[0]))
for y in (4, 5, 11, 20, 21):
    print("json tiles y=%d:" % y, tiles[y])
    print("json aclass y=%d:" % y, ac[y])
    print("json avalue y=%d:" % y, av[y])

import wlengine.scenario as S

dd = os.path.join(ROOT, "tests", "fixtures-generated", "dd")
sc = S.load(dd)
m = sc.map(1)
cells = m["cells"]
for y in (4, 5, 11, 20, 21):
    print("compiled aclass y=%d:" % y, cells["actionClass"][y])
    print("compiled image  y=%d:" % y, cells["image"][y])

tmp = tempfile.mkdtemp()
try:
    S.compile(os.path.join(ROOT, "SPEC", "scenario"), tmp)
    sc2 = S.load(tmp)
    m2 = sc2.map(1)
    c2 = m2["cells"]
    for y in (4, 5, 11, 20, 21):
        print("FRESH aclass y=%d:" % y, c2["actionClass"][y])
        print("FRESH image  y=%d:" % y, c2["image"][y])
except Exception:
    traceback.print_exc()
