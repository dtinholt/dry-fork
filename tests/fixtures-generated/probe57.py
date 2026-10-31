"""List the tests directory and dump conftest.py / wl_support.py helpers.

Usage: python3 tests/fixtures-generated/probe57.py [ls|conftest|support|all]
"""
import os
import sys


def ls(path):
    print("=== ls %s ===" % path)
    for name in sorted(os.listdir(path)):
        p = os.path.join(path, name)
        print("  %s%s" % (name, "/" if os.path.isdir(p) else ""))


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
if which in ("all", "ls"):
    ls("tests")
    ls("SPEC")
    ls("SPEC/scenario")
if which in ("all", "conftest"):
    show("tests/conftest.py", 1, 200)
if which in ("all", "conftest2"):
    show("tests/conftest.py", 185, 239)
if which in ("all", "support"):
    grep("tests/wl_support.py", "def ref_", 0)
    grep("tests/wl_support.py", "def ref_build_groups", 14)
    grep("tests/wl_support.py", "def ref_monster_need", 6)
    grep("tests/wl_support.py", "def ref_ranged_need", 6)
    grep("tests/wl_support.py", "def ref_jam_chance", 6)
    grep("tests/wl_support.py", "def ref_damage_member", 14)
    grep("tests/wl_support.py", "def ref_level_after", 6)
    grep("tests/wl_support.py", "def ref_max_hp", 6)
    grep("tests/wl_support.py", "def ref_speed_order", 22)
