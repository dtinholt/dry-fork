"""Check the reference log for the cactus cell and count walls."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

log = json.load(open(os.path.join(ROOT, "SPEC/scenario/walkthrough-reference-log.json")))
evs = log["events"] if isinstance(log, dict) else log
print("first 20 events:")
for e in evs[:20]:
    print("  ", json.dumps(e)[:200])
print("events touching x=2 or 3 at y=20:")
for e in evs:
    if e.get("y") == 20 and e.get("x") in (2, 3):
        print("  ", json.dumps(e)[:200])
print("all bump events:")
for e in evs:
    if e.get("type") == "bump":
        print("  ", json.dumps(e))

m = json.load(open(os.path.join(ROOT, "SPEC/scenario/map1-saltwell.json")))
walls = sum(1 for row in m["tiles"] for v in row if v == 25)
print("wall tiles (25):", walls)
from collections import Counter
print(Counter(v for row in m["tiles"] for v in row))
