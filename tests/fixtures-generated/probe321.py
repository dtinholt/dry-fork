"""Probe 321: neighbourhood of (15,20) in the engine map and the oracle view.

Run: python3 tests/fixtures-generated/probe321.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wlengine.scenario as S  # noqa: E402

OUT = os.path.join(HERE, "probe320data")
sc = S.load(OUT)
m = sc.map(1)
img = m["cells"]["image"]
ac = m["cells"]["actionClass"]
print("engine image rows 18..22, cols 10..20:")
for y in range(18, 23):
    print(y, [img[y][x] for x in range(10, 21)])
print("engine ac rows 18..22, cols 10..20:")
for y in range(18, 23):
    print(y, [ac[y][x] for x in range(10, 21)])

print("cells with image 28:")
for y in range(32):
    for x in range(32):
        if img[y][x] == 28:
            print("  ", x, y, "ac", ac[y][x])

# oracle
r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"),
                    "compiled", OUT, os.path.join(ROOT, "SPEC", "scenario")],
                   capture_output=True, text=True)
data = json.loads(r.stdout)
print("oracle keys:", sorted(data.keys()))
cells = data["oracle"].get("cells") or data["oracle"].get("map1") or {}
print("oracle cells keys:", sorted(cells.keys()) if isinstance(cells, dict) else type(cells))
if isinstance(cells, dict):
    for k in ("image", "actionClass", "action", "tiles"):
        if k in cells:
            v = cells[k]
            print("oracle", k, "row20:", v[20])
            print("oracle", k, "col20:", [v[y][20] for y in range(32)])
