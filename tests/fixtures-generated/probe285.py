"""Probe 285: dump map1 JSON conventions + tiles, and the compiled map tiles."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SPEC = os.path.join(ROOT, "SPEC", "scenario")

m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
print("conventions:", json.dumps(m["conventions"], indent=1))
print("tileset:", m["tileset"])
print("action_cells:", json.dumps(m["action_cells"])[:2000])
print("action_class:", json.dumps(m["action_class"])[:500])
print("action_value:", json.dumps(m["action_value"])[:500])

# tiles.json legend
t = json.load(open(os.path.join(SPEC, "tiles.json")))
print("tiles.json keys:", sorted(t.keys()))
print(json.dumps(t, indent=1)[:2500])
