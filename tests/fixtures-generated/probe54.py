"""Print the reference log's combat windows (raider fight and pump crawler).

Usage: python3 tests/fixtures-generated/probe54.py [raider|crawler|all]
"""
import sys

REF = "tests/fixtures-generated/reflog.txt"


def lines():
    return open(REF).read().split("\n")


def show(a, b):
    for i in range(a - 1, min(b, len(lines()))):
        print("%4d| %s" % (i + 1, lines()[i]))


which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("all", "raider"):
    show(215, 290)
if which in ("all", "crawler"):
    show(740, 800)
