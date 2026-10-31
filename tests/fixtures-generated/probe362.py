"""Probe 362: reproduce the M5 bump failure and dump the map cells around it.

Runs the 'bump' scenario (13 LEFT from (15,20) on location 1) through
headless.run and prints the events, then dumps the actionClass/action/image
cells for x in 0..8 at y in 19..21 so we can see where the cactus really is.

Also prints the scenario map info and the passability of each cell so we can
tell whether the engine is treating the cactus as passable (which would make
the party step onto it instead of bumping).
"""
import os
import sys
import json
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from wlengine import headless  # noqa: E402


def find_data():
    """Locate a compiled data directory (one holding LABTABLES.BIN)."""
    pats = (
        "tests/fixtures-generated/*data",
        "tests/fixtures-generated/*/*data",
        "tests/fixtures-generated/*",
        "tests/fixtures-generated/*/*",
    )
    for pat in pats:
        for c in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.isdir(c) and os.path.isfile(os.path.join(c, "LABTABLES.BIN")):
                return c
    return None


def dump_events(ev):
    for i, e in enumerate(ev):
        print("%3d %s" % (i, json.dumps(e, default=str)[:220]))
    ck = [e for e in ev if e.get("type") == "checkpoint"]
    print("checkpoint:", json.dumps(ck[-1], default=str) if ck else None)


def dump_cells(sc, loc):
    m = sc.map(loc)
    print("map size", m["size"], "info", json.dumps(m["info"], default=str)[:300])
    for y in (19, 20, 21):
        row_cls = m["cells"]["actionClass"][y]
        row_act = m["cells"]["action"][y]
        row_img = m["cells"]["image"][y]
        print("y=%d cls %s" % (y, list(row_cls[:9])))
        print("y=%d act %s" % (y, list(row_act[:9])))
        print("y=%d img %s" % (y, list(row_img[:9])))
    from wlengine import maps
    print("passable y=20:", [(x, maps.is_passable(m, x, 20)) for x in range(0, 9)])
    print("passable y=19:", [(x, maps.is_passable(m, x, 19)) for x in range(0, 9)])


def main():
    dd = find_data()
    print("data dir:", dd)
    if dd is None:
        return
    ev = headless.run(dd, {"seed": 20261021,
                           "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    dump_events(ev)

    from wlengine import scenario as sc_mod
    sc = sc_mod.Scenario(dd)
    dump_cells(sc, 1)

    # also dump the reference log if one exists
    for name in ("dump338.txt",):
        p = os.path.join(ROOT, "tests", "fixtures-generated", name)
        if os.path.isfile(p):
            print("=" * 60)
            print("reference", name)
            with open(p, encoding="utf-8", errors="replace") as fh:
                for i, l in enumerate(fh):
                    if i > 60:
                        break
                    print("  ", l.rstrip())


main()
