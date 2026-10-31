"""probe437: compare SPEC-05 Saltwell ASCII art with SPEC/scenario/map1-saltwell.json
and with the engine's compiled map.  Also introspect the scenario compile API."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

SPEC = Path("SPEC/SPEC-05-scenario.md").read_text(encoding="utf-8")
i = SPEC.index("### 5.2 Saltwell")
seg = SPEC[i:i + 3000]
rows = {}
for line in seg.split("\n"):
    m = re.match(r"^\s*(\d+)\s+(\S.*)$", line)
    if m:
        rows[int(m.group(1))] = m.group(2)

print("=== ASCII rows (len, content) ===")
for y in sorted(rows):
    print(y, len(rows[y]), repr(rows[y]))

print()
print("=== ASCII non-dot cells (string index) ===")
for y in sorted(rows):
    r = rows[y]
    cells = [(x, c) for x, c in enumerate(r) if c not in ".|"]
    if cells:
        print(y, cells)

d = json.loads(Path("SPEC/scenario/map1-saltwell.json").read_text(encoding="utf-8"))
tiles = d["tiles"]
ac = d["action_class"]
av = d["action_value"]
print()
print("=== JSON non-zero tiles (index) ===")
for y in range(len(tiles)):
    cells = [(x, v) for x, v in enumerate(tiles[y]) if v]
    if cells:
        print(y, cells)

print()
print("=== JSON non-zero action_class ===")
for y in range(len(ac)):
    cells = [(x, v) for x, v in enumerate(ac[y]) if v]
    if cells:
        print(y, cells)

print()
print("=== JSON action_cells ===")
for c in d["action_cells"]:
    print(c)

print()
print("=== engine scenario API ===")
import wlengine.scenario as sc  # noqa: E402
print([n for n in dir(sc) if not n.startswith("_")])
