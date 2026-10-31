"""Parse the Saltwell ASCII art from SPEC-05 and compare with the JSON map.

Usage: python3 tests/fixtures-generated/probe39.py
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
    tiles = m["tiles"]
    cls = m["action_class"]
    act = m["action_value"]
    for y in sorted(rows):
        art = rows[y]
        print("row %2d len=%d" % (y, len(art)))
        for x, ch in enumerate(art):
            if ch not in ".":
                jt = tiles[y][x] if x < len(tiles[y]) else None
                print("   x=%2d art=%r json tile=%s cls=%s act=%s"
                      % (x, ch, jt, cls[y][x], act[y][x]))
    # where is tile 11 (cactus) in the JSON?
    print("tile 11 cells:", [(x, y) for y in range(len(tiles)) for x in range(len(tiles[y]))
                             if tiles[y][x] == 11])
    print("class 11 cells:", [(x, y) for y in range(len(cls)) for x in range(len(cls[y]))
                              if cls[y][x] == 11][:40])


if __name__ == "__main__":
    main()
