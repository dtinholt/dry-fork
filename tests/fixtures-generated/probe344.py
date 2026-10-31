import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wlengine import scenario

sc = scenario.load(sys.argv[1] if len(sys.argv) > 1 else "data")
m = sc.map(0)
cells = m["cells"]
img = cells["image"]
cls = cells["actionClass"]
print("rows", len(img), "cols", len(img[0]))
for y in range(18, 23):
    print("y=%d" % y, [img[y][x] for x in range(0, 20)])
print("classes")
for y in range(18, 23):
    print("y=%d" % y, [cls[y][x] for x in range(0, 20)])
print("transposed img[14][20]=", img[14][20] if len(img) > 14 and len(img[14]) > 20 else None)
print("transposed img[3][20]=", img[3][20] if len(img) > 3 and len(img[3]) > 20 else None)
print("transposed img[2][20]=", img[2][20] if len(img) > 2 and len(img[2]) > 20 else None)
print("start", sc.start if hasattr(sc, "start") else None)
