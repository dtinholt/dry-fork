"""Probe: reference-log moves at the start, and the compiled map vs the JSON."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "..", "SPEC", "scenario")
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))

ref = json.load(open(os.path.join(SPEC, "walkthrough-reference-log.json")))
ev = ref["events"]
for e in ev[:60]:
    print(json.dumps(e)[:200])

print("=== compiled map vs JSON")
import wlengine.scenario as S  # noqa: E402

sc = S.load(os.path.join(HERE, "dd"))
m = sc.map(1)
img = m["cells"]["image"]
cls = m["cells"]["actionClass"]
j = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
jt = j["tiles"]
jc = j["action_class"]
same_yx = all(img[y][x] == jt[y][x] for y in range(32) for x in range(32))
same_xy = all(img[y][x] == jt[x][y] for y in range(32) for x in range(32))
print("compiled == JSON [y][x]:", same_yx, " compiled == JSON [x][y]:", same_xy)
print("compiled cls == JSON cls [y][x]:", all(cls[y][x] == jc[y][x] for y in range(32) for x in range(32)))
print("compiled cls == JSON cls [x][y]:", all(cls[y][x] == jc[x][y] for y in range(32) for x in range(32)))
