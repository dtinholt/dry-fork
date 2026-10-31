"""Probe 296: dump the headless.py parts relevant to look / dispatch / keys.

Run: python3 tests/fixtures-generated/probe296.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)


def main():
    hl = os.path.join(SRC, "wlengine", "headless.py")
    with open(hl, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    print("total lines:", len(lines))
    for i, line in enumerate(lines, 1):
        low = line.lower()
        if ("look" in low or "def key_" in line or "def dispatch" in line
                or "def new_game" in line or "def input" in line
                or "def run_script" in line or "def run_repeat" in line
                or "def _until_met" in line or "def snapshot" in line
                or "def member_snapshot" in line or "def move" in line
                or "def try_move" in line or "def bump" in line):
            print("%4d| %s" % (i, line))


if __name__ == "__main__":
    main()
