"""probe466: dump JSON rows 11, 20, 31 and the ASCII interior indices, to see
exactly where the frozen JSON puts the pump, the gate, the road and the cactus.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"
m = json.loads((SCEN / "map1-saltwell.json").read_text())

for y in (11, 20, 31, 12, 30):
    print("row %d tiles:" % y, m["tiles"][y])
    print("row %d class:" % y, m["action_class"][y])
    print("row %d value:" % y, m["action_value"][y])
    print()

print("action_cells:")
for c in m["action_cells"]:
    print(" ", c)
