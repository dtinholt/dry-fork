"""Probe 399: print the scenario JSON action_class rows 19..21 and the engine's
compiled map rows, to see whether the cactus is at (2,20) or (3,20).

Run: python3 tests/fixtures-generated/probe399.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SCEN = os.path.join(ROOT, "SPEC", "scenario")
m = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
ac = m["action_class"]
av = m["action_value"]
tl = m["tiles"]
print("width/height:", m.get("width"), m.get("height"))
for y in (19, 20, 21):
    print("y=%d ac  :" % y, ac[y])
    print("y=%d av  :" % y, av[y])
    print("y=%d tile:" % y, tl[y])
print("action_cells:", json.dumps(m["action_cells"], indent=1))

print("=" * 70)
import wlengine.scenario as S  # noqa: E402
d = tempfile.mkdtemp(prefix="probe399-")
S.compile(SCEN, d)
sc = S.load(d)
mm = sc.map(1)
print("engine map keys:", sorted(mm.keys()))
print("engine size:", mm.get("size"))
for key in ("action_class", "action_value", "tiles"):
    v = mm.get(key)
    if v is None:
        continue
    print("engine", key, "type", type(v).__name__)
    if isinstance(v, list) and v and isinstance(v[0], list):
        for y in (19, 20, 21):
            print("  y=%d:" % y, v[y])
    elif isinstance(v, list):
        size = mm.get("size")
        if size:
            for y in (19, 20, 21):
                print("  y=%d:" % y, v[y * size:(y + 1) * size])
