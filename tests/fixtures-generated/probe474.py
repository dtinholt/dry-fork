"""Probe 474: extract the SPEC-05 5.2 Saltwell ASCII map and print the exact
column index of every non-'.' character, then compare with the frozen JSON
tiles, to settle whether the ASCII has the cactus at x=2 or x=3 and the road at
x=14 or x=15."""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    spec = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
    with open(spec, encoding="utf-8") as fh:
        text = fh.read()
    idx = text.find("### 5.2 Saltwell")
    chunk = text[idx:idx + 3000]
    m = re.search(r"```text\n(.*?)```", chunk, re.S)
    block = m.group(1)
    rows = block.splitlines()
    print("ASCII block rows:", len(rows))
    for r in rows:
        print(repr(r))
    print()
    # rows[0] is the column header, rows[1] the tens header, rows[2..] the map
    for r in rows[2:]:
        m2 = re.match(r"\s*(\d+)\s+(.*)$", r)
        if not m2:
            continue
        y = int(m2.group(1))
        body = m2.group(2)
        marks = [(i, c) for i, c in enumerate(body) if c not in ".|"]
        pipes = [i for i, c in enumerate(body) if c == "|"]
        print("y=%2d len=%d pipes=%s marks=%s" % (y, len(body), pipes[:4], marks))

    print()
    d = json.load(open(os.path.join(SCEN, "map1-saltwell.json"), encoding="utf-8"))
    tiles = d["tiles"]
    for y in (11, 20, 31):
        marks = [(x, t) for x, t in enumerate(tiles[y]) if t != 0]
        print("JSON y=%2d marks=%s" % (y, marks))


if __name__ == "__main__":
    main()
