"""Probe 294: dump the parts of headless.py and the CLI entry point that the
remaining M6 failures depend on.

Run: python3 tests/fixtures-generated/probe294.py
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


def dump(path):
    print("=" * 70)
    print(path)
    print("=" * 70)
    with open(path, encoding="utf-8") as fh:
        print(fh.read())


def main():
    hl = os.path.join(SRC, "wlengine", "headless.py")
    show(hl, 180, 245)
    show(hl, 1140, 1231)
    dump(os.path.join(SRC, "wlengine", "__init__.py"))
    dump(os.path.join(SRC, "wlengine", "errors.py"))
    print("=" * 70)
    print("ls src/wlengine")
    print("=" * 70)
    for name in sorted(os.listdir(os.path.join(SRC, "wlengine"))):
        print(name)
    print("=" * 70)
    print("ls src")
    print("=" * 70)
    for name in sorted(os.listdir(SRC)):
        print(name)
    print("=" * 70)
    print("ls tests")
    print("=" * 70)
    for name in sorted(os.listdir(os.path.join(ROOT, "tests"))):
        print(name)
    print("=" * 70)
    print("grep -n 'first_frame_state\\|def run\\|RepeatLimit\\|ScriptError' headless.py")
    print("=" * 70)
    with open(hl, encoding="utf-8") as fh:
        for i, line in enumerate(fh.read().splitlines(), 1):
            if ("first_frame_state" in line or "def run" in line
                    or "RepeatLimit" in line or "ScriptError" in line
                    or "repeat_until" in line):
                print("%4d| %s" % (i, line))


if __name__ == "__main__":
    main()
