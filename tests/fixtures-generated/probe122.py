"""Probe 122: compare our compiled map images with the reference log's cell_change images."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    from wlengine import scenario, maps
    d = tempfile.mkdtemp(prefix="probe122-")
    scenario.compile(SCEN, d)
    sc = scenario.load(d)
    for loc, cells in [(0, [(30, 41), (31, 41), (26, 41)]),
                       (2, [(26, 14), (26, 12), (25, 5)]),
                       (3, [(16, 6), (17, 6)])]:
        m = sc.map(loc)
        print("location", loc, "size", m["size"])
        for (x, y) in cells:
            print("   (%d,%d) image=%r class=%r action=%r" % (
                x, y, maps.image_at(m, x, y),
                m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x]))
            rec = maps.record_at(m, x, y)
            print("      record:", rec)
    # JSON tiles for comparison
    for name, cells in [("map0-overworld", [(30, 41), (31, 41)]),
                        ("map2-ninemile", [(26, 14), (26, 12)]),
                        ("map3-pumphouse", [(16, 6), (17, 6)])]:
        j = json.load(open(os.path.join(SCEN, name + ".json")))
        print(name)
        for (x, y) in cells:
            print("   (%d,%d) json tile=%r" % (x, y, j["tiles"][y][x]))


if __name__ == "__main__":
    main()
