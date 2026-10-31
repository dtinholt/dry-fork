"""probe354: which reading of the map arrays is consistent with the reference
walkthrough log?  Replay the log's moves and check passability under [y][x]
and under [x][y].

Run: python3 tests/fixtures-generated/probe354.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")

MAPS = {}
for loc, name in enumerate(["overworld", "saltwell", "ninemile", "pumphouse"]):
    MAPS[loc] = json.load(open(os.path.join(SC, "map%d-%s.json" % (loc, name))))

log = json.load(open(os.path.join(SC, "walkthrough-reference-log.json")))["events"]

# passability: class 11 blocked, class 4 impassable blocked, tile 0..? treat
# tile 0 (sand) as passable; walls are class 11 anyway.  Use the class arrays.
def cls_yx(loc, x, y):
    d = MAPS[loc]
    return d["action_class"][y][x]

def cls_xy(loc, x, y):
    d = MAPS[loc]
    return d["action_class"][x][y]

bad_yx = []
bad_xy = []
pos = None
for e in log:
    if e.get("type") == "checkpoint":
        st = e["state"]
        pos = (st["location"], st["x"], st["y"])
    if e.get("type") == "move":
        loc, x, y = e["location"], e["x"], e["y"]
        if cls_yx(loc, x, y) == 11:
            bad_yx.append((e["seq"], loc, x, y, "class11"))
        if cls_xy(loc, x, y) == 11:
            bad_xy.append((e["seq"], loc, x, y, "class11"))
    if e.get("type") == "bump":
        loc = pos[0] if pos else 1
        x, y = e["x"], e["y"]
        if cls_yx(loc, x, y) != e.get("action_class"):
            bad_yx.append((e["seq"], loc, x, y, "bump class %s vs %s" % (cls_yx(loc, x, y), e.get("action_class"))))
        if cls_xy(loc, x, y) != e.get("action_class"):
            bad_xy.append((e["seq"], loc, x, y, "bump class %s vs %s" % (cls_xy(loc, x, y), e.get("action_class"))))

print("moves/bumps inconsistent with [y][x]:", len(bad_yx))
for b in bad_yx[:20]:
    print("   ", b)
print("moves/bumps inconsistent with [x][y]:", len(bad_xy))
for b in bad_xy[:20]:
    print("   ", b)

print()
print("checkpoints:")
for e in log:
    if e.get("type") == "checkpoint":
        st = e["state"]
        print("  ", e["name"], st["location"], st["x"], st["y"], "steps", st["steps"])
