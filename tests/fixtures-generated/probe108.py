"""Probe: find the cactus tiles in map1 and compare the oracle's map cells with
the engine's compiled map.

Run:  python3 tests/fixtures-generated/probe108.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

SCEN = ROOT / "SPEC" / "scenario"
OUT = ROOT / "tests" / "fixtures-generated" / "dump108.txt"
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
t = m1["tiles"]
ac = m1["action_class"]
av = m1["action_value"]
p("cactus (tile 11) positions as [y][x]:")
for y in range(32):
    for x in range(32):
        if t[y][x] == 11:
            p("  y=%d x=%d class=%d action=%d" % (y, x, ac[y][x], av[y][x]))
p("class 11 positions as [y][x]:")
for y in range(32):
    for x in range(32):
        if ac[y][x] == 11:
            p("  y=%d x=%d tile=%d action=%d" % (y, x, t[y][x], av[y][x]))

p()
p("### oracle map cells")
import wlengine.scenario as S  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="wlprobe"))
S.compile(str(SCEN), str(tmp))
r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled",
                    str(tmp), str(SCEN)], capture_output=True, text=True)
data = json.loads(r.stdout)
maps = data["oracle"]["maps"]
p("maps keys:", sorted(maps.keys()))
m = maps["1"] if "1" in maps else maps[1]
p("map keys:", sorted(m.keys()))
cells = m["cells"]
p("cells keys:", sorted(cells.keys()))
p("actionClass[20][0:9]:", cells["actionClass"][20][0:9])
p("actionClass[2][0:9]:", cells["actionClass"][2][0:9])
p("image[20][0:9]:", cells["image"][20][0:9])
p("image[2][0:9]:", cells["image"][2][0:9])
p("actionClass[17][8]=%r actionClass[8][17]=%r" % (cells["actionClass"][17][8], cells["actionClass"][8][17]))
p("image[17][8]=%r image[8][17]=%r" % (cells["image"][17][8], cells["image"][8][17]))
p("actionClass[20][3]=%r actionClass[3][20]=%r" % (cells["actionClass"][20][3], cells["actionClass"][3][20]))
p("image[20][3]=%r image[3][20]=%r" % (cells["image"][20][3], cells["image"][3][20]))
p("actionClass[20][2]=%r actionClass[2][20]=%r" % (cells["actionClass"][20][2], cells["actionClass"][2][20]))
p("image[20][2]=%r image[2][20]=%r" % (cells["image"][20][2], cells["image"][2][20]))

OUT.write_text("\n".join(buf))
print("wrote", OUT, len(buf), "lines")
