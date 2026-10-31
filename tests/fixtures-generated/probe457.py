"""probe457: compare every SPEC-05 Saltwell ASCII cell with the frozen JSON
tiles, using the SPEC-06 2.3 glyph table.

Run: python3 tests/fixtures-generated/probe457.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")

GLYPH = {'.': 0, ':': 1, '"': 2, '=': 3, ',': 4, 's': 5, 'o': 6, '~': 7, '^': 8,
         'b': 9, 'T': 10, 'Y': 11, 'H': 12, '*': 13, 'O': 14, '%': 15, '#': 16,
         '_': 17, ';': 18, '/': 19, '+': 20, 'n': 21, 'h': 22, 'P': 23, 'p': 24,
         '|': 25, 'w': 26, '`': 27, 'X': 28, 'G': 29, 'K': 30, '>': 31}


def main():
    txt = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md"), encoding="utf-8").read().splitlines()
    start = next(i for i, l in enumerate(txt) if l.strip().startswith("0  ||||"))
    art = []
    for k in range(32):
        art.append(txt[start + k][5:])
    m = json.load(open(os.path.join(SCEN, "map1-saltwell.json"), encoding="utf-8"))
    tiles = m["tiles"]
    diffs = []
    for y in range(32):
        row = art[y]
        for x in range(32):
            ch = row[x]
            t = GLYPH.get(ch)
            j = tiles[y][x]
            if t is None:
                diffs.append((y, x, ch, "?", j))
            elif t != j:
                diffs.append((y, x, ch, t, j))
    print("total diffs:", len(diffs))
    for d in diffs:
        print("  y=%2d x=%2d ascii=%r tile=%s json=%s" % d)
    print()
    print("== per-row diff counts ==")
    for y in range(32):
        n = sum(1 for d in diffs if d[0] == y)
        print("y=%2d diffs=%d" % (y, n))


if __name__ == "__main__":
    main()
