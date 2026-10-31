"""Probe 149: dump the frozen test harness sources so we can inspect them
without spending read_file budget.  Prints conftest.py, wl_support.py and the
head of test_m5_rules.py.

Usage: python3 tests/fixtures-generated/probe149.py [name ...]
Names: conftest, support, m5, m5tail, m6, combatref, all
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")

FILES = {
    "conftest": (os.path.join(TESTS, "conftest.py"), None, None),
    "support": (os.path.join(TESTS, "wl_support.py"), None, None),
    "m5": (os.path.join(TESTS, "test_m5_rules.py"), 1, 130),
    "m5tail": (os.path.join(TESTS, "test_m5_rules.py"), 440, 520),
    "m6": (os.path.join(TESTS, "test_m6_playable.py"), None, None),
    "combatref": (os.path.join(TESTS, "wl_combat_ref.py"), None, None),
}


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


def main():
    names = sys.argv[1:] or ["conftest", "support", "m5", "m5tail"]
    if names == ["all"]:
        names = list(FILES)
    for name in names:
        if name not in FILES:
            print("unknown:", name)
            continue
        dump(*FILES[name])


if __name__ == "__main__":
    main()
