"""Probe 375: dump oracle map1 tiles/classes row 20 and compare with scenario JSON.

Run: python3 tests/fixtures-generated/probe375.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wl_support as W  # noqa: E402
from wlengine import scenario  # noqa: E402

d = tempfile.mkdtemp(prefix="probe375-")
scenario.compile(str(W.SCENARIO), d)

r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"),
                    "compiled", d, str(W.SCENARIO)], capture_output=True, text=True)
data = json.loads(r.stdout)
m1 = data["oracle"]["map1"]
print("map1 keys:", list(m1.keys()))
print(json.dumps({k: v for k, v in m1.items() if k not in ("tiles", "action_class", "action_value")}, indent=1)[:3000])
print()
for k in ("tiles", "action_class", "action_value"):
    if k in m1:
        print(k, "row20:", m1[k][20][:20])
print()
exp = data["expected"].get("map1")
if exp:
    print("expected map1 keys:", list(exp.keys()))
    for k in ("tiles", "action_class", "action_value"):
        if k in exp:
            print("expected", k, "row20:", exp[k][20][:20])
