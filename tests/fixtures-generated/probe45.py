"""Probe 45: render the Saltwell JSON action_class grid both ways and compare
with the SPEC-05 ASCII art (walls '#' at the border and the two buildings in
rows 2 to 7)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"

ART = """||||||||||||||||||||||||||||||||
|..............................|
|.#########......#############.|
|.#_______#......#___________#.|
|.#__nnn__#......#____h______#.|
|.#_______#......#___________#.|
|.#_______#..Y...#___________#.|
|.####/####......######/######.|
|.....;................;.......|
|.....;;;;;;;;;;;;;;;;;;;......|
|..T.........;;;;;.............|
|............;;P;;......Y......|
|............;;;;;.............|
|..............;...............|
|..............;.......b.......|
|..w...........;...............|
|..............;...............|
|.......p......;...............|
|.......;;;;;;;;...............|
|..............;.......T.......|
|..Y...........;...............|
|..............;..........Y....|
|..............;...............|
|.....b........;...............|
|..............;...............|
|..............;.........b.....|
|..............;...............|
|..T...........;...............|
|..............;...............|
|..............;...............|
|..............;;..............|
|||||||||||||||;;|||||||||||||||""".splitlines()


def render(grid, size=32):
    out = []
    for y in range(size):
        row = []
        for x in range(size):
            v = grid[y][x]
            row.append("#" if v == 11 else ("." if v == 0 else str(v % 10)))
        out.append("".join(row))
    return out


def main():
    d = json.loads((SCEN / "map1-saltwell.json").read_text())
    ac = d["action_class"]
    print("== JSON action_class as [y][x] ==")
    for r in render(ac):
        print(r)
    print("== JSON action_class transposed ([x][y]) ==")
    tr = [[ac[x][y] for x in range(32)] for y in range(32)]
    for r in render(tr):
        print(r)
    print("== SPEC art ==")
    for r in ART:
        print(r)
    print("== diff [y][x] vs art ==")
    for y in range(32):
        for x in range(32):
            a = ART[y][x]
            want = 11 if a == "|" or a == "#" else 0
            got = ac[y][x]
            if (want == 11) != (got == 11):
                print("  (%d,%d) art %r json %d" % (x, y, a, got))


if __name__ == "__main__":
    main()
