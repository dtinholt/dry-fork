"""Probe 169: compare SPEC-05 ASCII art rows with the JSON tiles/action_class.

Run: python3 tests/fixtures-generated/probe169.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPEC = os.path.join(ROOT, "SPEC")

GLYPH = {0: ".", 1: ":", 2: '"', 3: "=", 4: ",", 5: "s", 6: "o", 7: "~",
         8: "^", 9: "b", 10: "T", 11: "Y", 12: "H", 13: "*", 14: "O", 15: "%",
         16: "#", 17: "_", 18: ";", 19: "/", 20: "+", 21: "n", 22: "h",
         23: "P", 24: "p", 25: "|", 26: "w", 27: "`", 28: "X", 29: "G",
         30: "K", 31: ">"}


def art_rows(spec_text, heading, nrows):
    i = spec_text.find(heading)
    seg = spec_text[i:i + 6000]
    rows = {}
    for line in seg.splitlines():
        m = re.match(r"^\s*(\d+)\s*\|(.*)\|\s*$", line)
        if m:
            rows[int(m.group(1))] = m.group(2)
    return rows


def main():
    text = open(os.path.join(SPEC, "SPEC-05-scenario.md")).read()
    for loc, heading, fn, n in ((0, "### 5.1 Dry Fork overworld", "map0-overworld.json", 64),
                                (1, "### 5.2 Saltwell", "map1-saltwell.json", 32),
                                (2, "### 5.3 Ninemile", "map2-ninemile.json", 32),
                                (3, "### 5.4 Pumphouse Deep", "map3-pumphouse.json", 32)):
        d = json.load(open(os.path.join(SPEC, "scenario", fn)))
        rows = art_rows(text, heading, n)
        print("=== location %d (%s) art rows %d ===" % (loc, fn, len(rows)))
        bad = 0
        for y in sorted(rows):
            art = rows[y]
            tiles = d["tiles"][y]
            g = "".join(GLYPH.get(t, "?") for t in tiles)
            if art != g:
                bad += 1
                if bad <= 6:
                    print("y=%2d art %s" % (y, art))
                    print("     jsn %s" % g)
        print("mismatched rows:", bad)


if __name__ == "__main__":
    main()
