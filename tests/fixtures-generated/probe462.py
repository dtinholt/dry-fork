"""probe462: compare SPEC-05 ASCII map art with SPEC/scenario/map1-saltwell.json.

Goal: find the exact column shift that makes the frozen tests (M5 bump at
(2,20), M6 look west from (15,20) -> image 28) agree with the compiled map.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
SCEN = SPEC / "scenario"


def load_map(name):
    return json.loads((SCEN / name).read_text())


def ascii_rows():
    """Extract the ASCII map art for Saltwell (location 1) from SPEC-05."""
    text = (SPEC / "SPEC-05-scenario.md").read_text()
    # find the Saltwell section
    i = text.index("### 5.2 Saltwell")
    j = text.index("### 5.3", i)
    sec = text[i:j]
    rows = []
    for line in sec.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and len(s) > 20:
            rows.append(s)
    return rows


def main():
    m = load_map("map1-saltwell.json")
    print("keys:", sorted(m.keys()))
    print("width", m.get("width"), "height", m.get("height"))
    print("conventions:", m.get("conventions"))
    rows = ascii_rows()
    print("ascii rows found:", len(rows))
    for k, r in enumerate(rows[:6]):
        print("ascii[%d] len=%d %r" % (k, len(r), r))
    # print row 20 of each array
    for key in ("tiles", "action_class", "action_value", "image"):
        if key in m:
            print(key, "row20:", m[key][20])
    # find the ';' (road) column in ascii row 20
    if len(rows) > 20:
        r = rows[20]
        print("ascii row20:", r)
        print("';' at string idx:", [i for i, c in enumerate(r) if c == ";"])
        print("'|' at string idx:", [i for i, c in enumerate(r) if c == "|"])
    # find image 28 in json
    if "image" in m:
        for y, row in enumerate(m["image"]):
            cols = [x for x, v in enumerate(row) if v == 28]
            if cols:
                print("image 28 at y=%d x=%s" % (y, cols))
    # find class 11 (blocked) cells
    for y, row in enumerate(m["action_class"]):
        cols = [x for x, v in enumerate(row) if v == 11]
        if cols:
            print("class 11 at y=%d x=%s" % (y, cols))


if __name__ == "__main__":
    main()
