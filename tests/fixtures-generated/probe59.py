"""Dump the M5 save/load tests and labstate.py.

Usage: python3 tests/fixtures-generated/probe59.py [tests|labstate|all]
"""
import sys


def show(path, a, b):
    lines = open(path).read().split("\n")
    print("=== %s lines %d-%d (of %d) ===" % (path, a, b, len(lines)))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))


which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("all", "tests"):
    show("tests/test_m5_rules.py", 760, 835)
if which in ("all", "labstate"):
    show("src/wlengine/labstate.py", 1, 60)
if which in ("all", "labtests"):
    show("tests/test_m5_rules.py", 380, 435)
