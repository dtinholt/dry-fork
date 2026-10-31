"""probe444: inspect the reference log for look/bump events and the walkthrough
script, to see which coordinates the reference implementation used."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")

log = json.load(open(os.path.join(SPEC, "scenario", "walkthrough-reference-log.json"), encoding="utf-8"))
print("log keys:", sorted(log.keys()))
ev = log["events"]
print("events:", len(ev))
types = {}
for e in ev:
    types[e.get("type")] = types.get(e.get("type"), 0) + 1
print("types:", types)

for i, e in enumerate(ev):
    if e.get("type") in ("look", "bump"):
        print(i, json.dumps(e, sort_keys=True))

wt = json.load(open(os.path.join(SPEC, "scenario", "walkthrough.json"), encoding="utf-8"))
print("walkthrough keys:", sorted(wt.keys()))
print(json.dumps(wt, indent=1)[:3000])
