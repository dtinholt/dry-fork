"""Probe 376: diagnose M5 test_bump_is_not_a_step.

The test walks LEFT 13 times from (15,20) in Saltwell (location 1) and expects
to end at x=3 with a bump into (2,20) class 11.  We currently end at x=4, so
one of the 12 steps is being refused.  Dump the map cells around y=20 and the
headless event stream.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))

import wlengine.headless as H  # noqa: E402
import wlengine.scenario as S  # noqa: E402


def find_dirs():
    out = []
    for d in glob.glob(os.path.join(HERE, "*")):
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "GAME1")):
            out.append(d)
    return out


def dump_cells(sc, loc, ys, xs):
    m = sc.map(loc)
    tiles = m.get("tiles")
    cls = m.get("action_class")
    print("  loc", loc, "w", m.get("width"), "h", m.get("height"),
          "keys", sorted(m.keys()))
    for y in ys:
        row = []
        for x in xs:
            t = tiles[y][x] if tiles else "?"
            c = cls[y][x] if cls else "?"
            row.append("x%d:t%s/c%s" % (x, t, c))
        print("   y=%d %s" % (y, " ".join(row)))


def main():
    print("headless attrs:", [n for n in dir(H) if not n.startswith("_")])
    print("scenario attrs:", [n for n in dir(S) if not n.startswith("_")])
    dirs = find_dirs()
    print("data dirs:", dirs)
    for d in dirs:
        try:
            sc = S.load(d)
        except Exception as e:  # noqa: BLE001
            print(" load failed", d, e)
            continue
        print("===", d)
        for loc in (0, 1):
            try:
                dump_cells(sc, loc, [19, 20, 21], list(range(0, 8)))
            except Exception as e:  # noqa: BLE001
                print("  dump failed loc", loc, e)
        # passability helpers if present
        for name in ("passable", "can_enter", "cell", "action_at", "blocked"):
            fn = getattr(sc, name, None)
            if fn is not None:
                print("  scenario has", name)
                try:
                    for x in range(0, 6):
                        print("    %s(1,%d,20) -> %r" % (name, x, fn(1, x, 20)))
                except Exception as e:  # noqa: BLE001
                    print("    %s raised %s" % (name, e))
                break
    # try to drive the headless engine
    for name in ("run", "run_script", "Session", "Engine", "Driver", "main"):
        print("headless.%s = %r" % (name, getattr(H, name, None)))


main()
