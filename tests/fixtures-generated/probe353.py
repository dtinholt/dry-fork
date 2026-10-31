"""probe353: compare the map cells the failing M5/M6 tests expect against the
scenario JSON and the reference log.

Run: python3 tests/fixtures-generated/probe353.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")


def load(name):
    with open(os.path.join(SC, name)) as f:
        return json.load(f)


for loc in (0, 1):
    d = load("map%d-%s.json" % (loc, ["overworld", "saltwell", "ninemile", "pumphouse"][loc]))
    t = d["tiles"]
    ac = d["action_class"]
    av = d["action_value"]
    print("=== map", loc, d["name"], "size", d["width"], d["height"])
    for (x, y) in [(14, 20), (15, 20), (2, 20), (3, 20), (4, 20), (20, 14), (14, 15), (20, 3)]:
        try:
            print("   (x=%d,y=%d) tile=%s class=%s action=%s" % (x, y, t[y][x], ac[y][x], av[y][x]))
        except Exception as e:
            print("   (x=%d,y=%d) failed %s" % (x, y, e))
    # transposed reading
    print("   transposed:")
    for (x, y) in [(14, 20), (2, 20), (3, 20)]:
        try:
            print("     [x=%d][y=%d] tile=%s class=%s" % (x, y, t[x][y], ac[x][y]))
        except Exception as e:
            print("     [x=%d][y=%d] failed %s" % (x, y, e))

sc = load("scenario.json")
print("=== scenario.json keys", list(sc))
print(json.dumps({k: v for k, v in sc.items() if k not in ("maps",)}, indent=1)[:3000])

log = load("walkthrough-reference-log.json")["events"]
print("=== reference log: look events")
for i, e in enumerate(log):
    if e.get("type") == "look":
        print("  ", i, e)
print("=== reference log: events with y==20 and x<8")
for i, e in enumerate(log):
    if e.get("y") == 20 and isinstance(e.get("x"), int) and e["x"] < 8:
        print("  ", i, e)
print("=== reference log: first 40 events")
for i, e in enumerate(log[:40]):
    print("  ", i, e)
