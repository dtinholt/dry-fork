"""Compare the SPEC-05 Saltwell drawing with the scenario JSON grid."""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SC = os.path.join(ROOT, "SPEC", "scenario")


def parse_drawing():
    text = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")).read()
    i = text.index("### 5.2 Saltwell")
    j = text.index("Non-plain cells", i)
    seg = text[i:j]
    rows = {}
    for line in seg.split("\n"):
        m = re.match(r"^\s*(\d+)\s+\|(.*)\|\s*$", line)
        if m:
            rows[int(m.group(1))] = m.group(2)
    return rows


def main():
    rows = parse_drawing()
    print("drawing rows:", sorted(rows))
    for y in sorted(rows):
        print("%2d len=%d %s" % (y, len(rows[y]), rows[y]))
    d = json.load(open(os.path.join(SC, "map1-saltwell.json")))
    print("json keys:", list(d.keys()))
    ac = d["action_class"]
    print("ac shape", len(ac), len(ac[0]))
    print("tiles shape", len(d["tiles"]), len(d["tiles"][0]) if d.get("tiles") else None)
    print("tiles row 20:", d["tiles"][20])
    print("ac row 20:", ac[20])
    print("ac row 11:", ac[11])
    print("ac row 3:", ac[3])
    # compare drawing glyphs with class
    for y in sorted(rows):
        line = rows[y]
        for x, ch in enumerate(line):
            if ch not in ".|":
                cls = ac[y][x] if y < len(ac) and x < len(ac[y]) else None
                print("(%2d,%2d) glyph=%r class=%s" % (x, y, ch, cls))


if __name__ == "__main__":
    main()
