"""probe359: is the reference walkthrough log consistent with the map SHIFTED
left by one column (cell (x,y) = JSON[y][x+1])?  That is the reading the two
failing tests (M5 bump, M6 look) were authored against.

Run: python3 tests/fixtures-generated/probe359.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")
NAMES = ["overworld", "saltwell", "ninemile", "pumphouse"]
MAPS = {loc: json.load(open(os.path.join(SC, "map%d-%s.json" % (loc, n))))
        for loc, n in enumerate(NAMES)}

log = json.load(open(os.path.join(SC, "walkthrough-reference-log.json")))["events"]


def cell(loc, x, y, shift):
    d = MAPS[loc]
    jx = x + shift
    if not (0 <= jx < d["width"] and 0 <= y < d["height"]):
        return None
    return d["tiles"][y][jx], d["action_class"][y][jx], d["action_value"][y][jx]


for shift in (0, 1):
    bad = []
    loc = 1
    for e in log:
        if e.get("type") == "checkpoint":
            loc = e["state"]["location"]
        if e.get("type") == "move":
            c = cell(e["location"], e["x"], e["y"], shift)
            if c is None:
                bad.append((e["seq"], "move off map", e["location"], e["x"], e["y"]))
            elif c[1] == 11:
                bad.append((e["seq"], "move onto class 11", e["location"], e["x"], e["y"], c))
        if e.get("type") == "bump":
            c = cell(loc, e["x"], e["y"], shift)
            if c is None or c[1] != e.get("action_class"):
                bad.append((e["seq"], "bump class mismatch", loc, e["x"], e["y"], c, e.get("action_class")))
    print("shift=%d: %d inconsistencies" % (shift, len(bad)))
    for b in bad[:12]:
        print("   ", b)

# where do the shop events happen?
print()
print("log events 95..135:")
for i, e in enumerate(log[95:135], start=95):
    print("  ", i, e)
