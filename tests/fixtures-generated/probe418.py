"""Probe 418: oracle map1 cells vs the JSON arrays."""
import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path("src").resolve()))
sys.path.insert(0, str(pathlib.Path("tests").resolve()))

import wlengine.scenario as S  # noqa: E402

SCEN = pathlib.Path("SPEC/scenario")
OUT = pathlib.Path("tests/fixtures-generated/dump418.txt")
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


dd = pathlib.Path(tempfile.mkdtemp(prefix="probe418-"))
S.compile(str(SCEN), str(dd))
r = subprocess.run([sys.executable, "tests/oracle_tool.py", "compiled", str(dd), str(SCEN)],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
o = d["oracle"]
cells = o["map1"]["cells"]
p("oracle cells keys:", sorted(cells.keys()))
for k in sorted(cells.keys()):
    v = cells[k]
    if isinstance(v, list) and v and isinstance(v[0], list):
        p("  %s rows=%d cols=%d" % (k, len(v), len(v[0])))
        for y in (14, 20):
            p("    y=%2d %s" % (y, v[y]))
    else:
        p("  %s = %s" % (k, str(v)[:300]))

m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
p("JSON tiles[y][x] y=20:", m1["tiles"][20])
p("JSON tiles[y][x] y=14:", m1["tiles"][14])
p("JSON tiles[x][y] x=20:", m1["tiles"][20])
p("JSON tiles[x][y] x=14:", m1["tiles"][14])
p("JSON action_class[y][x] y=20:", m1["action_class"][20])
p("JSON action_class[y][x] y=14:", m1["action_class"][14])
p("JSON action_class[x][y] x=20:", m1["action_class"][20])
p("JSON action_class[x][y] x=14:", m1["action_class"][14])
p("JSON action_value[y][x] y=20:", m1["action_value"][20])
p("JSON action_value[y][x] y=14:", m1["action_value"][14])
p("JSON action_value[x][y] x=20:", m1["action_value"][20])
p("JSON action_value[x][y] x=14:", m1["action_value"][14])

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
