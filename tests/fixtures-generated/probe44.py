"""Probe 44: figure out the indexing convention of the map JSON arrays.

For each known bump cell from the reference log, print the JSON value under
both indexings ([y][x] and [x][y]) and the value in the compiled GAME1 map.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"

KNOWN = [(1, 8, 17, 11, 1), (2, 26, 14, 4, 2), (2, 18, 17, 11, 1),
         (2, 25, 21, 11, 0), (3, 16, 6, 4, 5), (1, 15, 11, 11, 0),
         (1, 2, 20, 11, 0)]

FILES = {1: "map1-saltwell.json", 2: "map2-ninemile.json", 3: "map3-pumphouse.json",
         0: "map0-overworld.json"}


def main():
    for loc, x, y, cls, act in KNOWN:
        d = json.loads((SCEN / FILES[loc]).read_text())
        ac = d["action_class"]
        av = d["action_value"]
        tl = d["tiles"]
        print("loc %d cell (%d,%d) want class %d action %d" % (loc, x, y, cls, act))
        print("   [y][x]: class %r action %r tile %r" % (ac[y][x], av[y][x], tl[y][x]))
        print("   [x][y]: class %r action %r tile %r" % (ac[x][y], av[x][y], tl[x][y]))
        print("   width/height %r %r" % (d.get("width"), d.get("height")))
    # Saltwell row 20 and column 20
    d = json.loads((SCEN / FILES[1]).read_text())
    print("saltwell action_class[20] =", d["action_class"][20])
    print("saltwell tiles[20]        =", d["tiles"][20])
    print("saltwell col20 class      =", [d["action_class"][r][20] for r in range(32)])
    print("saltwell col20 tiles      =", [d["tiles"][r][20] for r in range(32)])
    print("saltwell col2 class       =", [d["action_class"][r][2] for r in range(32)])
    print("saltwell col3 class       =", [d["action_class"][r][3] for r in range(32)])
    print("saltwell col2 tiles       =", [d["tiles"][r][2] for r in range(32)])
    print("saltwell col3 tiles       =", [d["tiles"][r][3] for r in range(32)])
    print("saltwell row20 tiles      =", d["tiles"][20])
    print("saltwell row20 class      =", d["action_class"][20])


if __name__ == "__main__":
    main()
