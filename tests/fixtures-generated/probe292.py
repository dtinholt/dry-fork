"""probe292: what does the compiled data dir contain, and where can a location
name come from?  Also: what does a fresh new game state look like?"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from wlengine import containers, headless, scenario  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
cands = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if "LABTABLES.BIN" in filenames:
        cands.append(dirpath)
print("compiled dirs:", cands)
dd = cands[0]
print("files:", sorted(os.listdir(dd)))

t = containers.read_tables(os.path.join(dd, "LABTABLES.BIN"))
print("table keys:", sorted(t.keys()))
for k in sorted(t.keys()):
    v = t[k]
    if isinstance(v, (list, tuple)) and len(v) < 40:
        print("  %s = %r" % (k, v))
    else:
        print("  %s = <%s len %s>" % (k, type(v).__name__, len(v) if hasattr(v, "__len__") else "?"))

sc = scenario.load(dd)
print("scenario attrs:", [a for a in dir(sc) if not a.startswith("_")])
print("start:", sc.start)
print("maps:", sorted(sc.maps.keys()))
m = sc.maps[1]
print("map keys:", sorted(m.keys()))
print("info:", m["info"])
print("strings:", m["strings"][:5])

eng = headless.Engine(dd, seed=20261021)
eng.new_game(20261021)
print("events:", eng.events)
print("x,y,loc:", eng.x, eng.y, eng.location)
print("tiles row 20:", m["cells"]["image"][20][:20])
print("class row 20:", m["cells"]["actionClass"][20][:20])
print("action row 20:", m["cells"]["action"][20][:20])
print("image at 14,20:", m["cells"]["image"][20][14])
print("class at 14,20:", m["cells"]["actionClass"][20][14])
print("border image:", m["info"]["borderImage"])
