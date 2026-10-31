"""Compare SPEC-05 ASCII art (glyph -> tile id) with the JSON tiles for every
map, row by row, and report every differing cell.

Glyph table: SPEC-06 section 2.3, tiles 0..31.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
GLYPHS = '.:"=,so~^bTYH*O%#_;/+nhPp|w`XGK>'
G2T = {c: i for i, c in enumerate(GLYPHS)}

SECTIONS = {
    "map0-overworld.json": "### 5.1 Dry Fork overworld",
    "map1-saltwell.json": "### 5.2 Saltwell",
    "map2-ninemile.json": "### 5.3 Ninemile",
    "map3-pumphouse.json": "### 5.4 Pumphouse Deep",
}


def ascii_rows(section_title):
    txt = (SPEC / "SPEC-05-scenario.md").read_text(encoding="utf-8")
    i = txt.index(section_title)
    seg = txt[i:]
    m = re.search(r"```text\n(.*?)```", seg, re.S)
    block = m.group(1)
    rows = {}
    for line in block.split("\n"):
        mm = re.match(r"^\s*(\d+)\s+(.*)$", line)
        if mm:
            rows[int(mm.group(1))] = mm.group(2)
    return rows


def main():
    for fname, title in SECTIONS.items():
        d = json.loads((SPEC / "scenario" / fname).read_text())
        rows = ascii_rows(title)
        tiles = d["tiles"]
        print("=== %s (%s) ascii rows=%d json rows=%d width=%d ===" %
              (fname, title, len(rows), len(tiles), d["width"]))
        diffs = []
        for y in sorted(rows):
            r = rows[y]
            if y >= len(tiles):
                diffs.append((y, "row missing in json"))
                continue
            for x, ch in enumerate(r):
                t = G2T.get(ch)
                if t is None:
                    diffs.append((y, x, "unknown glyph %r" % ch))
                    continue
                if x >= len(tiles[y]):
                    diffs.append((y, x, "col missing in json"))
                    continue
                if tiles[y][x] != t:
                    diffs.append((y, x, "ascii tile %d (%r) json tile %d" % (t, ch, tiles[y][x])))
        print("differences: %d" % len(diffs))
        for dd in diffs[:40]:
            print("   ", dd)
        # also: does the json have non-zero cells outside the ascii rows?
        for y in range(len(tiles)):
            if y not in rows:
                nz = [(x, v) for x, v in enumerate(tiles[y]) if v != 0]
                if nz:
                    print("   json row %d not in ascii, non-zero: %s" % (y, nz[:10]))


if __name__ == "__main__":
    main()
