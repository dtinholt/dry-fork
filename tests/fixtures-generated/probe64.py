"""Dump the combat-relevant source and tests so the next step can be planned.

Run: python3 tests/fixtures-generated/probe64.py [what]

``what`` is one of: all, headless, headless2, rules, tests, support, combatref,
labstate, scenario, grep.

This probe exists only to make reading the frozen sources convenient from the
builder loop; it never writes anything and is not imported by the engine.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show(path, a, b):
    print("=" * 70)
    print("### %s lines %d-%d" % (path, a, b))
    print("=" * 70)
    full = os.path.join(ROOT, path)
    with open(full, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if a <= i <= b:
                print("%4d %s" % (i, line.rstrip("\n")))


def grep(path, pattern):
    print("=" * 70)
    print("### grep %r in %s" % (pattern, path))
    print("=" * 70)
    full = os.path.join(ROOT, path)
    with open(full, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if pattern in line:
                print("%4d %s" % (i, line.rstrip("\n")))


WHAT = sys.argv[1] if len(sys.argv) > 1 else "all"

if WHAT in ("all", "headless"):
    show("src/wlengine/headless.py", 700, 1077)
if WHAT in ("all", "headless2"):
    show("src/wlengine/headless.py", 1, 400)
if WHAT in ("all", "rules"):
    show("src/wlengine/rules.py", 1, 318)
if WHAT in ("all", "tests"):
    show("tests/test_m5_rules.py", 600, 700)
if WHAT in ("all", "support"):
    show("tests/wl_support.py", 340, 520)
if WHAT == "combatref":
    show("tests/wl_combat_ref.py", 1, 200)
if WHAT == "labstate":
    show("src/wlengine/labstate.py", 1, 60)
if WHAT == "scenario":
    show("src/wlengine/scenario.py", 1, 200)
if WHAT == "grep":
    grep("src/wlengine/headless.py", sys.argv[2])
if WHAT == "grep2":
    grep("tests/test_m5_rules.py", sys.argv[2])
if WHAT == "grep3":
    grep("tests/wl_support.py", sys.argv[2])
if WHAT == "grep4":
    grep("src/wlengine/rules.py", sys.argv[2])
