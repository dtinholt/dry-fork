"""Probe the bump failure and the combat state (iter 62)."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

from wlengine import headless  # noqa: E402

DATA = os.path.join(HERE, "dd")

SEED = 20261021


def main():
    print("MRO:", [c.__name__ for c in headless.Engine.__mro__])
    eng = headless.Engine(DATA, seed=SEED, options={})
    eng.new_game(SEED)
    m = eng.sc.map(1)
    print("map1 size", m["size"])
    for y in range(18, 23):
        row = []
        for x in range(0, 8):
            row.append("%d/%d" % (m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x]))
        print("y=%d" % y, row)
    print("passable:", [maps_pass(eng, x, 20) for x in range(0, 8)])

    ev = headless.run(DATA, {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, SEED)
    for e in ev[-8:]:
        print(json.dumps(e))


def maps_pass(eng, x, y):
    from wlengine import maps
    return maps.is_passable(eng.sc.map(1), x, y)


if __name__ == "__main__":
    main()
