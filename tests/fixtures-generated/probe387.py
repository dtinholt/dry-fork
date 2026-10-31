"""Probe: dump map1 cells from the oracle view around (14,20) and (15,20)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TESTS = ROOT / "tests"
DD = TESTS / "fixtures-generated" / "dd3"

r = subprocess.run([sys.executable, str(TESTS / "oracle_tool.py"), "compiled", str(DD), str(ROOT / "SPEC" / "scenario")],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
m = d["oracle"]["map1"]
cells = m["cells"]
print("cells keys", sorted(cells.keys()))
for k, v in cells.items():
    print(k, type(v), (len(v) if hasattr(v, "__len__") else v))
ac = cells["actionClass"]
print("actionClass[20][13:17]", ac[20][13:17])
print("actionClass[11][12:18]", ac[11][12:18])
for k in sorted(cells.keys()):
    if k == "actionClass":
        continue
    v = cells[k]
    if isinstance(v, list) and v and isinstance(v[0], list):
        print(k, "row20", v[20][13:17], "row11", v[11][12:18])
    else:
        print(k, json.dumps(v)[:200])
print("actions", json.dumps(m["actions"])[:1500])
