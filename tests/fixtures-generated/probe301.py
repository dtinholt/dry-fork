"""Probe 301: dump the scenario module API (map, location names, premade party).

Run: python3 tests/fixtures-generated/probe301.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)


def main():
    p = os.path.join(SRC, "wlengine", "scenario.py")
    with open(p, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    print("total lines:", len(lines))
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if (s.startswith("def ") or s.startswith("class ") or s.startswith("    def ")
                or "location_name" in line or "def map" in line or "border_image" in line
                or "premade_party" in line or "def compile" in line):
            print("%4d| %s" % (i, line))


if __name__ == "__main__":
    main()
