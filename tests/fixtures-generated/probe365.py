"""Probe 365: print the full tiles/action_class rows 18..22 of the frozen
Saltwell JSON, and parse the ASCII map from SPEC-05 section 5.2 to compare.
"""
import os
import sys
import json
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")
SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")


def main():
    with open(SCEN, encoding="utf-8") as fh:
        j = json.load(fh)
    for y in range(18, 23):
        print("JSON tiles y=%d:" % y, j["tiles"][y])
        print("JSON acls  y=%d:" % y, j["action_class"][y])
    print()
    # parse the ASCII map
    with open(SPEC, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"### 5\.2 Saltwell.*?```text\n(.*?)```", text, re.S)
    art = m.group(1).splitlines()
    print("ascii lines:", len(art))
    for line in art:
        if line.strip().startswith("20 ") or line.strip().startswith("19 ") or line.strip().startswith("21 "):
            print(repr(line))
    # build the grid
    grid = []
    for line in art[1:]:
        body = line[5:] if len(line) > 5 else line
        grid.append(body)
    print("grid rows", len(grid), "widths", sorted({len(r) for r in grid}))
    for y in range(18, 23):
        row = grid[y]
        print("ASCII y=%d:" % y, row)
        print("   chars x0..8:", list(row[1:10]))
    # compare
    print()
    print("compare JSON tile vs ASCII char (x=0..31, y=18..22)")
    for y in range(18, 23):
        diffs = []
        for x in range(32):
            ch = grid[y][x + 1]
            t = j["tiles"][y][x]
            diffs.append((x, ch, t))
        print("y=%d" % y, diffs[:12])


main()
