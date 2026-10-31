"""Probe 163: print SPEC-03 section 9.6 in full and SPEC-04 sections 5 and 6.

Run: python3 tests/fixtures-generated/probe163.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPEC = os.path.join(ROOT, "SPEC")


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
    section(os.path.join(SPEC, "SPEC-03-maps.md"), "### 9.6")
    section(os.path.join(SPEC, "SPEC-04-rules.md"), "## 5. Movement and time")
    section(os.path.join(SPEC, "SPEC-04-rules.md"), "## 6. Lab cell hooks")


if __name__ == "__main__":
    main()
