"""Probe 366: parse the SPEC-05 5.2 ASCII map carefully and compare it with the
frozen map1-saltwell.json tiles, to find the true cactus coordinate.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")


def main():
    with open(SPEC, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"### 5\.2 Saltwell.*?```text\n(.*?)```", text, re.S)
    art = m.group(1).splitlines()
    print("n lines", len(art))
    for i, l in enumerate(art[:6]):
        print(i, len(l), repr(l))
    print("...")
    for i, l in enumerate(art[-3:], len(art) - 3):
        print(i, len(l), repr(l))
    # rows are art[2:]
    rows = art[2:]
    print("n rows", len(rows), "widths", sorted({len(r) for r in rows}))
    for y in (17, 19, 20):
        r = rows[y]
        print("row %d len %d %r" % (y, len(r), r))
        print("   chars:", list(r))
    # find the cactus glyph 'Y'
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "Y":
                print("Y at row %d col %d" % (y, x))


main()
