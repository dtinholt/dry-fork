"""Dump the combat-relevant parts of headless.py and rules.py for inspection.

This probe is deliberately verbose: it prints the whole headless driver and the
rules module so that a later iteration can implement the combat phases without
re-reading the sources. It also dumps the reference combat log window for the
raider fight and the walkthrough script prefix, so the next iteration can
compare event shapes directly.

Usage: python3 tests/fixtures-generated/probe86.py
Output: tests/fixtures-generated/dump86.txt
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "dump86.txt"


def dump(path, lo, hi):
    lines = (ROOT / path).read_text().splitlines()
    out = ["==== %s lines %d-%d ====" % (path, lo, hi)]
    for i in range(lo - 1, min(hi, len(lines))):
        out.append("%5d %s" % (i + 1, lines[i]))
    return out


def dump_whole(path):
    lines = (ROOT / path).read_text().splitlines()
    out = ["==== %s (%d lines) ====" % (path, len(lines))]
    for i, line in enumerate(lines):
        out.append("%5d %s" % (i + 1, line))
    return out


def dump_tail(path, n):
    lines = (ROOT / path).read_text().splitlines()
    lo = max(1, len(lines) - n + 1)
    return dump(path, lo, len(lines))


def main():
    parts = []
    parts += dump("src/wlengine/headless.py", 1, 80)
    parts += dump("src/wlengine/headless.py", 400, 700)
    parts += dump("src/wlengine/headless.py", 700, 1077)
    parts += dump_whole("src/wlengine/rules.py")
    parts += dump("src/wlengine/scenario.py", 1, 60)
    parts += dump_whole("src/wlengine/labstate.py")
    parts += dump_whole("tests/wl_support.py")
    parts += dump_whole("tests/wl_combat_ref.py")
    parts += dump_whole("tests/test_m5_rules.py")
    parts += dump_whole("tests/conftest.py")
    OUT.write_text("\n".join(parts) + "\n")
    print("wrote", OUT, len(parts), "lines")


if __name__ == "__main__":
    main()
