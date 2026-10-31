"""Probe 416: load the compiled map 1 through the engine and compare cells."""
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path("src").resolve()))
sys.path.insert(0, str(pathlib.Path("tests").resolve()))

import wlengine.maps as M  # noqa: E402
import wlengine.scenario as S  # noqa: E402

SCEN = pathlib.Path("SPEC/scenario")
OUT = pathlib.Path("tests/fixtures-generated/dump416.txt")
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


p("maps module attrs:", [n for n in dir(M) if not n.startswith("_")])

dd = pathlib.Path(tempfile.mkdtemp(prefix="probe416-"))
S.compile(str(SCEN), str(dd))
p("compiled dir", dd)

# how does the engine load maps?
for name in ("load_maps", "load_map", "read_maps", "maps_from_game", "load_game"):
    if hasattr(M, name):
        p("has", name)

try:
    maps = M.load_maps(str(dd))
    p("load_maps ->", type(maps), len(maps) if hasattr(maps, "__len__") else "")
except Exception as e:
    p("load_maps failed:", type(e).__name__, e)

m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
p("json action_class y=20:", m1["action_class"][20])
p("json tiles y=20:", m1["tiles"][20])
p("json action_class y=14:", m1["action_class"][14])
p("json tiles y=14:", m1["tiles"][14])
p("json tiles x=14 col:", [m1["tiles"][y][14] for y in range(32)])
p("json tiles x=15 col:", [m1["tiles"][y][15] for y in range(32)])

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
