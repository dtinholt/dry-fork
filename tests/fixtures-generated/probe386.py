"""Probe: run the oracle tool on the compiled data and inspect map1 cells."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TESTS = ROOT / "tests"
DD = TESTS / "fixtures-generated" / "dd3"

r = subprocess.run([sys.executable, str(TESTS / "oracle_tool.py"), "compiled", str(DD), str(ROOT / "SPEC" / "scenario")],
                   capture_output=True, text=True)
print("rc", r.returncode)
if r.returncode:
    print(r.stdout[-2000:], r.stderr[-2000:])
    raise SystemExit(1)
d = json.loads(r.stdout)
print("errors", d.get("errors"))
o = d["oracle"]
print("oracle keys", sorted(o.keys()))
m = o.get("map1")
print("map1 type", type(m))
if isinstance(m, dict):
    print("map1 keys", sorted(m.keys()))
    for k, v in m.items():
        if isinstance(v, list):
            print(k, "list len", len(v), json.dumps(v[:3])[:300])
        else:
            print(k, json.dumps(v)[:300])
