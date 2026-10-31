"""Probe 141: compile the scenario, run the bump test, dump the map cells.

Run from the project root:  python3 tests/fixtures-generated/probe141.py
"""
import os
import sys
import json
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TESTS = os.path.join(ROOT, "tests")
for p in (ROOT, os.path.join(ROOT, "src"), TESTS, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from wlengine import scenario as sc_mod
from wlengine import headless as hl
from wlengine import maps as maps_mod

SCEN = os.path.join(ROOT, "SPEC", "scenario")
SEED = 19880101

dd = tempfile.mkdtemp(prefix="probe141-")
print("compiling to", dd)
try:
    sc_mod.compile(SCEN, dd)
except Exception:
    traceback.print_exc()
    sys.exit(1)
print("compiled:", sorted(os.listdir(dd)))

ev = hl.run(dd, {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
print("== events ==")
for e in ev:
    print("  ", json.dumps(e, sort_keys=True))

print("== map 1 cells around (2,20) ==")
sc = sc_mod.Scenario(dd)
m = sc.map(1)
print("size", m["size"])
for y in range(18, 23):
    row = []
    for x in range(0, 8):
        cls = m["cells"]["actionClass"][y][x]
        act = m["cells"]["action"][y][x]
        img = m["cells"]["image"][y][x]
        row.append("%d:%d/%d/%d" % (x, cls, act, img))
    print("  y=%d  %s" % (y, "  ".join(row)))
print("passable(2,20) =", maps_mod.is_passable(m, 2, 20))
print("record_at(2,20) =", maps_mod.record_at(m, 2, 20))
print("passable(3,20) =", maps_mod.is_passable(m, 3, 20))
print("record_at(3,20) =", maps_mod.record_at(m, 3, 20))
print("passable(4,20) =", maps_mod.is_passable(m, 4, 20))
print("record_at(4,20) =", maps_mod.record_at(m, 4, 20))
