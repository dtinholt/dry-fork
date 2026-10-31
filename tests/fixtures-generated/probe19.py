"""Probe 19: compare the JSON map arrays with the SPEC-05 ASCII art.

Run:  python3 tests/fixtures-generated/probe19.py
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))


def spec_art(name):
    txt = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")).read()
    i = txt.index("### 5.2 Saltwell")
    j = txt.index("Non-plain cells other than walls", i)
    rows = []
    for line in txt[i:j].split("\n"):
        if re.match(r"^\s*\d+\s", line):
            rows.append(line.split(None, 1)[1])
    return rows


def main():
    art = spec_art("saltwell")
    d = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
    cls = d["action_class"]
    til = d["tiles"]
    print("art rows", len(art), "json rows", len(cls))
    for y in range(len(cls)):
        a = art[y]
        # render json row as chars
        row = []
        for x in range(len(cls[y])):
            c = cls[y][x]
            t = til[y][x]
            if c == 11:
                row.append("|" if t == 25 else "Y")
            elif c == 0:
                row.append("." if t == 0 else "?")
            else:
                row.append(str(c))
        js = "".join(row)
        if js != a:
            print("y=%2d art %s" % (y, a))
            print("      js  %s" % js)
    print("=" * 70)
    print("raw json action_class row 20:", json.dumps(cls[20]))
    print("raw json tiles row 20:", json.dumps(til[20]))
    print("=" * 70)
    # reference log bumps
    ref = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")))
    ev = ref if isinstance(ref, list) else ref.get("events")
    for e in ev:
        if e.get("type") == "bump":
            print("ref bump", e)
    print("=" * 70)
    wt = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough.json")))
    print(json.dumps(wt["script"])[:3000])


if __name__ == "__main__":
    main()
