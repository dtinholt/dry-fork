"""Probe 190: items.json, walkthrough expected blocks, map1 cells near (2,20),
and the compiled map cells."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump190.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


SC = os.path.join(ROOT, "SPEC", "scenario")

items = json.load(open(os.path.join(SC, "items.json"), encoding="utf-8"))
p("=" * 70)
p("ITEMS")
for it in items["items"]:
    p(json.dumps(it, sort_keys=True))

wt = json.load(open(os.path.join(SC, "walkthrough.json"), encoding="utf-8"))
p("=" * 70)
p("WALKTHROUGH checkpoints")
for c in wt["checkpoints"]:
    p(json.dumps(c, sort_keys=True)[:3000])

m1 = json.load(open(os.path.join(SC, "map1-saltwell.json"), encoding="utf-8"))
p("=" * 70)
p("map1 keys: %r" % list(m1))
for y in (19, 20, 21):
    p("tiles[%d] = %r" % (y, m1["tiles"][y]))
ac = m1.get("action_class")
if ac:
    for y in (19, 20, 21):
        p("action_class[%d] = %r" % (y, ac[y]))
p("info: %r" % json.dumps(m1.get("info"), sort_keys=True))
p("actions: %r" % json.dumps(m1.get("actions"), sort_keys=True)[:3000])

# compile
from wlengine import scenario as scmod  # noqa: E402

d = tempfile.mkdtemp()
try:
    scmod.compile(SC, d)
    p("=" * 70)
    p("compiled dir: %r" % sorted(os.listdir(d)))
    from wlengine import maps as mapsmod  # noqa: E402
    m = mapsmod.load_map(d, 1)
    p("compiled map1 size %r" % m["size"])
    for y in (19, 20, 21):
        p("compiled tiles[%d] = %r" % (y, m["tiles"][y]))
        p("compiled actionClass[%d] = %r" % (y, m["cells"]["actionClass"][y]))
        p("compiled action[%d] = %r" % (y, m["cells"]["action"][y]))
        p("compiled image[%d] = %r" % (y, m["cells"]["image"][y]))
except Exception as e:  # noqa: BLE001
    p("compile failed: %s: %s" % (type(e).__name__, e))

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
