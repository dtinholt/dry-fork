"""Probe 396: find the scenario definitions in tests/test_m5_rules.py (the
'bump' script) and print the surrounding code.

Run: python3 tests/fixtures-generated/probe396.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
tf = os.path.join(ROOT, "tests", "test_m5_rules.py")
src = open(tf).read()
lines = src.splitlines()
for i, ln in enumerate(lines):
    if "bump" in ln or "SCEN" in ln or "def runner" in ln or "SEED" in ln:
        print("%4d: %s" % (i + 1, ln))
