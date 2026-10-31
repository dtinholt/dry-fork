"""Probe 380: show the rows where the JSON Saltwell tiles differ from the
SPEC-05 ASCII map, and the corresponding action classes.
"""
import json
import os
import re

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
        rows.append(m.group(2))
    return rows


def main():
    d = json.load(open(MAP1))
    t = d["tiles"]
    c = d["action_class"]
    spec = spec_ascii()
    for y in range(32):
        row = "".join(GLYPH.get(t[y][x], "?") for x in range(32))
        if row != spec[y]:
            print("y=%d" % y)
            print("  spec %s" % spec[y])
            print("  json %s" % row)
            for x in range(32):
                if row[x] != spec[y][x]:
                    print("    x=%d spec=%r json=%r tile=%d class=%d" % (
                        x, spec[y][x], row[x], t[y][x], c[y][x]))
    # also print the class grid rows 4,14,15,23,25
    for y in (4, 14, 15, 23, 25):
        print("class y=%d %s" % (y, "".join(str(c[y][x] % 10) for x in range(32))))


main()
