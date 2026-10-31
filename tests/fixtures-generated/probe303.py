"""Probe 303: scenario.py 760-830 and headless look-related code.

Run: python3 tests/fixtures-generated/probe303.py
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
    show(os.path.join(SRC, "wlengine", "scenario.py"), 760, 830)
    hl = os.path.join(SRC, "wlengine", "headless.py")
    with open(hl, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    print("=" * 70)
    print("headless.py lines mentioning look / L / interact")
    print("=" * 70)
    for i, line in enumerate(lines, 1):
        low = line.lower()
        if "look" in low or "interact" in low or '"l"' in low or "'l'" in low:
            print("%4d| %s" % (i, line))


if __name__ == "__main__":
    main()
