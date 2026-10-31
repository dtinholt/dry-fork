"""Probe 379: parse the SPEC-05 Saltwell ASCII map properly and compare with
the JSON arrays under both index conventions.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
MAP1 = os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")

GLYPH = {0: ".", 1: ".", 2: ".", 3: ".", 4: ".", 5: ".", 6: ".", 7: "~",
         8: "#", 9: "o", 10: "T", 11: "Y", 12: "=", 13: "t", 14: "c",
         15: "r", 16: "#", 17: "_", 18: ";", 19: "/", 20: "D", 21: "C",
         22: "H", 23: "P", 24: "p", 25: "|", 26: "O", 27: "_", 28: "#",
         29: "G", 30: "S", 31: "s"}


def spec_ascii():
    lines = open(SPEC).read().splitlines()
    starts = [i for i, ln in enumerate(lines)
              if ln.strip().startswith("00000000001111111111222222222233")]
    start = starts[1]
    rows = []
    for ln in lines[start + 2:start + 2 + 32]:
        m = re.match(r"^\s*(\d{1,2})\s{2,}(\S{32})\s*$", ln)
        if m:
            rows.append(m.group(2))
    return rows


def render(grid):
    return ["".join(GLYPH.get(grid[y][x], "?") for x in range(32)) for y in range(32)]


def main():
    d = json.load(open(MAP1))
    t = d["tiles"]
    spec = spec_ascii()
    print("spec rows:", len(spec))
    if len(spec) != 32:
        print("first few:", spec[:3])
        return
    yx = render(t)
    xy = render([[t[x][y] for x in range(32)] for y in range(32)])
    for name, grid in (("[y][x]", yx), ("[x][y]", xy)):
        diff = [y for y in range(32) if grid[y] != spec[y]]
        print(name, "rows differing:", diff, "count", len(diff))
    for y in (9, 20, 30, 31):
        print("y=%2d spec %s" % (y, spec[y]))
        print("      yx   %s" % yx[y])
        print("      xy   %s" % xy[y])


main()
