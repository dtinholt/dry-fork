"""Dump everything needed to implement M5 combat: the reference model, the
test bodies, the reference log combat window, and the current engine code.

This is a large probe on purpose: the read budget is spent, so it prints all
the source and data needed to write the combat implementation in one go.

Sections:
  1. tests/wl_combat_ref.py            (the oracle for the raider fight)
  2. tests/test_m5_rules.py 600-834    (the failing tests)
  3. src/wlengine/rules.py 200-318     (combat helpers)
  4. src/wlengine/headless.py 700-1044 (engine combat + save/load)
  5. src/wlengine/labstate.py
  6. tests/wl_support.py 340-520       (ref_* helpers)
  7. the reference log combat window
  8. the scenario encounter record for the raiders
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show(path, a=None, b=None):
    print("=" * 78)
    print("FILE", path, a, b)
    print("=" * 78)
    with open(os.path.join(ROOT, path)) as f:
        lines = f.readlines()
    if a is None:
        a, b = 1, len(lines)
    for i in range(a - 1, min(b, len(lines))):
        print("%4d| %s" % (i + 1, lines[i].rstrip()))


show("tests/wl_combat_ref.py")
show("tests/test_m5_rules.py", 600, 834)
show("src/wlengine/rules.py", 200, 318)
show("src/wlengine/headless.py", 700, 1044)
show("src/wlengine/labstate.py")
show("tests/wl_support.py", 340, 520)

# 7. reference log combat window
print("=" * 78)
print("REFERENCE LOG combat window")
print("=" * 78)
for name in ("reflog.txt", "refdump.txt"):
    p = os.path.join(ROOT, "tests", "fixtures-generated", name)
    if not os.path.exists(p):
        continue
    with open(p) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if '"type": "encounter_start"' in line or '"type": "combat_end"' in line:
            lo = max(0, i - 5)
            hi = min(len(lines), i + 90)
            for j in range(lo, hi):
                print("%s:%4d| %s" % (name, j + 1, lines[j].rstrip()))
            print("-" * 60)
    break

# 8. scenario encounter record
print("=" * 78)
print("SCENARIO encounters.json")
print("=" * 78)
for cand in ("SPEC/scenario/encounters.json", "tests/fixtures-generated/dd/encounters.json"):
    p = os.path.join(ROOT, cand)
    if os.path.exists(p):
        print("FOUND", cand)
        print(open(p).read()[:4000])
        break
