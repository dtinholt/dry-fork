"""Compare the scenario JSON action_class grid with the SPEC-05 drawing."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SC = os.path.join(ROOT, "SPEC", "scenario")


def main():
    d = json.load(open(os.path.join(SC, "map1-saltwell.json")))
    ac = d["action_class"]
    av = d["action_value"]
    print("width", d["width"], "height", d["height"])
    print("ac dims", len(ac), len(ac[0]))
    for y in range(0, 32):
        row = "".join("%X" % (ac[y][x] & 0xF) for x in range(0, 32))
        print("%2d %s" % (y, row))
    print()
    print("transposed check: ac[x][y]")
    for y in range(0, 32):
        row = "".join("%X" % (ac[x][y] & 0xF) for x in range(0, 32))
        print("%2d %s" % (y, row))
    print()
    for (x, y) in [(2, 20), (8, 17), (15, 11), (13, 6), (23, 11), (25, 21), (16, 6), (26, 14)]:
        print("(%d,%d) ac[y][x]=%d ac[x][y]=%d av[y][x]=%d" % (x, y, ac[y][x], ac[x][y], av[y][x]))


if __name__ == "__main__":
    main()
