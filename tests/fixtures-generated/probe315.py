"""Probe 315: for every map, print image at (14,20) and (15,20) in both index
orders, to see whether any map makes the look test's expectation consistent.

Run: python3 tests/fixtures-generated/probe315.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "src"))

from wlengine import headless, scenario  # noqa: E402

SCEN = os.path.join(PROJ, "SPEC", "scenario")


def main():
    dd = tempfile.mkdtemp(prefix="probe315-")
    scenario.compile(SCEN, dd)
    sc = headless._load_scenario(dd)
    for loc in sorted(sc.maps):
        m = sc.maps[loc]
        img = m["cells"]["image"]
        ac = m["cells"]["actionClass"]
        print("map %d: image[20][14]=%d image[14][20]=%d image[20][15]=%d image[15][20]=%d"
              % (loc, img[20][14], img[14][20], img[20][15], img[15][20]))
        print("        ac[20][14]=%d ac[14][20]=%d ac[20][15]=%d ac[15][20]=%d"
              % (ac[20][14], ac[14][20], ac[20][15], ac[15][20]))
        # any cell with image 28 at x=14?
        col = [(y, img[y][14]) for y in range(32) if img[y][14] == 28]
        print("        image 28 in column x=14 at y:", col)
    # JSON maps
    for name in sorted(os.listdir(SCEN)):
        if not name.startswith("map") or not name.endswith(".json"):
            continue
        j = json.load(open(os.path.join(SCEN, name)))
        t = j["tiles"]
        print("%s: tiles[20][14]=%d tiles[14][20]=%d tiles[20][15]=%d tiles[15][20]=%d"
              % (name, t[20][14], t[14][20], t[20][15], t[15][20]))


main()
