"""Probe 152: compile the scenario, run the bump script, dump events and the
map cells around (2,20) on location 1.

Run: python3 tests/fixtures-generated/probe152.py
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

SEED = 20261021


def main():
    import wl_support as W
    from wlengine import scenario as scen
    from wlengine import headless, maps

    d = tempfile.mkdtemp(prefix="probe152-")
    scen.compile(str(W.SCENARIO), d)
    print("compiled to", d)
    print("files:", sorted(os.listdir(d)))

    script = {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}
    ev = headless.run(d, json.loads(json.dumps(script)), SEED)
    for i, e in enumerate(ev):
        print("%3d %s" % (i, json.dumps(e, sort_keys=True)))

    sc = scen.Scenario(d)
    m = sc.map(1)
    cells = m["cells"]
    print("map 1 size", m["size"])
    for y in range(18, 23):
        row = []
        for x in range(0, 10):
            row.append("%d/%d/%d" % (cells["actionClass"][y][x],
                                     cells["action"][y][x],
                                     cells["image"][y][x]))
        print("y=%2d " % y, " ".join(row))
    print("records row 20:")
    for x in range(0, 8):
        rec = maps.record_at(m, x, 20)
        print("  x=%d cls=%d act=%d passable=%s rec=%r" % (
            x, cells["actionClass"][20][x], cells["action"][20][x],
            maps.is_passable(m, x, 20), rec))


if __name__ == "__main__":
    main()
