"""Probe 151: print the runner fixture from conftest and the headless API,
then run the bump scenario and dump the events.

Run: python3 tests/fixtures-generated/probe151.py
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
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    lo = 0 if start is None else max(0, start - 1)
    hi = len(lines) if end is None else min(len(lines), end)
    for i in range(lo, hi):
        sys.stdout.write("%4d| %s" % (i + 1, lines[i]))
    print()


def main():
    import wl_support as W
    # find the runner fixture in conftest
    dump(os.path.join(TESTS, "conftest.py"), 180, 260)
    print("W.api:", W.api)
    print("W.SCENARIO:", W.SCENARIO)
    print("W.engine_ready:", W.engine_ready)
    print("W._armed:", W._armed)
    print("W.audit_hook:", W.audit_hook)
    print("W.FORBIDDEN_PREFIXES:", W.FORBIDDEN_PREFIXES)
    print("W attrs:", sorted(a for a in dir(W) if not a.startswith("__")))


if __name__ == "__main__":
    main()
