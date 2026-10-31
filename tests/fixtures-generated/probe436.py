"""probe436: compare the SPEC-05 ASCII art of every map against the frozen
SPEC/scenario JSON, using the correct glyph->tile mapping (JSON tile id =
glyph id + 1 for glyph >= 1, 0 for '.'), and print the non-zero cells of each
JSON row with explicit indices.

Run: python3 tests/fixtures-generated/probe436.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
SCEN = SPEC / "scenario"

GLYPHS = '.:"=,so~^bTYH*O%#_;/+nhPp|w`XGK>'


def glyph_to_tile(ch):
    if ch == ".":
        return 0
    i = GLYPHS.find(ch)
    if i < 0:
        return None
    return i + 1


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
    scen = json.loads((SCEN / "scenario.json").read_text(encoding="utf-8"))
    for loc in scen["locations"]:
        m = json.loads((SCEN / loc["file"]).read_text(encoding="utf-8"))
        heading = "### 5.%d " % (loc["location"] + 1)
        body = section(text, heading)
        rows = ascii_rows(body)
        print("=== location %d %s: %d ascii rows, json %dx%d" % (
            loc["location"], m["name"], len(rows), m["width"], m["height"]))
        tiles = m["tiles"]
        for y in sorted(rows):
            if y >= len(tiles):
                continue
            row = rows[y]
            diffs = []
            for x, ch in enumerate(row):
                want = glyph_to_tile(ch)
                if want is None:
                    continue
                if x < len(tiles[y]) and tiles[y][x] != want:
                    diffs.append((x, ch, want, tiles[y][x]))
            if diffs:
                print("  row %2d: %d diffs %s" % (y, len(diffs), diffs[:12]))
        # print non-zero cells of the json rows that matter
        for y in (11, 20, 21, 31):
            nz = [(x, tiles[y][x]) for x in range(len(tiles[y])) if tiles[y][x] != 0]
            print("  json row %2d non-zero: %s" % (y, nz))
            if y in rows:
                print("  ascii row %2d: %r" % (y, rows[y]))


if __name__ == "__main__":
    main()
