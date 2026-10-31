"""Dump the M5 combat tests, the walkthrough script helpers and the reference
log's combat events, so combat can be implemented without spending reads.

Usage: python3 tests/fixtures-generated/probe53.py [tests|ref|script|all]
"""
import sys

TESTS = "tests/test_m5_rules.py"
REF = "tests/fixtures-generated/reflog.txt"


def show(path, a, b):
    lines = open(path).read().split("\n")
    print("=== %s lines %d-%d (of %d) ===" % (path, a, b, len(lines)))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))


def grep(path, pat, ctx=0):
    lines = open(path).read().split("\n")
    print("=== grep %s %r ===" % (path, pat))
    for i, line in enumerate(lines):
        if pat in line:
            for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
                print("%4d| %s" % (j + 1, lines[j]))


which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("all", "tests"):
    show(TESTS, 620, 834)
if which in ("all", "ref"):
    grep(REF, "encounter_start", 0)
    grep(REF, "combat_end", 0)
    grep(REF, "round_start", 0)
if which in ("all", "script"):
    grep(TESTS, "def opening_script", 20)
    grep(TESTS, "def prefix", 10)
    grep(TESTS, "def between", 10)
    grep(TESTS, "def ckpt", 6)
    grep(TESTS, "def subset", 6)
    grep(TESTS, "def strip", 6)
