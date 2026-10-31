"""Probe 49: index the SPEC-05 Saltwell art precisely and compare with the JSON
tiles/action_class arrays, and read maps.is_passable."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"


def art_rows():
    txt = (ROOT / "SPEC" / "SPEC-05-scenario.md").read_text()
    i = txt.index("### 5.2 Saltwell")
    j = txt.index("Non-plain cells", i)
    block = txt[i:j]
    rows = []
    for line in block.splitlines():
        m = re.match(r"^\s*(\d+)\s*\|(.*)\|\s*$", line)
        if m:
            rows.append((int(m.group(1)), m.group(2)))
    return rows


def main():
    rows = art_rows()
    print("art rows:", len(rows))
    for y, s in rows:
        print("%2d len=%d %r" % (y, len(s), s))
    d = json.loads((SCEN / "map1-saltwell.json").read_text())
    tl = d["tiles"]
    ac = d["action_class"]
    print("== compare art vs JSON tiles ==")
    for y, s in rows:
        for x, ch in enumerate(s):
            if ch in ".#|":
                continue
            jt = tl[y][x]
            jc = ac[y][x]
            print("  (%2d,%2d) art %r json tile %3d class %d" % (x, y, ch, jt, jc))


if __name__ == "__main__":
    main()
