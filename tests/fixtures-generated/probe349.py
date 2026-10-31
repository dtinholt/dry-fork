"""Probe: does the reference log discriminate between tiles[y][x] and tiles[x][y]?"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "..", "SPEC", "scenario")

ref = json.load(open(os.path.join(SPEC, "walkthrough-reference-log.json")))["events"]
maps = {}
for loc, fn in [(0, "map0-overworld.json"), (1, "map1-saltwell.json"),
                (2, "map2-ninemile.json"), (3, "map3-pumphouse.json")]:
    maps[loc] = json.load(open(os.path.join(SPEC, fn)))

BLOCKED = {11}


def passable(m, x, y, transposed):
    if not (0 <= x < m["width"] and 0 <= y < m["height"]):
        return False
    if transposed:
        t, c = m["tiles"][x][y], m["action_class"][x][y]
    else:
        t, c = m["tiles"][y][x], m["action_class"][y][x]
    if c == 11:
        return False
    if c == 4:
        # impassable mask: look up the record
        av = m["action_value"][y][x] if not transposed else m["action_value"][x][y]
        recs = m["records"].get("4") or []
        if av and av - 1 < len(recs):
            return not recs[av - 1].get("impassable")
        return True
    return True


diff = 0
for e in ref:
    if e["type"] != "move":
        continue
    loc, x, y = e["location"], e["x"], e["y"]
    m = maps[loc]
    a = passable(m, x, y, False)
    b = passable(m, x, y, True)
    if a != b:
        diff += 1
        print("MOVE discriminates: loc %d (%d,%d) nontrans=%s trans=%s" % (loc, x, y, a, b))
print("moves that discriminate:", diff)

# also check the bump targets
for e in ref:
    if e["type"] != "bump":
        continue
    loc = None
    for prev in ref:
        if prev is e:
            break
    print("bump", e["x"], e["y"], e["action_class"], e["action"])
