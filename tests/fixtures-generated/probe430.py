"""probe430: extract the SPEC-05 5.2 map ASCII rows (they start with a row
number and spaces) and compare them, column by column, with the frozen
SPEC/scenario/map1-saltwell.json tile/action_class arrays.

Run: python3 tests/fixtures-generated/probe430.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
SCEN = SPEC / "scenario"

GLYPH = {
    '.': 0, '"': 1, '=': 2, ',': 3, 's': 4, 'o': 5, '~': 6, '^': 7, 'b': 8,
    'T': 9, 'Y': 10, 'H': 11, '*': 12, 'O': 13, '%': 14, '#': 15, '_': 16,
    ';': 17, '/': 18, '+': 19, 'n': 20, 'h': 21, 'P': 22, 'p': 23, '|': 24,
    'w': 25, '`': 26, 'X': 27, 'G': 28, 'K': 29, '>': 30,
}


def section(text, heading):
    m = re.search(r"^%s.*$" % re.escape(heading), text, re.M)
    if not m:
        return ""
    start = m.end()
    m2 = re.search(r"^#{2,3} ", text[start:], re.M)
    return text[start:start + (m2.start() if m2 else len(text))]


def ascii_rows(body):
    rows = {}
    for line in body.splitlines():
        m = re.match(r"^\s*(\d+)\s+(\S+)\s*$", line)
        if m:
            rows[int(m.group(1))] = m.group(2)
    return rows


def main():
    text = (SPEC / "SPEC-05-scenario.md").read_text(encoding="utf-8")
    body = section(text, "### 5.2 Saltwell")
    rows = ascii_rows(body)
    print("ascii rows:", sorted(rows))
    for y in (0, 1, 2, 11, 20, 31):
        if y in rows:
            print("ascii[%2d] len=%d %r" % (y, len(rows[y]), rows[y]))

    j = json.loads((SCEN / "map1-saltwell.json").read_text(encoding="utf-8"))
    tiles = j["tiles"]
    aclass = j["action_class"]
    print("json: %dx%d" % (j["width"], j["height"]))

    print("\n--- direct comparison (ascii index x == json x) ---")
    for y in sorted(rows):
        if y >= len(tiles):
            continue
        row = rows[y]
        diffs = []
        for x, ch in enumerate(row):
            want = GLYPH.get(ch)
            if want is None:
                continue
            if x < len(tiles[y]) and tiles[y][x] != want:
                diffs.append((x, ch, want, tiles[y][x]))
        if diffs:
            print("row %2d: %d diffs %s" % (y, len(diffs), diffs[:10]))

    print("\n--- shifted comparison (ascii x -> json x-1) ---")
    for y in sorted(rows):
        if y >= len(tiles):
            continue
        row = rows[y]
        diffs = []
        for x, ch in enumerate(row):
            want = GLYPH.get(ch)
            if want is None:
                continue
            if x - 1 >= 0 and x - 1 < len(tiles[y]) and tiles[y][x - 1] != want:
                diffs.append((x, ch, want, tiles[y][x - 1]))
        if diffs:
            print("row %2d: %d diffs %s" % (y, len(diffs), diffs[:10]))

    print("\n--- json rows 2,3,11,20,31 ---")
    for y in (2, 3, 11, 20, 31):
        print("tiles[%2d] = %s" % (y, tiles[y]))
        print("aclass[%2d] = %s" % (y, aclass[y]))

    print("\n--- action_cells ---")
    for c in j["action_cells"]:
        print(c)


if __name__ == "__main__":
    main()
