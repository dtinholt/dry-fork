"""Probe 361: reproduce the M5 bump failure and dump the map cells around it.

Runs the 'bump' scenario (13 LEFT from (15,20) on location 1) through
headless.run and prints the events, then dumps the actionClass/action/image
cells for x in 0..6 at y=20 so we can see where the cactus really is.
"""
import os
import sys
import json
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from wlengine import headless  # noqa: E402


def find_data():
    for pat in ("tests/fixtures-generated/*data", "tests/fixtures-generated/*/*data"):
        for c in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.isdir(c) and os.path.isfile(os.path.join(c, "LABTABLES.BIN")):
                return c
    # fall back: any dir with LABTABLES.BIN
    for c in sorted(glob.glob(os.path.join(ROOT, "tests", "fixtures-generated", "*"))):
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "LABTABLES.BIN")):
            return c
    return None


def main():
    dd = find_data()
    print("data dir:", dd)
    if dd is None:
        return
    ev, _ = headless.run(dd, {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    for i, e in enumerate(ev):
        print("%3d %s" % (i, json.dumps(e, default=str)[:200]))
    ck = [e for e in ev if e.get("type") == "checkpoint"]
    print("checkpoint:", json.dumps(ck[-1], default=str) if ck else None)

    # dump the map cells
    from wlengine import scenario as sc_mod
    sc = sc_mod.Scenario(dd)
    m = sc.map(1)
    print("map size", m["size"])
    for y in (19, 20, 21):
        row_cls = m["cells"]["actionClass"][y]
        row_act = m["cells"]["action"][y]
        row_img = m["cells"]["image"][y]
        print("y=%d cls %s" % (y, list(row_cls[:8])))
        print("y=%d act %s" % (y, list(row_act[:8])))
        print("y=%d img %s" % (y, list(row_img[:8])))
    print("passable:", [(x, 20, m["cells"]["actionClass"][20][x]) for x in range(0, 8)])


main()
