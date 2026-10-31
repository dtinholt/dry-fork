"""Probe 420: where are the class-11 cells and the street tiles in map1?"""
import json
import pathlib
import sys

SCEN = pathlib.Path("SPEC/scenario")
OUT = pathlib.Path("tests/fixtures-generated/dump420.txt")
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
ac = m1["action_class"]
av = m1["action_value"]
tl = m1["tiles"]

p("conventions:", m1["conventions"])
p("action_class rows:")
for y in range(32):
    p(" y=%2d %s" % (y, "".join("%X" % v for v in ac[y])))
p("action_value rows:")
for y in range(32):
    p(" y=%2d %s" % (y, "".join("%X" % v for v in av[y])))
p("tiles rows:")
for y in range(32):
    p(" y=%2d %s" % (y, " ".join("%2d" % v for v in tl[y])))

p("class 11 in row 20:", [x for x in range(32) if ac[20][x] == 11])
p("class 11 in col 20:", [y for y in range(32) if ac[y][20] == 11])
p("tile 18 in row 20:", [x for x in range(32) if tl[20][x] == 18])
p("tile 18 in col 20:", [y for y in range(32) if tl[y][20] == 18])
p("tile 18 in row 14:", [x for x in range(32) if tl[14][x] == 18])
p("tile 18 in col 14:", [y for y in range(32) if tl[y][14] == 18])

for (x, y) in [(8, 17), (26, 14), (18, 17), (25, 21), (16, 6), (15, 11), (2, 20), (3, 20), (14, 20), (15, 20)]:
    p("cell (%d,%d): class=%d action=%d tile=%d image=%d" % (x, y, ac[y][x], av[y][x], tl[y][x], tl[y][x] + 10))
    p("   transposed: class=%d action=%d tile=%d" % (ac[x][y], av[x][y], tl[x][y]))

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
