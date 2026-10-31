"""Probe 150: dump harness sources + map data around the cactus bump.

Run: python3 tests/fixtures-generated/probe150.py [section ...]
Sections: harness, map, run, all
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def dump(path, start=None, end=None):
    print("=" * 70)
    print("FILE:", path)
    print("=" * 70)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:
        print("  cannot read:", exc)
        return
    lo = 0 if start is None else max(0, start - 1)
    hi = len(lines) if end is None else min(len(lines), end)
    for i in range(lo, hi):
        sys.stdout.write("%4d| %s" % (i + 1, lines[i]))
    print()


def section_harness():
    dump(os.path.join(TESTS, "conftest.py"))
    dump(os.path.join(TESTS, "wl_support.py"))


def section_map():
    import wl_support as W
    from wlengine import scenario as scen
    sc = scen.Scenario(W.SCENARIO)
    m = sc.map(1)
    print("map 1 size", m["size"], "info", m["info"])
    cells = m["cells"]
    for y in range(18, 23):
        row = []
        for x in range(0, 10):
            row.append("%d/%d/%d" % (cells["actionClass"][y][x],
                                     cells["action"][y][x],
                                     cells["image"][y][x]))
        print("y=%2d " % y, " ".join(row))
    print("records near (2,20):")
    for x in range(0, 8):
        rec = None
        try:
            rec = __import__("wlengine.maps", fromlist=["maps"]).record_at(m, x, 20)
        except Exception as exc:  # pragma: no cover
            rec = "ERR %s" % exc
        print("  x=%d cls=%d act=%d rec=%r" % (x, cells["actionClass"][20][x],
                                               cells["action"][20][x], rec))


def section_run():
    import wl_support as W
    from wlengine import headless
    print("headless attrs:", [a for a in dir(headless) if not a.startswith("_")])
    print("W attrs:", [a for a in dir(W) if not a.startswith("_")])


def main():
    names = sys.argv[1:] or ["harness", "map", "run"]
    if names == ["all"]:
        names = ["harness", "map", "run"]
    for name in names:
        fn = globals().get("section_" + name)
        if fn is None:
            print("unknown section:", name)
            continue
        print("#### SECTION", name)
        try:
            fn()
        except Exception as exc:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
