"""Probe 286: parse the SPEC-05 5.2 ASCII art and compare with map1 JSON tiles;
also ask the oracle tool for its expected map cells."""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SPEC = os.path.join(ROOT, "SPEC", "scenario")
SPECMD = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")

# --- parse the ASCII art of section 5.2 ------------------------------------
lines = open(SPECMD).read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("### 5.2 Saltwell"))
end = next(i for i, l in enumerate(lines) if i > start and l.startswith("### 5.3"))
art = []
for l in lines[start:end]:
    m = re.match(r"^\s+(\d+)\s+(\S.*)$", l)
    if m and l.strip() and not l.strip().startswith("|"):
        pass
    m2 = re.match(r"^\s{2}(\d+)\s{2}(.*)$", l)
    if m2:
        art.append((int(m2.group(1)), m2.group(2)))
print("art rows:", len(art))
for y, row in art:
    print("%2d len=%d %r" % (y, len(row), row))

# --- JSON tiles ------------------------------------------------------------
m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
tiles = m["tiles"]
print("json row 20:", tiles[20])
print("json row 0:", tiles[0])
print("json row 31:", tiles[31])

# --- oracle expected -------------------------------------------------------
d = tempfile.mkdtemp(prefix="probe286-")
from wlengine import scenario as scen  # noqa: E402
scen.compile(SPEC, d)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
env.pop("PYTHONPATH", None)
r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"), "compiled", d, SPEC],
                   capture_output=True, text=True, env=env)
data = json.loads(r.stdout)
exp = data.get("expected", {})
print("expected keys:", sorted(exp.keys()))
maps = exp.get("maps")
if maps:
    print("maps type", type(maps), len(maps))
    mm = maps[1] if isinstance(maps, list) else maps
    cells = mm.get("cells")
    print("cells keys:", sorted(cells.keys()) if isinstance(cells, dict) else type(cells))
    if isinstance(cells, dict):
        print("image row 20:", cells["image"][20])
        print("class row 20:", cells["actionClass"][20])
        print("action row 20:", cells["action"][20])
