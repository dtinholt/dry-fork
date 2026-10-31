"""Dump the reference walkthrough log around the raider fight (SPEC-05 6).

Run: python3 tests/fixtures-generated/probe65.py [start] [count]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")

d = json.load(open(LOG))
ev = d["events"]
print("note:", d.get("note"))
print("total events:", len(ev))

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
count = int(sys.argv[2]) if len(sys.argv) > 2 else 40

if start == 0:
    # find the encounter_start
    for i, e in enumerate(ev):
        if e.get("type") == "encounter_start":
            print("encounter_start at index", i)
            start = i - 6
            break

for i in range(max(0, start), min(len(ev), start + count)):
    print("%4d %s" % (i, json.dumps(ev[i])))
