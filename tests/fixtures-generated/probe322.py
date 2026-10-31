"""Probe 322: engine image grid vs scenario tiles+10, elementwise; oracle cells.

Run: python3 tests/fixtures-generated/probe322.py
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
SCEN = os.path.join(ROOT, "SPEC", "scenario")
j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
tiles = j["tiles"]
ac = j["action_class"]

sc = S.load(OUT)
m = sc.map(1)
img = m["cells"]["image"]
eac = m["cells"]["actionClass"]

bad = []
for y in range(32):
    for x in range(32):
        if img[y][x] != tiles[y][x] + 10:
            bad.append((x, y, img[y][x], tiles[y][x] + 10))
print("engine image != tiles+10 count:", len(bad), bad[:10])

badac = []
for y in range(32):
    for x in range(32):
        if eac[y][x] != ac[y][x]:
            badac.append((x, y, eac[y][x], ac[y][x]))
print("engine ac != json ac count:", len(badac), badac[:10])

print("tiles[20][14]", tiles[20][14], "tiles[14][20]", tiles[14][20])
print("tiles[20][15]", tiles[20][15], "tiles[15][20]", tiles[15][20])
print("tiles[19][15]", tiles[19][15], "tiles[15][19]", tiles[15][19])
print("ac[20][14]", ac[20][14], "ac[14][20]", ac[14][20])
print("ac[20][15]", ac[20][15], "ac[15][20]", ac[15][20])

r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"),
                    "compiled", OUT, SCEN], capture_output=True, text=True)
data = json.loads(r.stdout)
cells = data["oracle"]["cells"]["cells"]
print("oracle inner cells keys:", sorted(cells.keys()))
oimg = cells.get("image")
if oimg:
    print("oracle image[20]:", oimg[20])
    print("oracle image[14]:", oimg[14])
    print("oracle image[20][14]:", oimg[20][14], "oracle image[14][20]:", oimg[14][20])
    print("oracle image[20][15]:", oimg[20][15], "oracle image[15][20]:", oimg[15][20])
    print("oracle image[19][15]:", oimg[19][15], "oracle image[15][19]:", oimg[15][19])
oac = cells.get("actionClass")
if oac:
    print("oracle ac[20][14]:", oac[20][14], "oracle ac[14][20]:", oac[14][20])
    print("oracle ac[20][15]:", oac[20][15], "oracle ac[15][20]:", oac[15][20])
