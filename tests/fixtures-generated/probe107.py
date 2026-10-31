"""Probe: figure out the orientation of the scenario map arrays.

Run:  python3 tests/fixtures-generated/probe107.py
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

SCEN = ROOT / "SPEC" / "scenario"
OUT = ROOT / "tests" / "fixtures-generated" / "dump107.txt"
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
t = m1["tiles"]
ac = m1["action_class"]
av = m1["action_value"]
p("len(tiles)=%d len(tiles[0])=%d" % (len(t), len(t[0])))
p("len(action_class)=%d len(action_class[0])=%d" % (len(ac), len(ac[0])))
p("tiles[17][8]=%r tiles[8][17]=%r" % (t[17][8], t[8][17]))
p("ac[17][8]=%r ac[8][17]=%r" % (ac[17][8], ac[8][17]))
p("tiles[20][15]=%r tiles[15][20]=%r" % (t[20][15], t[15][20]))
p("ac[20][15]=%r ac[15][20]=%r" % (ac[20][15], ac[15][20]))
p("tiles[20][2]=%r tiles[2][20]=%r" % (t[20][2], t[2][20]))
p("ac[20][2]=%r ac[2][20]=%r" % (ac[20][2], ac[2][20]))
p("tiles[20][3]=%r tiles[3][20]=%r" % (t[20][3], t[3][20]))
p("ac[20][3]=%r ac[3][20]=%r" % (ac[20][3], ac[3][20]))
p("tiles[20][0]=%r tiles[0][20]=%r" % (t[20][0], t[0][20]))
p("ac[20][0]=%r ac[0][20]=%r" % (ac[20][0], ac[0][20]))
p("tiles[20][1]=%r tiles[1][20]=%r" % (t[20][1], t[1][20]))
p("ac[20][1]=%r ac[1][20]=%r" % (ac[20][1], ac[1][20]))
p("tiles[20][4]=%r tiles[4][20]=%r" % (t[20][4], t[4][20]))
p("ac[20][4]=%r ac[4][20]=%r" % (ac[20][4], ac[4][20]))
p("tiles[20][5]=%r tiles[5][20]=%r" % (t[20][5], t[5][20]))
p("ac[20][5]=%r ac[5][20]=%r" % (ac[20][5], ac[5][20]))
p("tiles[20][6]=%r tiles[6][20]=%r" % (t[20][6], t[6][20]))
p("ac[20][6]=%r ac[6][20]=%r" % (ac[20][6], ac[6][20]))
p("tiles[20][7]=%r tiles[7][20]=%r" % (t[20][7], t[7][20]))
p("ac[20][7]=%r ac[7][20]=%r" % (ac[20][7], ac[7][20]))
p("tiles[20][8]=%r tiles[8][20]=%r" % (t[20][8], t[8][20]))
p("ac[20][8]=%r ac[8][20]=%r" % (ac[20][8], ac[8][20]))
p("tiles[20][9]=%r tiles[9][20]=%r" % (t[20][9], t[9][20]))
p("ac[20][9]=%r ac[9][20]=%r" % (ac[20][9], ac[9][20]))
p("tiles[20][10]=%r tiles[10][20]=%r" % (t[20][10], t[10][20]))
p("ac[20][10]=%r ac[10][20]=%r" % (ac[20][10], ac[10][20]))
p("tiles[20][11]=%r tiles[11][20]=%r" % (t[20][11], t[11][20]))
p("ac[20][11]=%r ac[11][20]=%r" % (ac[20][11], ac[11][20]))
p("tiles[20][12]=%r tiles[12][20]=%r" % (t[20][12], t[12][20]))
p("ac[20][12]=%r ac[12][20]=%r" % (ac[20][12], ac[12][20]))
p("tiles[20][13]=%r tiles[13][20]=%r" % (t[20][13], t[13][20]))
p("ac[20][13]=%r ac[13][20]=%r" % (ac[20][13], ac[13][20]))
p("tiles[20][14]=%r tiles[14][20]=%r" % (t[20][14], t[14][20]))
p("ac[20][14]=%r ac[14][20]=%r" % (ac[20][14], ac[14][20]))
p("tiles[20][15]=%r tiles[15][20]=%r" % (t[20][15], t[15][20]))
p("ac[20][15]=%r ac[15][20]=%r" % (ac[20][15], ac[15][20]))
p("tiles[20][16]=%r tiles[16][20]=%r" % (t[20][16], t[16][20]))
p("ac[20][16]=%r ac[16][20]=%r" % (ac[20][16], ac[16][20]))
p("tiles[20][17]=%r tiles[17][20]=%r" % (t[20][17], t[17][20]))
p("ac[20][17]=%r ac[17][20]=%r" % (ac[20][17], ac[17][20]))
p("tiles[20][18]=%r tiles[18][20]=%r" % (t[20][18], t[18][20]))
p("ac[20][18]=%r ac[18][20]=%r" % (ac[20][18], ac[18][20]))
p("tiles[20][19]=%r tiles[19][20]=%r" % (t[20][19], t[19][20]))
p("ac[20][19]=%r ac[19][20]=%r" % (ac[20][19], ac[19][20]))
p("tiles[20][20]=%r" % (t[20][20],))
p("ac[20][20]=%r" % (ac[20][20],))

p()
p("### compiled map")
import wlengine.scenario as S  # noqa: E402
import wlengine.maps as M  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="wlprobe"))
S.compile(str(SCEN), str(tmp))
mp = M.load_map(str(tmp), 1)
p("size", mp["size"])
for (x, y) in [(8, 17), (15, 20), (2, 20), (3, 20), (0, 20), (1, 20), (4, 20), (5, 20)]:
    p("cell (%d,%d) class=%d action=%d image=%d passable=%s" % (
        x, y, mp["cells"]["actionClass"][y][x], mp["cells"]["action"][y][x],
        mp["cells"]["image"][y][x], M.is_passable(mp, x, y)))
p("row20 classes:", mp["cells"]["actionClass"][20][0:20])
p("row20 images:", mp["cells"]["image"][20][0:20])
p("col20 classes:", [mp["cells"]["actionClass"][yy][20] for yy in range(0, 20)])
p("col20 images:", [mp["cells"]["image"][yy][20] for yy in range(0, 20)])

OUT.write_text("\n".join(buf))
print("wrote", OUT, len(buf), "lines")
