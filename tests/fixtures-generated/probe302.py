"""Probe 302: dump scenario.py lines 594-830 (Scenario class).

Run: python3 tests/fixtures-generated/probe302.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)


def show(path, lo, hi):
    print("=" * 70)
    print("%s lines %d-%d" % (path, lo, hi))
    print("=" * 70)
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for i in range(lo - 1, min(hi, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))


def main():
    show(os.path.join(SRC, "wlengine", "scenario.py"), 594, 830)


if __name__ == "__main__":
    main()
