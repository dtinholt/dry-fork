"""probe333: confirm the orientation of the compiled map for location 1.

Prints, for the frozen JSON and for the compiled data directory (if one can be
found under tests/fixtures-generated), the tile/image and action class at the
cells the M5 bump test and the M6 look test care about:

  (2,20), (3,20), (4,20)  -- the M5 bump test
  (14,20)                 -- the M6 look test

Also prints the transposed readings (tiles[x][y]) so the two hypotheses can be
told apart at a glance.  Read-only.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

SPEC = os.path.join(ROOT, "SPEC", "scenario")


def main():
    m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
    tiles, ac = m["tiles"], m["action_class"]
    print("JSON map1-saltwell.json")
    for (x, y) in [(2, 20), (3, 20), (4, 20), (14, 20)]:
        print("  (x=%d,y=%d) tiles[y][x]=%d image=%d ac[y][x]=%d | tiles[x][y]=%d ac[x][y]=%d"
              % (x, y, tiles[y][x], tiles[y][x] + 10, ac[y][x], tiles[x][y], ac[x][y]))
    print("  row 20 tiles[20][0:8] =", tiles[20][:8])
    print("  row 20 ac[20][0:8]    =", ac[20][:8])

    # find a compiled data dir
    cands = []
    for name in sorted(os.listdir(os.path.join(ROOT, "tests", "fixtures-generated"))):
        p = os.path.join(ROOT, "tests", "fixtures-generated", name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "LABTABLES.BIN")):
            cands.append(p)
    print("compiled candidates:", cands[:5])
    if not cands:
        return
    from wlengine import scenario as sc_mod
    sc = sc_mod.load(cands[0])
    mm = sc.map(1)
    cells = mm["cells"]
    print("compiled dir:", cands[0])
    for (x, y) in [(2, 20), (3, 20), (4, 20), (14, 20)]:
        print("  (x=%d,y=%d) image[y][x]=%s ac[y][x]=%s | image[x][y]=%s ac[x][y]=%s"
              % (x, y, cells["image"][y][x], cells["actionClass"][y][x],
                 cells["image"][x][y], cells["actionClass"][x][y]))
    print("  row 20 image[20][0:8] =", cells["image"][20][:8])
    print("  row 20 ac[20][0:8]    =", cells["actionClass"][20][:8])


if __name__ == "__main__":
    main()
