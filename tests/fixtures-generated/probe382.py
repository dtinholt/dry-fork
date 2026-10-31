"""Probe 382: which index convention does the reference log use?

For every consecutive move in SPEC/scenario/walkthrough-reference-log.json,
check whether the target cell is walkable under [y][x] and under [x][y].
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REF = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def load_map(loc):
    name = {0: "map0-overworld.json", 1: "map1-saltwell.json",
            2: "map2-ninemile.json", 3: "map3-pumphouse.json"}[loc]
    return json.load(open(os.path.join(SCEN, name)))


def main():
    ev = json.load(open(REF))["events"]
    maps = {loc: load_map(loc) for loc in (0, 1, 2, 3)}
    moves = [e for e in ev if e.get("type") == "move"]
    bad_yx = []
    bad_xy = []
    for e in moves:
        loc, x, y = e["location"], e["x"], e["y"]
        m = maps[loc]
        c = m["action_class"]
        t = m["tiles"]
        cyx = c[y][x]
        cxy = c[x][y]
        if cyx == 11:
            bad_yx.append((loc, x, y, cyx, cxy))
        if cxy == 11:
            bad_xy.append((loc, x, y, cyx, cxy))
    print("moves:", len(moves))
    print("blocked under [y][x]:", len(bad_yx), bad_yx[:10])
    print("blocked under [x][y]:", len(bad_xy), bad_xy[:10])
    # bumps: the bumped cell must be blocked
    for e in ev:
        if e.get("type") == "bump":
            loc = e.get("location", 1)
            x, y = e["x"], e["y"]
            m = maps[loc]
            print("bump", loc, x, y, "cls[y][x]=", m["action_class"][y][x],
                  "cls[x][y]=", m["action_class"][x][y],
                  "tile[y][x]=", m["tiles"][y][x], "tile[x][y]=", m["tiles"][x][y])
    # look events
    looks = [e for e in ev if e.get("type") == "look"]
    print("looks:", len(looks))
    for e in looks[:5]:
        print(json.dumps(e, sort_keys=True))


main()
