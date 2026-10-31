"""Probe 156: full class-11 cell list for map1 (Saltwell) from the JSON and
from the compiled map, plus the SPEC-05 Saltwell description.

Run: python3 tests/fixtures-generated/probe156.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    import wl_support as W
    from wlengine import scenario as scen

    m = W.load_json(W.SCENARIO / "map1-saltwell.json")
    ac = m["action_class"]
    av = m["action_value"]
    tiles = m["tiles"]
    print("class-11 cells in JSON (y, x, action_value, tile):")
    for y in range(len(ac)):
        for x in range(len(ac[y])):
            if ac[y][x] == 11:
                print("   y=%d x=%d av=%d tile=%d" % (y, x, av[y][x], tiles[y][x]))
    print("row 20 full:", ac[20])
    print("row 19 full:", ac[19])
    print("row 21 full:", ac[21])
    print("col 2:", [ac[y][2] for y in range(32)])
    print("col 3:", [ac[y][3] for y in range(32)])

    d = tempfile.mkdtemp(prefix="probe156-")
    scen.compile(str(W.SCENARIO), d)
    sc = scen.Scenario(d)
    cm = sc.map(1)
    cells = cm["cells"]
    print("compiled class-11 cells:")
    for y in range(cm["size"]):
        for x in range(cm["size"]):
            if cells["actionClass"][y][x] == 11:
                print("   y=%d x=%d act=%d img=%d" % (y, x, cells["action"][y][x], cells["image"][y][x]))

    # SPEC-05 Saltwell text
    spec = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
    with open(spec, encoding="utf-8") as fh:
        lines = fh.readlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("### 5.2 Saltwell"):
            start = i
        elif start is not None and ln.startswith("### 5.3"):
            end = i
            break
    else:
        end = start + 200
    for i in range(start, end):
        sys.stdout.write("%4d| %s" % (i + 1, lines[i]))


if __name__ == "__main__":
    main()
