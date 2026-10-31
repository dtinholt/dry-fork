"""Probe 377: compile the scenario and run the M5 bump script, dumping events.

Also dumps the map cells around (x, 20) for location 1 so we can see which
cell refuses the step.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wlengine.headless as H  # noqa: E402
import wlengine.scenario as S  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")
SEED = 20261021


def main():
    d = tempfile.mkdtemp(prefix="probe377-")
    S.compile(SCEN, d)
    print("compiled to", d)
    print("files:", sorted(os.listdir(d)))
    ev = H.run(d, {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, None)
    for i, e in enumerate(ev):
        print(i, json.dumps(e, sort_keys=True))
    # map cells
    sc = S.load(d)
    for loc in (0, 1):
        m = sc.map(loc)
        cells = m.get("cells")
        print("loc", loc, "cells type", type(cells).__name__)
        if cells is None:
            continue
        for y in (19, 20, 21):
            row = []
            for x in range(0, 8):
                c = cells[y][x] if isinstance(cells, list) else None
                row.append("x%d:%r" % (x, c))
            print("  y=%d %s" % (y, " ".join(row)))


main()
