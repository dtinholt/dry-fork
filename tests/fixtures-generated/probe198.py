"""Probe 198: the cactus cell, the (31,41) cell change, LABSTATE dedup."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump198.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


SC = os.path.join(ROOT, "SPEC", "scenario")

# 1. the SPEC-05 art rows
spec = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md"), encoding="utf-8").read()
for line in spec.splitlines():
    s = line.strip()
    if s.startswith("20  |") or s.startswith("11  |") or s.startswith("12  |") or s.startswith("31  |"):
        body = s.split("|", 1)[1]
        p("ART %r" % s)
        p("   len=%d" % len(body))
        p("   Y at %r" % [i for i, c in enumerate(body) if c == "Y"])
        p("   P at %r" % [i for i, c in enumerate(body) if c == "P"])
        p("   ; at %r" % [i for i, c in enumerate(body) if c == ";"])

# 2. map1 tiles/action_class rows
m1 = json.load(open(os.path.join(SC, "map1-saltwell.json"), encoding="utf-8"))
for y in (11, 12, 20, 21):
    p("map1 y=%d tiles=%r" % (y, m1["tiles"][y]))
    p("map1 y=%d class=%r" % (y, m1["action_class"][y]))

# 3. map0 cells around (30,41),(31,41)
m0 = json.load(open(os.path.join(SC, "map0-overworld.json"), encoding="utf-8"))
p("map0 action_cells near 41:")
for c in m0["action_cells"]:
    if c["y"] in (40, 41, 42):
        p("   %r" % c)
p("map0 records keys: %r" % list(m0["records"]))
for k, v in m0["records"].items():
    p("   records[%s] = %r" % (k, v))
p("map0 tiles y=41: %r" % m0["tiles"][41])
p("map0 class y=41: %r" % m0["action_class"][41])

# 4. reference log bump events
ref = json.load(open(os.path.join(SC, "walkthrough-reference-log.json"), encoding="utf-8"))["events"]
p("ref bump events: %r" % [e for e in ref if e.get("type") == "bump"])
p("ref cell_change events: %r" % [e for e in ref if e.get("type") == "cell_change"])
p("ref paragraph events: %r" % [(e.get("seq"), e.get("n")) for e in ref if e.get("type") == "paragraph"])

# 5. our engine: walkthrough to CP5-pre-save, then check (31,41)
from wlengine import scenario as scmod  # noqa: E402
from wlengine import headless as hl  # noqa: E402

wt = json.load(open(os.path.join(SC, "walkthrough.json"), encoding="utf-8"))
script = wt["script"]
idx = next(i for i, it in enumerate(script) if isinstance(it, dict) and it.get("checkpoint") == "CP5-pre-save")
d = tempfile.mkdtemp()
scmod.compile(SC, d)
ev = hl.run(d, {"seed": 20261021, "script": script[:idx + 1]}, 20261021)
p("our events between CP4 and CP5-pre-save:")
seen = False
for e in ev:
    if e.get("type") == "checkpoint" and e.get("name") == "CP4":
        seen = True
    if seen:
        p("   " + json.dumps({k: v for k, v in e.items() if k != "state"}, sort_keys=True)[:200])

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
