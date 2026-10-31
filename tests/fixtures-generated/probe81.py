"""Investigate the cactus cell (2,20) vs (3,20)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

m = json.load(open(os.path.join(ROOT, "SPEC/scenario/map1-saltwell.json")))
for y in (19, 20, 21):
    print("json tiles y=%d" % y, [(x, v) for x, v in enumerate(m["tiles"][y]) if v])
    print("json ac    y=%d" % y, [(x, v) for x, v in enumerate(m["action_class"][y]) if v])

spec = open(os.path.join(ROOT, "SPEC/SPEC-05-scenario.md"), encoding="utf-8").read().splitlines()
for i, l in enumerate(spec):
    if l.strip().startswith("20  |") or l.strip().startswith("11  |") or l.strip().startswith("31  |"):
        row = l.strip().split("|", 1)[1]
        row = "|" + row
        print("spec row", repr(l))
        print("   indices", [(x, c) for x, c in enumerate(row) if c not in ".|"])

log = json.load(open(os.path.join(ROOT, "SPEC/scenario/walkthrough-reference-log.json")))
evs = log["events"] if isinstance(log, dict) else log
print("ref log events", len(evs))
for e in evs:
    if e.get("type") == "bump":
        print("ref bump", json.dumps(e))
