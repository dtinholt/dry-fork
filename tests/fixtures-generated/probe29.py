"""Probe 29: is the JSON action_class [y][x] or [x][y]? Compare with the ASCII art."""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SCEN = PROJECT / "SPEC" / "scenario"

text = (PROJECT / "SPEC" / "SPEC-05-scenario.md").read_text(encoding="utf-8")
i = text.index("### 5.2 Saltwell")
j = text.index("### 5.3", i)
sec = text[i:j]
block = re.findall(r"```text\n(.*?)```", sec, re.S)[0]
lines = block.split("\n")
art = {}
for ln in lines[2:]:
    if not ln.strip():
        continue
    m = re.match(r"\s*(\d+)\s\s(.*)$", ln)
    if not m:
        print("no match:", repr(ln))
        continue
    y = int(m.group(1))
    art[y] = m.group(2)
print("art rows:", len(art), "widths:", sorted(set(len(v) for v in art.values())))

m = json.load(open(SCEN / "map1-saltwell.json"))
ac = m["action_class"]
tl = m["tiles"]
print("ac rows:", len(ac), "cols:", sorted(set(len(r) for r in ac)))
print("tl rows:", len(tl), "cols:", sorted(set(len(r) for r in tl)))

# glyph map
GLYPH = {".": 0, "|": 25, ";": 18, "Y": 11, "T": 0, "b": 0, "p": 0, "w": 0, "P": 0,
         "#": 25, "_": 0, "/": 0, "n": 0, "h": 0}

print()
print("row 20 art:", art[20])
print("row 20 json tiles:", tl[20])
print("row 20 json ac   :", ac[20])
print()
print("col 20 art:", "".join(art[y][20] for y in range(32)))
print("col 20 json tiles:", [tl[y][20] for y in range(32)])
print("col 20 json ac   :", [ac[y][20] for y in range(32)])
print()
# where is tile 11 in json?
for y in range(32):
    for x in range(32):
        if tl[y][x] == 11:
            print("json tile 11 at", x, y, "art glyph", art[y][x])
# where is Y in art?
for y in range(32):
    for x in range(32):
        if art[y][x] == "Y":
            print("art Y at", x, y, "json tile", tl[y][x], "json ac", ac[y][x])
