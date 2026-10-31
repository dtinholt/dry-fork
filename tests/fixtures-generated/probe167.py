"""Probe 167: map 1 row 20 cells and records around the cactus.

Run: python3 tests/fixtures-generated/probe167.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
SPEC = os.path.join(ROOT, "SPEC")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)

OUT = HERE


def main():
    import wlengine.scenario as sc
    import wlengine.maps as maps
    d = tempfile.mkdtemp(prefix="probe167-")
    sc.compile(os.path.join(SPEC, "scenario"), d)
    s = sc.Scenario(d)
    m = s.map(1)
    print("size", m["size"])
    for y in (19, 20, 21):
        row = []
        for x in range(0, 8):
            row.append("%d/%d" % (m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x]))
        print("y=%d" % y, row)
    for x in range(0, 6):
        rec = maps.record_at(m, x, 20)
        print("rec(%d,20)" % x, json.dumps(rec, default=str)[:300])
    print("passable(2,20)", maps.is_passable(m, 2, 20))
    print("passable(3,20)", maps.is_passable(m, 3, 20))


if __name__ == "__main__":
    main()
