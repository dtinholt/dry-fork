"""Probe: compile fresh, compare map1 tiles with the JSON, find image 28 near (15,20)."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "..", "SPEC", "scenario")
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))

import wlengine.scenario as S  # noqa: E402

d = tempfile.mkdtemp()
S.compile(SPEC, d)
sc = S.load(d)
m = sc.map(1)
img = m["cells"]["image"]
cls = m["cells"]["actionClass"]
j = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
jt, jc = j["tiles"], j["action_class"]
print("compiled == JSON [y][x]:", all(img[y][x] == jt[y][x] for y in range(32) for x in range(32)))
print("compiled == JSON [x][y]:", all(img[y][x] == jt[x][y] for y in range(32) for x in range(32)))
print("cls == JSON [y][x]:", all(cls[y][x] == jc[y][x] for y in range(32) for x in range(32)))
print("compiled (14,20) img[y][x]=%d cls=%d" % (img[20][14], cls[20][14]))
print("compiled (15,20) img[y][x]=%d cls=%d" % (img[20][15], cls[20][15]))
print("compiled (15,19) img[y][x]=%d cls=%d" % (img[19][15], cls[19][15]))
print("compiled (2,20) img[y][x]=%d cls=%d" % (img[20][2], cls[20][2]))
print("compiled (3,20) img[y][x]=%d cls=%d" % (img[20][3], cls[20][3]))
print("image 28 cells near (15,20):")
for y in range(15, 26):
    for x in range(10, 21):
        if img[y][x] == 28:
            print("   (x=%d,y=%d) cls=%d" % (x, y, cls[y][x]))
