"""Probe 282: investigate M5 test_bump_is_not_a_step.

Dump the Saltwell map tiles around (2..5, 20) from:
  * SPEC/scenario/map1-saltwell.json (source of truth for the oracle)
  * the engine's compiled/decoded map (whatever the engine actually walks on)
and run the bump script through the engine to see the events.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SPEC = os.path.join(ROOT, "SPEC", "scenario")

with open(os.path.join(SPEC, "map1-saltwell.json")) as f:
    m = json.load(f)
print("map1 keys:", sorted(m.keys()))
tiles = m.get("tiles") or m.get("tile_map") or m.get("map")
print("tiles type:", type(tiles))
if isinstance(tiles, list):
    print("rows:", len(tiles), "cols:", len(tiles[0]) if tiles else 0)
    for y in range(18, 23):
        row = tiles[y]
        print("y=%d" % y, [(x, row[x]) for x in range(0, 8)])
elif isinstance(tiles, dict):
    print(json.dumps({k: v for k, v in tiles.items() if k in ("width", "height")}, indent=1))
    flat = tiles.get("data") or tiles.get("tiles")
    if isinstance(flat, list):
        w = tiles.get("width")
        for y in range(18, 23):
            print("y=%d" % y, [(x, flat[y * w + x]) for x in range(0, 8)])

# engine side
try:
    from wlengine import scenario as scen
    print("scenario module:", scen.__file__)
    print("scenario attrs:", [a for a in dir(scen) if not a.startswith("_")])
except Exception as e:
    print("scenario import failed:", e)

try:
    from wlengine import headless
    print("headless attrs:", [a for a in dir(headless) if not a.startswith("_")])
except Exception as e:
    print("headless import failed:", e)

# Run the bump script through the engine and print the tail events.
try:
    import wlengine.headless as H
    ev = H.run({"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    print("--- engine events (tail 8) ---")
    for e in ev[-8:]:
        print(e)
except Exception as e:
    import traceback
    traceback.print_exc()

# What does the oracle say?  Look at the reference log for a bump near (2,20).
try:
    with open(os.path.join(SPEC, "walkthrough-reference-log.json")) as f:
        ref = json.load(f)
    print("ref type:", type(ref))
except Exception as e:
    print("ref load failed:", e)
