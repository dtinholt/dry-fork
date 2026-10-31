"""Probe 284: where does the reference log put the cactus bump?"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC", "scenario")

ref = json.load(open(os.path.join(SPEC, "walkthrough-reference-log.json")))
ev = ref["events"]
print("n events", len(ev))
for e in ev:
    if e.get("type") == "bump":
        print(e)

# Also the walkthrough step list.
wt = json.load(open(os.path.join(SPEC, "walkthrough.json")))
print("walkthrough keys:", sorted(wt.keys()))
print(json.dumps(wt, indent=1)[:3000])
