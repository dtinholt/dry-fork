"""Probe 428: reference-log events around the NPC bump and the cactus bump."""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")))
ev = d["events"]
for lo, hi in ((115, 135), (590, 610), (795, 815)):
    print("=== events %d..%d ===" % (lo, hi))
    for e in ev[lo:hi]:
        print(json.dumps(e)[:220])
