"""probe448: compare SPEC-05 Saltwell ASCII art against SPEC/scenario/map1-saltwell.json.

Goal: settle the off-by-one question from iterations 113-117.
The M5 test test_bump_is_not_a_step expects the cactus at (2,20) and the M6 test
test_look expects the road ';' at (14,20).  The frozen JSON is said to have the
';' at x=15.  This probe parses the ASCII art exactly as printed (including the
leading '|' column) and prints, for every row, the columns where the ASCII and
the JSON disagree, plus the raw ASCII row with a column ruler.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
SCEN = SPEC / "scenario"

GLYPH_TO_TILE = {
    ".": 0, ":": 1, '"': 2, "=": 3, ",": 4, "s": 5, "o": 6, "~": 7,
    "^": 8, "b": 9, "T": 10, "Y": 11, "H": 12, "*": 13, "O": 14, "%": 15,
    "#": 16, "_": 17, ";": 18, "/": 19, "+": 20, "n": 21, "h": 22, "P": 23,
    "p": 24, "|": 25, "w": 26, "`": 27, "X": 28, "G": 29, "K": 30, ">": 31,
}


def saltwell_ascii():
    text = (SPEC / "SPEC-05-scenario.md").read_text(encoding="utf-8")
    i = text.index("### 5.2 Saltwell")
    j = text.index("```text", i)
    k = text.index("```", j + 7)
    block = text[j + 7:k]
    rows = {}
    for line in block.splitlines():
        m = re.match(r"^\s*(\d+)\s\s(.*)$", line)
        if not m:
            continue
        y = int(m.group(1))
        rows[y] = m.group(2)
    return rows


def main():
    rows = saltwell_ascii()
    data = json.loads((SCEN / "map1-saltwell.json").read_text(encoding="utf-8"))
    tiles = data["tiles"]
    print("json dims: rows=%d cols=%d" % (len(tiles), len(tiles[0])))
    print("ascii rows: %d" % len(rows))
    print()
    ruler = "".join(str(i % 10) for i in range(40))
    print("     " + ruler)
    for y in sorted(rows):
        art = rows[y]
        print("%3d  %s" % (y, art))
    print()
    # Compare: ASCII string index i -> map x = i (leading '|' included).
    for y in sorted(rows):
        art = rows[y]
        jrow = tiles[y] if y < len(tiles) else []
        diffs = []
        for x in range(max(len(art), len(jrow))):
            a = art[x] if x < len(art) else None
            jv = jrow[x] if x < len(jrow) else None
            at = GLYPH_TO_TILE.get(a) if a is not None else None
            if at != jv:
                diffs.append((x, a, at, jv))
        if diffs:
            print("row %d diffs (x, ascii, ascii_tile, json_tile): %s" % (y, diffs))
    print()
    # Also compare with the ASCII shifted right by one (i.e. drop the leading '|').
    print("=== shifted comparison (ascii index i -> map x = i-1) ===")
    for y in sorted(rows):
        art = rows[y]
        jrow = tiles[y] if y < len(tiles) else []
        diffs = []
        for x in range(max(len(art), len(jrow) + 1)):
            a = art[x + 1] if x + 1 < len(art) else None
            jv = jrow[x] if x < len(jrow) else None
            at = GLYPH_TO_TILE.get(a) if a is not None else None
            if at != jv:
                diffs.append((x, a, at, jv))
        if diffs:
            print("row %d diffs: %s" % (y, diffs))
    print()
    print("row 20 json:", tiles[20])
    print("row 20 ascii:", rows[20])
    print("row 11 json:", tiles[11])
    print("row 11 ascii:", rows[11])
    print("row 31 json:", tiles[31])
    print("row 31 ascii:", rows[31])


if __name__ == "__main__":
    main()
