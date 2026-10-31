"""Probe 212: dump the engine's Saltwell map row 20 via the scenario object."""
import inspect
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump212.txt")
buf = []


def out(s=""):
    buf.append(str(s))


import wlengine.scenario as sc  # noqa: E402

d = tempfile.mkdtemp(prefix="probe212")
sc.compile(os.path.join(ROOT, "SPEC", "scenario"), d)

out("=== scenario.py: map / load ===")
src = inspect.getsource(sc)
for name in ("def map", "def load", "class Scenario", "def __init__"):
    i = src.find(name)
    if i >= 0:
        out(src[i:i + 1500])
        out("---")

try:
    s = sc.load(d)
except Exception as e:
    out("load failed: %r" % (e,))
    s = None

if s is not None:
    m = s.map(1)
    out("map1 keys %s" % sorted(m.keys()))
    out("size %s" % m.get("size"))
    cells = m["cells"]
    for key in sorted(cells.keys()):
        out("%s row20: %s" % (key, cells[key][20]))
    out("info %s" % m.get("info"))
    out("actions keys %s" % sorted(m.get("actions", {}).keys()))
    for cls in sorted(m.get("actions", {})):
        tbl = m["actions"][cls]
        out("class %s: %d records" % (cls, len(tbl)))
        for i, r in enumerate(tbl):
            out("   [%d] %s" % (i, r))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
