"""Probe 158: print SPEC-05 section 5.2 (Saltwell) and the JSON rows 17/20/21
with action values, to find the cactus.

Run: python3 tests/fixtures-generated/probe158.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    import wl_support as W

    spec = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
    with open(spec, encoding="utf-8") as fh:
        lines = fh.readlines()
    start = end = None
    for i, ln in enumerate(lines):
        if ln.startswith("### 5.2 Saltwell"):
            start = i
        elif start is not None and ln.startswith("### 5.3"):
            end = i
            break
    if end is None:
        end = start + 300
    for i in range(start, end):
        sys.stdout.write("%4d| %s" % (i + 1, lines[i]))

    m = W.load_json(W.SCENARIO / "map1-saltwell.json")
    for y in (17, 20, 21):
        print("y=%d class:" % y, m["action_class"][y])
        print("y=%d value:" % y, m["action_value"][y])
        print("y=%d tiles:" % y, m["tiles"][y])
    print("class11 records:", json.dumps(m["records"]["11"], sort_keys=True))


if __name__ == "__main__":
    main()
