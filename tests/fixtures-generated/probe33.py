"""Probe 33: compare art glyph positions with JSON tile positions per row."""
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
art = {}
for ln in block.split("\n"):
    if not ln.strip():
        continue
    m = re.match(r"\s*(\d+)\s\s(.*)$", ln)
    art[int(m.group(1))] = m.group(2)

m = json.load(open(SCEN / "map1-saltwell.json"))
tl = m["tiles"]
ac = m["action_class"]

# glyph -> tile id, from the SPEC-05 tile table + art legend
G = {".": 0, ";": 18, "Y": 11, "T": 10, "b": 9, "p": 24, "w": 7, "P": 23,
     "#": 16, "_": 17, "/": 19, "n": 21, "h": 22, "|": 25}

for y in range(32):
    a = art[y]
    jrow = tl[y]
    diffs = []
    for x in range(32):
        want = G.get(a[x])
        if want is None:
            diffs.append("x=%d unknown %r" % (x, a[x]))
        elif want != jrow[x]:
            diffs.append("x=%d art %r(%d) json %d" % (x, a[x], want, jrow[x]))
    if diffs:
        print("row %2d: %s" % (y, "; ".join(diffs)))
