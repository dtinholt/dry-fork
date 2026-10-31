"""Probe 378: compare the SPEC-05 Saltwell ASCII map with the JSON arrays under
both index conventions, and dump the reference log's look events.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
MAP1 = os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")
REF = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")

GLYPH = {0: ".", 1: ".", 2: ".", 3: ".", 4: ".", 5: ".", 6: ".", 7: "~",
         8: "#", 9: "o", 10: "T", 11: "Y", 12: "=", 13: "t", 14: "c",
         15: "r", 16: "#", 17: "_", 18: ";", 19: "/", 20: "D", 21: "C",
         22: "H", 23: "P", 24: "p", 25: "|", 26: "O", 27: "_", 28: "#",
         29: "G", 30: "S", 31: "s"}


def spec_ascii():
    lines = open(SPEC).read().splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("00000000001111111111222222222233"):
            start = i
            break
    rows = []
    for ln in lines[start + 2:start + 2 + 32]:
        m = re.match(r"\s*(\d+)\s+(.*)$", ln)
        rows.append(m.group(2))
    return rows


def render(grid):
    out = []
    for y in range(32):
        out.append("".join(GLYPH.get(grid[y][x], "?") for x in range(32)))
    return out


def main():
    d = json.load(open(MAP1))
    t = d["tiles"]
    spec = spec_ascii()
    print("spec rows:", len(spec), "len", len(spec[0]))
    yx = render(t)
    xy = render([[t[x][y] for x in range(32)] for y in range(32)])
    for name, grid in (("[y][x]", yx), ("[x][y]", xy)):
        diff = [y for y in range(32) if grid[y] != spec[y]]
        print(name, "rows differing from spec:", diff[:10], "count", len(diff))
    print("spec row 20:", spec[20])
    print("yx   row 20:", yx[20])
    print("xy   row 20:", xy[20])
    print("spec row 9 :", spec[9])
    print("yx   row 9 :", yx[9])
    print("xy   row 9 :", xy[9])
    # reference log look events
    ev = json.load(open(REF))["events"]
    looks = [e for e in ev if e.get("type") == "look"]
    print("look events:", len(looks))
    for e in looks[:6]:
        print(json.dumps(e, sort_keys=True)[:600])


main()
