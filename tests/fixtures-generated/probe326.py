"""Probe 326: what does the compiled Saltwell map hold at (14,20)?

The M6 `test_look` expects a `look` event with image 28 at (14,20), while the
scenario JSON says tiles[20][14] == 0 (sand).  Print the engine's decoded
`cells.image` row 20 and the tile row, plus the oracle's view of the same map,
so we can tell which array the `look` event must report.
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(PROJ, "src")
SCEN = os.path.join(PROJ, "SPEC", "scenario")
sys.path.insert(0, SRC)

from wlengine import scenario as scen_mod  # noqa: E402

d = tempfile.mkdtemp(prefix="probe326-")
scen_mod.compile(SCEN, d)
sc = scen_mod.load(d)
m = sc.map(1)
print("map keys:", sorted(m.keys()))
print("size:", m["size"])
print("info:", m["info"])
print("cells keys:", sorted(m["cells"].keys()))
print("tiles row 20:", m["cells"]["tile"][20] if "tile" in m["cells"] else None)
print("image row 20:", m["cells"]["image"][20])
print("actionClass row 20:", m["cells"]["actionClass"][20])
print("action row 20:", m["cells"]["action"][20])
print()
print("image at (14,20):", m["cells"]["image"][20][14])
print("image at (15,20):", m["cells"]["image"][20][15])
print("image at (16,20):", m["cells"]["image"][20][16])
print()
j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
print("json tiles row 20:", j["tiles"][20])
print("json action_class row 20:", j["action_class"][20])
print("json info:", j["info"])
print()
print("location names:", sc.location_names)
print("start:", sc.start)
print("premade party slots:", [p["slot"] for p in sc.premade_party()])
print("party0:", {k: v for k, v in sc.premade_party()[0].items() if k != "items"})
print()
# oracle view of the compiled map
r = subprocess.run([sys.executable, os.path.join(PROJ, "tests", "oracle_tool.py"),
                    "compiled", d, SCEN], capture_output=True, text=True)
try:
    data = json.loads(r.stdout)
except ValueError:
    print("oracle failed:", r.stdout[-500:], r.stderr[-500:])
    raise SystemExit(0)
maps = data.get("oracle", {}).get("maps") or data.get("oracle", {}).get("map")
print("oracle map keys:", list(data.get("oracle", {}).keys()))
if isinstance(maps, dict):
    mm = maps.get("1") or maps.get(1)
    if mm:
        print("oracle image row 20:", mm.get("cells", {}).get("image", [None] * 21)[20])
        print("oracle tile row 20:", mm.get("cells", {}).get("tile", [None] * 21)[20])
