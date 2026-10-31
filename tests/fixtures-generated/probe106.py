"""Probe: dump the Saltwell map cells around (2..5, 20) from the scenario JSON and
from the compiled map.

Run:  python3 tests/fixtures-generated/probe106.py
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

SCEN = ROOT / "SPEC" / "scenario"
OUT = ROOT / "tests" / "fixtures-generated" / "dump106.txt"
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
p("keys:", sorted(m1.keys()))
p("tiles row 20 x=0..8:", m1["tiles"][20][0:9])
p("action_class row 20 x=0..8:", m1["action_class"][20][0:9])
p("action_value row 20 x=0..8:", m1["action_value"][20][0:9])
p("records keys:", sorted(m1["records"].keys()) if isinstance(m1.get("records"), dict) else "n/a")
if isinstance(m1.get("records"), dict):
    for k, v in m1["records"].items():
        p("records[%s] = %s" % (k, json.dumps(v)[:800]))

p()
p("### compiled map")
import wlengine.scenario as S  # noqa: E402
import wlengine.maps as M  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="wlprobe"))
S.compile(str(SCEN), str(tmp))
mp = M.load_map(str(tmp), 1)
p("size", mp["size"])
p("actionClass row 20 x=0..8:", mp["cells"]["actionClass"][20][0:9])
p("action row 20 x=0..8:", mp["cells"]["action"][20][0:9])
p("image row 20 x=0..8:", mp["cells"]["image"][20][0:9])
for x in range(0, 9):
    p("cell (%d,20) class=%d action=%d image=%d passable=%s rec=%s" % (
        x, mp["cells"]["actionClass"][20][x], mp["cells"]["action"][20][x],
        mp["cells"]["image"][20][x], M.is_passable(mp, x, 20),
        json.dumps(M.record_at(mp, x, 20))[:200]))

OUT.write_text("\n".join(buf))
print("wrote", OUT, len(buf), "lines")
