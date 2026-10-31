"""Probe 162: grep SPEC-04/SPEC-05 for LR-15, bump, cactus, and the walkthrough
step list; also print the SPEC-03 9.6 movement section.

Run: python3 tests/fixtures-generated/probe162.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPEC = os.path.join(ROOT, "SPEC")


def grep(path, needles, ctx=0):
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    print("=" * 70)
    print("GREP", os.path.basename(path), needles)
    for i, ln in enumerate(lines):
        low = ln.lower()
        if any(n.lower() in low for n in needles):
            lo = max(0, i - ctx)
            hi = min(len(lines), i + ctx + 1)
            for k in range(lo, hi):
                sys.stdout.write("%4d| %s" % (k + 1, lines[k]))
            print("   ---")


def section(path, heading, stop_prefix="## "):
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith(heading):
            start = i
            break
    if start is None:
        print("no heading", heading, "in", path)
        return
    for i in range(start, len(lines)):
        if i > start and lines[i].startswith(stop_prefix):
            break
        sys.stdout.write("%4d| %s" % (i + 1, lines[i]))


def main():
    grep(os.path.join(SPEC, "SPEC-04-rules.md"), ["LR-15", "bump"], ctx=6)
    grep(os.path.join(SPEC, "SPEC-05-scenario.md"), ["bump", "cactus"], ctx=4)
    section(os.path.join(SPEC, "SPEC-03-maps.md"), "### 9.6")


if __name__ == "__main__":
    main()
