"""Probe 374: run the oracle on the engine's compiled data and dump map1 tiles.

Run: python3 tests/fixtures-generated/probe374.py
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

d = tempfile.mkdtemp(prefix="probe374-")
scenario.compile(str(W.SCENARIO), d)

r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"),
                    "compiled", d, str(W.SCENARIO)], capture_output=True, text=True)
print("rc", r.returncode)
print("stderr", r.stderr[-2000:])
data = json.loads(r.stdout)
print("top keys:", list(data.keys()))
print("oracle keys:", list(data.get("oracle", {}).keys()))
print("errors:", data.get("errors"))
maps = data.get("oracle", {}).get("maps")
if maps is None:
    print("no maps section")
else:
    print("maps type:", type(maps))
    print(json.dumps(maps, indent=1)[:2000])
