"""Probe 25: compare the SPEC-05 ASCII art of Saltwell with the JSON tiles
array, column by column, to find any shift."""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SPEC = os.path.join(ROOT, "SPEC")


def art_rows():
    txt = open(os.path.join(SPEC, "SPEC-05-scenario.md")).read().split("\n")
    start = next(i for i, l in enumerate(txt) if l.strip().startswith("### 5.2 Saltwell"))
    rows = {}
    for l in txt[start:start + 60]:
        m = re.match(r"^\s*(\d+)\s+\|(.*)\|\s*$", l)
        if m:
            rows[int(m.group(1))] = m.group(2)
    return rows


def main():
    rows = art_rows()
    j = json.load(open(os.path.join(SPEC, "scenario", "map1-saltwell.json")))
    tiles = j["tiles"]
    cls = j["action_class"]
    # tile id -> art char, guessed from the legend
    for y in sorted(rows):
        art = rows[y]
        tj = tiles[y]
        # find columns where art char is not '.' and not '|'
        marks = [(x, c) for x, c in enumerate(art) if c not in ".|"]
        tmarks = [(x, t) for x, t in enumerate(tj) if t not in (0, 25)]
        print("y=%2d art=%s" % (y, marks))
        print("      jsn=%s" % (tmarks,))


if __name__ == "__main__":
    main()
