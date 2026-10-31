"""Probe 30: full comparison of the Saltwell ASCII art against the JSON tiles."""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SCEN = PROJECT / "SPEC" / "scenario"

text = (PROJECT / "SPEC" / "SPEC-05-scenario.md").read_text(encoding="utf-8")
i = text.index("### 5.2 Saltwell")
j = text.index("### 5.3", i)
block = re.findall(r"```text\n(.*?)```", text[i:j], re.S)[0]
lines = block.split("\n")
art = {}
for ln in lines[2:]:
    if not ln.strip():
        continue
    m = re.match(r"\s*(\d+)\s\s(.*)$", ln)
    art[int(m.group(1))] = m.group(2)

m = json.load(open(SCEN / "map1-saltwell.json"))
tl = m["tiles"]
ac = m["action_class"]

GLYPH = {".": 0, "|": 25, ";": 18, "Y": 11, "T": 10, "b": 9, "p": 23, "w": 26,
         "P": 24, "#": 25, "_": 27, "/": 29, "n": 31, "h": 22}

bad = 0
for y in range(32):
    for x in range(32):
        g = art[y][x]
        want = GLYPH.get(g)
        got = tl[y][x]
        if want is None:
            print("unknown glyph %r at %d,%d json tile %d" % (g, x, y, got))
            continue
        if want != got:
            bad += 1
            print("mismatch at (%d,%d): art %r -> tile %d, json tile %d (ac %d)"
                  % (x, y, g, want, got, ac[y][x]))
print("mismatches:", bad)

# also compare the class: non-walkable tiles should be class 11 unless listed
WALK = {0, 1, 2, 3, 4, 5, 6, 12, 13, 14, 23, 27, 28, 29, 31}
bad2 = 0
for y in range(32):
    for x in range(32):
        t = tl[y][x]
        c = ac[y][x]
        if t not in WALK and c == 0:
            bad2 += 1
            print("non-walkable tile %d at (%d,%d) but class 0" % (t, x, y))
print("class mismatches:", bad2)
