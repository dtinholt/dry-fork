"""Dump the _saved/_payload helpers of test_m5_rules.py and SPEC-02 section 4.

Usage: python3 tests/fixtures-generated/probe60.py [helpers|all]
"""
import sys


def show(path, a, b):
    lines = open(path).read().split("\n")
    print("=== %s lines %d-%d (of %d) ===" % (path, a, b, len(lines)))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))


which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("all", "helpers"):
    show("tests/test_m5_rules.py", 735, 770)
if which in ("all", "labtests"):
    show("tests/test_m5_rules.py", 380, 435)
if which in ("all", "m6"):
    show("tests/test_m6_playable.py", 1, 120)
