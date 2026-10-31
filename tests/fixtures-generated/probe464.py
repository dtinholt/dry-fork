"""probe464: inspect the engine's compiled Saltwell map around the cells the
two failing tests care about, and compare with the JSON.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from wlengine import maps, scenario  # noqa: E402

SCEN = ROOT / "SPEC" / "scenario"

d = tempfile.mkdtemp(prefix="probe464-")
scenario.compile(str(SCEN), d)
m = maps.load_map(d, 1)
print("map keys:", sorted(m.keys()))
print("size:", m.get("size"), "width", m.get("width"), "height", m.get("height"))
print("tiles type:", type(m.get("tiles")), "len", len(m.get("tiles") or []))
for y in (19, 20, 21):
    row = []
    for x in range(0, 8):
        row.append((x, maps.image_at(m, x, y), m["actionClass"][y][x] if "actionClass" in m else None))
    print("y=%d x0..7:" % y, row)
    row = []
    for x in range(12, 18):
        row.append((x, maps.image_at(m, x, y), m["actionClass"][y][x] if "actionClass" in m else None))
    print("y=%d x12..17:" % y, row)
print("row 11:", [(x, maps.image_at(m, x, 11), m["actionClass"][11][x]) for x in range(12, 18)])
print("row 31:", [(x, maps.image_at(m, x, 31), m["actionClass"][31][x]) for x in range(13, 19)])
print("row 12:", [(x, maps.image_at(m, x, 12), m["actionClass"][12][x]) for x in range(11, 19)])

j = json.loads((SCEN / "map1-saltwell.json").read_text())
print()
print("JSON row 20 tiles:", j["tiles"][20])
print("JSON row 20 class:", j["action_class"][20])
print("JSON row 11 tiles:", j["tiles"][11])
print("JSON row 11 class:", j["action_class"][11])
print("JSON row 31 tiles:", j["tiles"][31])
print("JSON row 31 class:", j["action_class"][31])
print("JSON row 12 tiles:", j["tiles"][12])
print("JSON row 12 class:", j["action_class"][12])
print("JSON action_cells:", json.dumps(j["action_cells"])[:2000])
