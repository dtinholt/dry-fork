"""Probe 211: dump the compiled Saltwell map row 20 and the passability rule."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump211.txt")
buf = []


def out(s=""):
    buf.append(str(s))


import wlengine.scenario as sc  # noqa: E402

d = tempfile.mkdtemp(prefix="probe211")
sc.compile(os.path.join(ROOT, "SPEC", "scenario"), d)
out("compiled to %s" % d)
out(sorted(os.listdir(d)))

for name in sorted(os.listdir(d)):
    if name.endswith(".json") and "map" in name:
        out("--- %s" % name)

p = os.path.join(d, "map1-saltwell.json")
if os.path.exists(p):
    m = json.load(open(p))
    out("keys: %s" % sorted(m.keys()))
    out("size %s" % m.get("size"))
    cells = m.get("cells", {})
    out("cell keys: %s" % sorted(cells.keys()))
    for key in ("tiles", "image", "actionClass", "action"):
        col = cells.get(key)
        if col is None:
            continue
        out("%s row20: %s" % (key, col[20]))
        out("%s row20 x0..8: %s" % (key, col[20][:9]))
    out("info: %s" % json.dumps(m.get("info")))

out("=== maps.is_passable ===")
import inspect  # noqa: E402
import wlengine.maps as maps  # noqa: E402
out(inspect.getsource(maps.is_passable))
out(inspect.getsource(maps.apply_tail))
out(inspect.getsource(maps.record_at))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
