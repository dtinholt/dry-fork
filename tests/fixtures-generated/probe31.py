"""Probe 31: test [y][x] vs [x][y] for action_class/action_value/tiles against
the reference log's bump and cell_change events."""
from __future__ import annotations

import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SCEN = PROJECT / "SPEC" / "scenario"

ref = json.load(open(SCEN / "walkthrough-reference-log.json"))["events"]

maps = {}
for loc, f in ((0, "map0-overworld.json"), (1, "map1-saltwell.json"),
               (2, "map2-ninemile.json"), (3, "map3-pumphouse.json")):
    maps[loc] = json.load(open(SCEN / f))

print("== bumps ==")
for e in ref:
    if e.get("type") != "bump":
        continue
    x, y = e["x"], e["y"]
    print("bump (%d,%d) class %d action %d" % (x, y, e["action_class"], e["action"]))
    for loc, m in maps.items():
        ac, av = m["action_class"], m["action_value"]
        yx = (ac[y][x], av[y][x])
        xy = (ac[x][y], av[x][y])
        if yx == (e["action_class"], e["action"]) or xy == (e["action_class"], e["action"]):
            print("   loc %d: [y][x]=%r [x][y]=%r" % (loc, yx, xy))

print()
print("== cell_change images ==")
for e in ref:
    if e.get("type") != "cell_change":
        continue
    loc, x, y = e["location"], e["x"], e["y"]
    m = maps[loc]
    t = m["tiles"]
    print("cell_change loc %d (%d,%d) image %d -> tile %d; json tiles[y][x]=%d tiles[x][y]=%d"
          % (loc, x, y, e["image"], e["image"] - 10, t[y][x], t[x][y]))

print()
print("== saltwell row 20 / col 20 ==")
m = maps[1]
print("ac[20] =", m["action_class"][20])
print("ac[2]  =", m["action_class"][2])
print("ac[20][2] =", m["action_class"][20][2], " ac[2][20] =", m["action_class"][2][20])
print("tiles[20] =", m["tiles"][20])
print("tiles[2]  =", m["tiles"][2])
print("tiles[20][2] =", m["tiles"][20][2], " tiles[2][20] =", m["tiles"][2][20])
