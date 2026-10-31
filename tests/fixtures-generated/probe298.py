"""Probe 298: dump headless.py lines 670-1030.

Run: python3 tests/fixtures-generated/probe298.py
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
    hl = os.path.join(SRC, "wlengine", "headless.py")
    show(hl, 670, 1030)


if __name__ == "__main__":
    main()
