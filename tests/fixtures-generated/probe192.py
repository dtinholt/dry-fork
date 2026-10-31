"""Probe 192: reference fight events, map0 cells, map1 arrays, reference bumps."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump192.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


SC = os.path.join(ROOT, "SPEC", "scenario")
log = json.load(open(os.path.join(SC, "walkthrough-reference-log.json"), encoding="utf-8"))
evs = log["events"]

p("=" * 70)
p("REFERENCE LOG: bumps")
for i, e in enumerate(evs):
    if e.get("type") == "bump":
        p("%4d %s" % (i, json.dumps(e, sort_keys=True)))

p("=" * 70)
p("REFERENCE LOG: fight window")
start = next(i for i, e in enumerate(evs) if e.get("type") == "encounter_start")
end = next(i for i in range(start, len(evs)) if evs[i].get("type") == "checkpoint" and evs[i].get("name") == "CP4")
for i in range(start, end + 1):
    e = evs[i]
    if e.get("type") == "checkpoint":
        p("%4d checkpoint %s" % (i, e.get("name")))
    else:
        p("%4d %s" % (i, json.dumps(e, sort_keys=True)[:400]))

p("=" * 70)
p("REFERENCE LOG: cell_change events")
for i, e in enumerate(evs):
    if e.get("type") == "cell_change":
        p("%4d %s" % (i, json.dumps(e, sort_keys=True)))

p("=" * 70)
p("REFERENCE LOG: save/load events")
for i, e in enumerate(evs):
    if e.get("type") in ("save", "load"):
        p("%4d %s" % (i, json.dumps(e, sort_keys=True)))

m0 = json.load(open(os.path.join(SC, "map0-overworld.json"), encoding="utf-8"))
p("=" * 70)
p("map0 keys: %r" % list(m0))
p("map0 action_cells: %s" % json.dumps(m0["action_cells"], sort_keys=True)[:3000])
p("map0 records: %s" % json.dumps(m0["records"], sort_keys=True)[:3000])
for y in (40, 41, 42):
    p("map0 tiles[%d] = %r" % (y, m0["tiles"][y]))
    p("map0 action_class[%d] = %r" % (y, m0["action_class"][y]))
    p("map0 action_value[%d] = %r" % (y, m0["action_value"][y]))

m1 = json.load(open(os.path.join(SC, "map1-saltwell.json"), encoding="utf-8"))
p("=" * 70)
p("map1 known action cells check")
for c in m1["action_cells"]:
    x, y = c["x"], c["y"]
    p("cell (%d,%d): json tile %r class %r | tiles[%d][%d]=%r action_class[%d][%d]=%r"
      % (x, y, c["tile"], c["class"], y, x, m1["tiles"][y][x], y, x, m1["action_class"][y][x]))
p("map1 tiles[11] = %r" % m1["tiles"][11])
p("map1 action_class[11] = %r" % m1["action_class"][11])
p("map1 tiles[17] = %r" % m1["tiles"][17])
p("map1 action_class[17] = %r" % m1["action_class"][17])
p("map1 tiles[31] = %r" % m1["tiles"][31])
p("map1 action_class[31] = %r" % m1["action_class"][31])
p("map1 tiles[5] = %r" % m1["tiles"][5])
p("map1 action_class[5] = %r" % m1["action_class"][5])

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
