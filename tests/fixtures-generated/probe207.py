"""Probe 207: compiled map1 row 20, reference-log bumps, walkthrough script,
M3 map cell checks, item record structure."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump207.txt")
buf = []


def out(s=""):
    buf.append(str(s))


# 1. compile fresh
import tempfile  # noqa: E402
from wlengine import scenario as scmod  # noqa: E402

tmp = tempfile.mkdtemp()
scmod.compile(os.path.join(ROOT, "SPEC", "scenario"), tmp)
out("compiled to %s: %s" % (tmp, sorted(os.listdir(tmp))))

from wlengine import scenario as sc  # noqa: E402

s = sc.load(tmp)
m = s.map(1)
out("map1 size %s" % m["size"])
out("compiled actionClass row 20: %s" % m["cells"]["actionClass"][20])
out("compiled action row 20: %s" % m["cells"]["action"][20])
out("compiled image row 20: %s" % m["cells"]["image"][20])
out("compiled actionClass row 19: %s" % m["cells"]["actionClass"][19])
out("records keys: %s" % list(m["actions"]))
out("actions[11]: %s" % json.dumps(m["actions"].get(11))[:400])
out("actions[1]: %s" % json.dumps(m["actions"].get(1))[:400])
out("actions[10]: %s" % json.dumps(m["actions"].get(10))[:400])
out("actions[6]: %s" % json.dumps(m["actions"].get(6))[:400])
out("start: %s" % json.dumps(s.start))
out("item 3: %s" % json.dumps(s.item(3)))
out("item 4: %s" % json.dumps(s.item(4)))
out("item 5: %s" % json.dumps(s.item(5)))
out("item 6: %s" % json.dumps(s.item(6)))
out("item 9: %s" % json.dumps(s.item(9)))
out("item 11: %s" % json.dumps(s.item(11)))
out("party[0]: %s" % json.dumps(s.premade_party()[0]))

# 2. reference log bumps
ref = json.load(open(os.path.join(ROOT, "SPEC", "scenario",
                                  "walkthrough-reference-log.json")))
out("=== reference bumps ===")
for i, e in enumerate(ref["events"]):
    if e.get("type") in ("bump", "cell_change", "transition", "map_change"):
        out("%d: %s" % (i, json.dumps(e)[:250]))

# 3. walkthrough script
wt = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough.json")))
out("=== walkthrough script (first 40) ===")
for i, t in enumerate(wt["script"][:40]):
    out("%d: %s" % (i, json.dumps(t)[:200]))
out("=== walkthrough checkpoints ===")
out(json.dumps(wt.get("checkpoints"))[:1500])
out("=== walkthrough start ===")
out(json.dumps(wt.get("start"))[:500])

# 4. M3 map cell checks
full = os.path.join(ROOT, "tests", "test_m3_maps.py")
ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
out("=== test_m3_maps.py cell-related ===")
for i, l in enumerate(ls):
    if any(p in l for p in ("action_class", "actionClass", "cells", "tiles", "def test_")):
        out("%d: %s" % (i + 1, l))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
