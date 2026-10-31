"""Probe 342: brute-force where image 28 / class 11 live in each map, and what
the engine's compiled map1 image array looks like in full.
"""
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from wlengine import scenario  # noqa: E402

SCEN = ROOT / "SPEC" / "scenario"
dd = pathlib.Path(tempfile.mkdtemp()) / "data"
dd.mkdir(parents=True)
scenario.compile(str(SCEN), str(dd))
sc = scenario.Scenario(dd)

for loc in range(4):
    m = sc.map(loc)
    img = m["cells"]["image"]
    ac = m["cells"]["actionClass"]
    size = m["size"]
    hits28 = [(x, y) for y in range(size) for x in range(size) if img[y][x] == 28]
    hits11 = [(x, y) for y in range(size) for x in range(size) if ac[y][x] == 11]
    print("loc %d size %d: image==28 at %s" % (loc, size, hits28[:20]))
    print("   class==11 at %s" % (hits11[:20],))
    print("   image[20] =", img[20])
    print("   ac[20]    =", ac[20])

m = sc.map(1)
img = m["cells"]["image"]
print("map1 image[14][18:22] =", img[14][18:22])
print("map1 image[15][18:22] =", img[15][18:22])
print("map1 image[20][13:17] =", img[20][13:17])
print("map1 image[19][13:17] =", img[19][13:17])
print("map1 image[21][13:17] =", img[21][13:17])
print("map1 image[20][14] =", img[20][14], " image[14][20] =", img[14][20])
print("map1 image[20][15] =", img[20][15], " image[15][20] =", img[15][20])
