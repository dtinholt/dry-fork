"""Dump wl_combat_ref.py 150-215 and the wl_support ref_* helpers.

Usage: python3 tests/fixtures-generated/probe56.py [ref|support|all]
"""
import sys

REF = "tests/wl_combat_ref.py"
SUP = "tests/wl_support.py"


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
if which in ("all", "ref"):
    show(REF, 150, 215)
if which in ("all", "support"):
    grep(SUP, "def ref_", 0)
    grep(SUP, "def ref_build_groups", 12)
    grep(SUP, "def ref_monster_need", 6)
    grep(SUP, "def ref_ranged_need", 6)
    grep(SUP, "def ref_jam_chance", 6)
    grep(SUP, "def ref_damage_member", 12)
    grep(SUP, "def ref_level_after", 6)
    grep(SUP, "def ref_max_hp", 6)
    grep(SUP, "def ref_speed_order", 20)
