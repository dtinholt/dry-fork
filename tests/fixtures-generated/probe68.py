"""Summarise the reference walkthrough log: event types and interesting runs.

Run: python3 tests/fixtures-generated/probe68.py [type]
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")
ev = json.load(open(LOG))["events"]

WHAT = sys.argv[1] if len(sys.argv) > 1 else "types"

if WHAT == "types":
    c = Counter(e.get("type") for e in ev)
    for k, v in sorted(c.items()):
        print("%-20s %d" % (k, v))
elif WHAT == "grep":
    pat = sys.argv[2]
    for i, e in enumerate(ev):
        if pat in json.dumps(e):
            print("%4d %s" % (i, json.dumps(e)))
elif WHAT == "range":
    a, b = int(sys.argv[2]), int(sys.argv[3])
    for i in range(a, min(b, len(ev))):
        print("%4d %s" % (i, json.dumps(ev[i])))
elif WHAT == "checkpoints":
    for i, e in enumerate(ev):
        if e.get("type") == "checkpoint":
            print("%4d %s" % (i, json.dumps(e)[:400]))
