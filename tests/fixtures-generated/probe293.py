"""probe293: where can a location name come from in the compiled data?

* search every compiled file for b'Saltwell'
* print the map central directory and info
* print neighbours of (15,20) with image/class
* find cells with image 28 and class 0
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from wlengine import scenario  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
cands = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if "LABTABLES.BIN" in filenames:
        cands.append(dirpath)
dd = cands[0]
print("dir:", dd)
for name in sorted(os.listdir(dd)):
    p = os.path.join(dd, name)
    if not os.path.isfile(p):
        continue
    with open(p, "rb") as fh:
        data = fh.read()
    hits = []
    for needle in (b"Saltwell", b"Ninemile", b"Pumphouse", b"Dry Fork"):
        if needle in data:
            hits.append(needle.decode())
    print("  %-16s %8d %s" % (name, len(data), hits))

sc = scenario.load(dd)
m = sc.maps[1]
print("centralDirectory:", m["centralDirectory"])
print("info:", m["info"])
print("strings:", m["strings"])
print("npcs:", m["npcs"][:1] if m["npcs"] else None)

img = m["cells"]["image"]
cls = m["cells"]["actionClass"]
print("neighbours of (15,20):")
for (dx, dy, n) in [(0, -1, "N"), (0, 1, "S"), (-1, 0, "W"), (1, 0, "E")]:
    x, y = 15 + dx, 20 + dy
    print("  %s (%d,%d) image=%d class=%d" % (n, x, y, img[y][x], cls[y][x]))
print("cells with image 28 and class 0:")
for y in range(32):
    for x in range(32):
        if img[y][x] == 28 and cls[y][x] == 0:
            print("   (%d,%d)" % (x, y))
print("cells with image 28:")
for y in range(32):
    row = [x for x in range(32) if img[y][x] == 28]
    if row:
        print("   y=%d x=%s" % (y, row))
