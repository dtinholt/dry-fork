"""Probe 287: JSON tiles/action_class row 20 vs the compiled map, plus the
oracle's expected map cells, plus the reference log's first 40 events."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SPEC = os.path.join(ROOT, "SPEC", "scenario")

m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
print("JSON tiles[20]      :", m["tiles"][20])
print("JSON action_class[20]:", m["action_class"][20])
print("JSON action_value[20]:", m["action_value"][20])
print("JSON tiles[19]      :", m["tiles"][19])
print("JSON action_class[19]:", m["action_class"][19])

sc = json.load(open(os.path.join(SPEC, "scenario.json")))
print("scenario.json keys:", sorted(sc.keys()))
print(json.dumps(sc, indent=1)[:1500])

d = tempfile.mkdtemp(prefix="probe287-")
from wlengine import scenario as scen  # noqa: E402
from wlengine import maps as M  # noqa: E402
scen.compile(SPEC, d)
mp = M.load_map(d, 1)
print("compiled map keys:", sorted(mp.keys()))
cells = mp["cells"]
print("compiled image[20]      :", cells["image"][20])
print("compiled actionClass[20]:", cells["actionClass"][20])
print("compiled action[20]     :", cells["action"][20])

env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
env.pop("PYTHONPATH", None)
r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"), "compiled", d, SPEC],
                   capture_output=True, text=True, env=env)
data = json.loads(r.stdout)
maps = data.get("expected", {}).get("maps", {})
mm = maps.get("1") or maps.get(1)
print("expected map1 keys:", sorted(mm.keys()) if isinstance(mm, dict) else type(mm))
if isinstance(mm, dict):
    for k in ("cells", "tiles"):
        if k in mm:
            print("expected", k, "type", type(mm[k]))
            if isinstance(mm[k], dict):
                print("  keys", sorted(mm[k].keys()))
                for kk in ("image", "actionClass", "action"):
                    if kk in mm[k]:
                        print("  %s[20]:" % kk, mm[k][kk][20])
            elif isinstance(mm[k], list):
                print("  [20]:", mm[k][20])

ref = json.load(open(os.path.join(SPEC, "walkthrough-reference-log.json")))["events"]
print("--- reference log first 40 ---")
for e in ref[:40]:
    print(e)
