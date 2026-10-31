"""Probe 397: inspect Saltwell (map1) tiles around (15,20) and (2..4,20) from the
scenario JSON, and run the engine's headless.run for the 'bump' script to see
where it stops.

Run: python3 tests/fixtures-generated/probe397.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SCEN = os.path.join(ROOT, "SPEC", "scenario")

m = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
print("map1 keys:", sorted(m.keys()))
print("size:", m.get("size"))
for k in sorted(m.keys()):
    v = m[k]
    if isinstance(v, list) and len(v) > 40:
        print("  %s: list len %d, head %r" % (k, len(v), v[:8]))
    elif isinstance(v, dict):
        print("  %s: dict keys %r" % (k, list(v)[:12]))
    else:
        print("  %s: %r" % (k, v))

tiles = m.get("tiles") or m.get("tile_map") or m.get("cells")
if tiles is None:
    for k, v in m.items():
        if isinstance(v, list) and len(v) == m.get("size", 0) ** 2:
            tiles = v
            print("using", k, "as tiles")
            break
if tiles is not None:
    size = m["size"]
    def at(x, y):
        return tiles[y * size + x]
    print("row y=20, x=0..16:", [at(x, 20) for x in range(0, 17)])
    print("row y=19, x=0..16:", [at(x, 19) for x in range(0, 17)])
    print("row y=21, x=0..16:", [at(x, 21) for x in range(0, 17)])

print("=" * 70)
print("### tiles.json")
print("=" * 70)
tj = json.load(open(os.path.join(SCEN, "tiles.json")))
print(json.dumps(tj)[:3000])
