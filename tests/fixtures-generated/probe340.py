"""Probe 340: compile the scenario, dump the engine's runtime map1 row 20 and
the oracle's view of the compiled data, then run the M5 bump script and the M6
look script through headless.run.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from wlengine import headless, maps, scenario  # noqa: E402

SCEN = ROOT / "SPEC" / "scenario"
dd = pathlib.Path(tempfile.mkdtemp()) / "data"
dd.mkdir(parents=True)
scenario.compile(str(SCEN), str(dd))
print("compiled files:", sorted(p.name for p in dd.iterdir()))

sc = scenario.Scenario(dd)
m = sc.map(1)
cells = m["cells"]
print("map keys:", sorted(m.keys()))
print("size:", m.get("size"))
print("image[20][0:8]      =", cells["image"][20][0:8])
print("actionClass[20][0:8]=", cells["actionClass"][20][0:8])
print("image[20][12:18]    =", cells["image"][20][12:18])
print("SPEC tiles[20][0:8] =", json.loads((SCEN / "map1-saltwell.json").read_text())["tiles"][20][0:8])
print("SPEC tiles[20][12:18]=", json.loads((SCEN / "map1-saltwell.json").read_text())["tiles"][20][12:18])

print("walk west from (15,20) in the engine map:")
for x in range(15, 0, -1):
    print("  x=%2d image=%3d class=%2d passable=%s" % (
        x, cells["image"][20][x], cells["actionClass"][20][x], maps.is_passable(m, x, 20)))

# oracle view of the compiled data
r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(dd), str(SCEN)],
                   capture_output=True, text=True)
data = json.loads(r.stdout)
if "fatal" in data:
    print("oracle fatal:", data["fatal"][:400])
else:
    exp = data.get("expected", {})
    print("oracle expected sections:", sorted(exp.keys()))
    for key in ("map1", "maps", "map"):
        if key in exp:
            v = exp[key]
            print("oracle expected[%s] type=%s" % (key, type(v).__name__))
            if isinstance(v, dict):
                print("  keys:", sorted(v.keys())[:20])
    orc = data.get("oracle", {})
    print("oracle oracle sections:", sorted(orc.keys()))
    for key in ("map1", "maps", "map"):
        if key in orc:
            v = orc[key]
            print("oracle oracle[%s] type=%s" % (key, type(v).__name__))
            if isinstance(v, dict):
                print("  keys:", sorted(v.keys())[:20])
                if "cells" in v:
                    print("  image[20][0:8] =", v["cells"]["image"][20][0:8])
                    print("  ac[20][0:8]    =", v["cells"]["actionClass"][20][0:8])
    print("errors:", data.get("errors"))

# run the M5 bump script
ev = headless.run(str(dd), {"seed": 19880101, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, None)
print("bump run tail:")
for e in ev[-4:]:
    print("  ", e)

ev2 = headless.run(str(dd), {"seed": 19880101, "script": ["L", "LEFT", {"checkpoint": "a"}]}, None)
print("look run:")
for e in ev2:
    print("  ", e)
