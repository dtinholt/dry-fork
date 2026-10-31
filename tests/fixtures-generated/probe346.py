"""Probe: inspect map cells around the cells the two failing tests name."""
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))

import wlengine.scenario as S  # noqa: E402
import wlengine.maps as M  # noqa: E402


def find_dirs():
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for d in glob.glob(os.path.join(here, "*")):
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "GAME1")):
            out.append(d)
    return out


def main():
    for d in find_dirs():
        try:
            sc = S.load(d)
        except Exception as e:  # noqa: BLE001
            print("load failed:", d, e)
            continue
        print("=== ", d)
        for loc in (0, 1):
            m = sc.map(loc)
            cells = m["cells"]
            img = cells["image"]
            cls = cells["actionClass"]
            act = cells["action"]
            print("  loc", loc, "size", m["size"], "border", m["info"].get("borderImage"))
            for (x, y) in [(14, 20), (2, 20), (3, 20), (15, 20), (4, 20), (5, 20)]:
                print("    cell(%d,%d): img[y][x]=%s cls[y][x]=%s act=%s | img[x][y]=%s cls[x][y]=%s" % (
                    x, y, img[y][x], cls[y][x], act[y][x], img[x][y], cls[x][y]))
            print("    passable(2,20)=%s passable(3,20)=%s passable(4,20)=%s" % (
                M.is_passable(m, 2, 20), M.is_passable(m, 3, 20), M.is_passable(m, 4, 20)))


main()
