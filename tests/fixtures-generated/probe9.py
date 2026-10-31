"""Probe 9: test [y][x] vs [x][y] for map1-saltwell.json against the SPEC-05 table."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

TABLE = [(22, 4, 22, 11, 0), (6, 5, 17, 6, 1), (6, 7, 19, 1, 2), (23, 7, 19, 1, 3),
         (15, 11, 23, 11, 0), (13, 12, 18, 1, 4), (8, 17, 24, 11, 1), (15, 29, 18, 1, 1),
         (15, 31, 18, 10, 1), (16, 31, 18, 10, 2)]


def main():
    mj = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
    cls = mj["action_class"]
    act = mj["action_value"]
    tiles = mj["tiles"]
    print("shape cls:", len(cls), len(cls[0]))
    for (x, y, tile, c, a) in TABLE:
        print("cell (%2d,%2d) want tile %2d cls %2d act %d | [y][x]: tile %2d cls %2d act %d | [x][y]: tile %2d cls %2d act %d"
              % (x, y, tile, c, a,
                 tiles[y][x], cls[y][x], act[y][x],
                 tiles[x][y], cls[x][y], act[x][y]))
    print()
    print("row20 cls:", cls[20])
    print("row20 tiles:", tiles[20])
    print("col20 cls:", [cls[y][20] for y in range(32)])
    print("col20 tiles:", [tiles[y][20] for y in range(32)])
    print("row2 cls:", cls[2])
    print("row2 tiles:", tiles[2])
    print("action_cells:", json.dumps(mj["action_cells"]))


if __name__ == "__main__":
    main()
