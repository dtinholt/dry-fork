"""Align the Saltwell ASCII art with the JSON map, both ways.

Usage: python3 tests/fixtures-generated/probe40.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC" / "SPEC-05-scenario.md"


def art_rows():
    txt = SPEC.read_text()
    i = txt.index("### 5.2 Saltwell")
    seg = txt[i:i + 4000]
    rows = {}
    for ln in seg.splitlines():
        m = re.match(r"^\s*(\d+)\s*\|(.*)\|\s*$", ln)
        if m:
            rows[int(m.group(1))] = m.group(2)
    return rows


def main():
    rows = art_rows()
    m = json.load(open(ROOT / "SPEC" / "scenario" / "map1-saltwell.json"))
    tiles, cls, act = m["tiles"], m["action_class"], m["action_value"]
    print("art width", len(rows[0]), "map width", len(tiles[0]))
    for y in sorted(rows):
        art = rows[y]
        jt = "".join("%2d " % v for v in tiles[y])
        jc = "".join("%2d " % v for v in cls[y])
        print("y=%2d art : %s" % (y, art))
        print("      tile: %s" % jt)
        print("      cls : %s" % jc)
        # non-dot art chars and their map x under both alignments
        for x, ch in enumerate(art):
            if ch == ".":
                continue
            a0 = tiles[y][x] if x < len(tiles[y]) else None
            a1 = tiles[y][x + 1] if x + 1 < len(tiles[y]) else None
            print("      art[%2d]=%r  x0->tile %s cls %s | x+1->tile %s cls %s"
                  % (x, ch, a0, cls[y][x], a1, cls[y][x + 1]))


if __name__ == "__main__":
    main()
