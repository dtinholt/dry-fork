"""Probe 419: compare the engine's decoded map cells with the oracle's."""
import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path("src").resolve()))
sys.path.insert(0, str(pathlib.Path("tests").resolve()))

import wlengine.maps as M  # noqa: E402
import wlengine.scenario as S  # noqa: E402

SCEN = pathlib.Path("SPEC/scenario")
OUT = pathlib.Path("tests/fixtures-generated/dump419.txt")
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


dd = pathlib.Path(tempfile.mkdtemp(prefix="probe419-"))
S.compile(str(SCEN), str(dd))
r = subprocess.run([sys.executable, "tests/oracle_tool.py", "compiled", str(dd), str(SCEN)],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
ocells = d["oracle"]["map1"]["cells"]

# how does the engine load a map?
import inspect
p("load_map sig:", inspect.signature(M.load_map))
p("decode_map sig:", inspect.signature(M.decode_map))
p("is_passable sig:", inspect.signature(M.is_passable))
p("image_at sig:", inspect.signature(M.image_at))

# try to load via containers
import wlengine.containers as C
p("containers attrs:", [n for n in dir(C) if not n.startswith("_")])

game = (dd / "GAME1").read_bytes()
tables = json.loads((dd / "LABTABLES.BIN").read_bytes() if False else "{}") if False else None

# use the engine's own scenario loader if it has one
for name in ("load_scenario", "load", "Scenario", "load_data"):
    if hasattr(S, name):
        p("scenario has", name)

try:
    sc = S.load(str(dd))
    p("S.load ->", type(sc))
    m = sc.map(1)
    p("map keys:", sorted(m.keys()))
    ecells = m["cells"]
    for k in sorted(ecells.keys()):
        p("engine cells", k, "rows", len(ecells[k]), "cols", len(ecells[k][0]))
    for k in ("actionClass", "action", "image"):
        if k in ecells and k in ocells:
            diffs = []
            for y in range(32):
                for x in range(32):
                    if ecells[k][y][x] != ocells[k][y][x]:
                        diffs.append((x, y, ecells[k][y][x], ocells[k][y][x]))
            p("DIFFS", k, len(diffs), diffs[:20])
            # transposed comparison
            tdiffs = []
            for y in range(32):
                for x in range(32):
                    if ecells[k][y][x] != ocells[k][x][y]:
                        tdiffs.append((x, y, ecells[k][y][x], ocells[k][x][y]))
            p("TRANSPOSED DIFFS", k, len(tdiffs), tdiffs[:20])
except Exception as e:
    import traceback
    p("S.load failed:", traceback.format_exc()[-2000:])

m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
p("json action_class[20][3] =", m1["action_class"][20][3], " [3][20] =", m1["action_class"][3][20])
p("json action_class[20][2] =", m1["action_class"][20][2], " [2][20] =", m1["action_class"][2][20])
p("json tiles[20][14] =", m1["tiles"][20][14], " [14][20] =", m1["tiles"][14][20])
p("json tiles[20][3] =", m1["tiles"][20][3], " [3][20] =", m1["tiles"][3][20])
p("json tiles[20][2] =", m1["tiles"][20][2], " [2][20] =", m1["tiles"][2][20])
p("json action_class[20][14] =", m1["action_class"][20][14], " [14][20] =", m1["action_class"][14][20])
p("json action_class[20][15] =", m1["action_class"][20][15], " [15][20] =", m1["action_class"][15][20])
p("json tiles[20][15] =", m1["tiles"][20][15], " [15][20] =", m1["tiles"][15][20])
p("json tiles[20][0] =", m1["tiles"][20][0], " [0][20] =", m1["tiles"][0][20])
p("json tiles[20][31] =", m1["tiles"][20][31], " [31][20] =", m1["tiles"][31][20])
p("json tiles[14][23] =", m1["tiles"][14][23], " [23][14] =", m1["tiles"][23][14])
p("json action_class[14][23] =", m1["action_class"][14][23], " [23][14] =", m1["action_class"][23][14])

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
