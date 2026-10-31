"""Probe: inspect map tiles/classes around the cells the two failing tests name.

M5 test_bump_is_not_a_step expects cell (2,20) blocked class 11 and (3,20)
walkable.  M6 test_look expects cell (14,20) image 28 class 0.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))

import wlengine.scenario as S  # noqa: E402


def find_dirs():
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for d in glob.glob(os.path.join(here, "*")):
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "GAME1")):
            out.append(d)
    return out


def main():
    dirs = find_dirs()
    print("candidate data dirs:", dirs)
    for d in dirs:
        try:
            sc = S.load(d)
        except Exception as e:  # noqa: BLE001
            print("  load failed:", d, e)
            continue
        print("=== ", d)
        for loc in (0, 1):
            try:
                m = sc.map(loc)
            except Exception as e:  # noqa: BLE001
                print("  map", loc, "failed", e)
                continue
            tiles = m.get("tiles")
            cls = m.get("action_class")
            print("  loc", loc, "dims", m.get("width"), m.get("height"),
                  "tiles type", type(tiles).__name__)
            if tiles is None:
                print("   keys:", sorted(m.keys()))
                continue
            for (x, y) in [(14, 20), (20, 14), (2, 20), (20, 2), (3, 20), (20, 3),
                           (15, 20), (20, 15)]:
                try:
                    t = tiles[y][x]
                except Exception as e:  # noqa: BLE001
                    t = "ERR %s" % e
                try:
                    c = cls[y][x]
                except Exception as e:  # noqa: BLE001
                    c = "ERR %s" % e
                print("    cell(x=%d,y=%d) tile=%s class=%s  [tiles[x][y]=%s]" % (
                    x, y, t, c,
                    (tiles[x][y] if isinstance(tiles, list) and x < len(tiles)
                     and isinstance(tiles[x], list) and y < len(tiles[x]) else "?")))


main()
