"""Probe 367: compare the SPEC-05 5.2 ASCII art with map1-saltwell.json tiles.

Parses the art (x=0 at raw index 5) and reports every mismatch against the
JSON tiles array, plus the glyph->tile mapping inferred from the art.
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
SCEN = os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")

GLYPH = {"|": 25, ".": 0, ";": 18, "#": 16, "_": 17, "/": 19, "Y": 11, "T": 10,
         "P": 23, "p": 24, "b": 22, "w": 26, "n": 21, "h": 21}


def main():
    with open(SPEC, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"### 5\.2 Saltwell.*?```text\n(.*?)```", text, re.S)
    art = m.group(1).splitlines()
    rows = art[2:]
    with open(SCEN, encoding="utf-8") as fh:
        j = json.load(fh)
    tiles = j["tiles"]
    acls = j["action_class"]
    bad = 0
    for y, line in enumerate(rows):
        body = line[5:37]
        if len(body) != 32:
            print("row %d bad length %d" % (y, len(body)))
            continue
        for x, ch in enumerate(body):
            want = GLYPH.get(ch)
            got = tiles[y][x]
            if want is None:
                print("row %d x=%d unknown glyph %r (json %d)" % (y, x, ch, got))
                bad += 1
            elif want != got:
                print("MISMATCH row %d x=%d glyph %r json tile %d cls %d" % (y, x, ch, got, acls[y][x]))
                bad += 1
    print("total mismatches:", bad)
    # print rows 18..22 with indices
    for y in range(18, 23):
        print("y=%d art %r" % (y, rows[y][5:37]))
        print("     json %s" % (tiles[y],))


main()
