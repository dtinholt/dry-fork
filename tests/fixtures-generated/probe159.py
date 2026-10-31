"""Probe 159: render the JSON action_class grid as ASCII and compare with the
SPEC-05 Saltwell art (with exact character counts).

Run: python3 tests/fixtures-generated/probe159.py
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

    m = W.load_json(W.SCENARIO / "map1-saltwell.json")
    ac = m["action_class"]
    av = m["action_value"]
    tiles = m["tiles"]
    print("JSON grid (class 11 -> '|' if tile 25 else 'Y', class 10 -> ';', else '.'):")
    print("     00000000001111111111222222222233")
    print("     01234567890123456789012345678901")
    for y in range(32):
        row = []
        for x in range(32):
            c = ac[y][x]
            if c == 11:
                row.append("|" if tiles[y][x] == 25 else "Y")
            elif c == 10:
                row.append(";")
            elif c == 0:
                row.append(".")
            else:
                row.append(str(c))
        print("%3d  %s" % (y, "".join(row)))

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
    print("SPEC art rows with lengths:")
    for i in range(start, end):
        ln = lines[i].rstrip("\n")
        if ln.startswith("  ") and ("|" in ln or "." in ln) and len(ln) > 20:
            print("len=%2d %r" % (len(ln), ln))


if __name__ == "__main__":
    main()
