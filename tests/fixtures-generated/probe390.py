"""Probe: align the SPEC-05 Saltwell art with the JSON tiles."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "SPEC"
txt = (SPEC / "SPEC-05-scenario.md").read_text()
start = txt.index("### 5.2 Saltwell")
end = txt.index("Non-plain cells other than walls", start)
block = txt[start:end]
art = []
for line in block.splitlines():
    m = re.match(r"^\s*(\d+)\s+(\|.*\|)\s*$", line)
    if m:
        art.append((int(m.group(1)), m.group(2)))
print("art rows", len(art), "inner widths", sorted({len(r) - 2 for _, r in art}))
for y, row in art[:2]:
    print(repr(row))
print("row20 repr:", repr(dict(art)[20]))
print("row20 inner idx:", [(i, c) for i, c in enumerate(dict(art)[20][1:-1]) if c != "."])

d = json.load(open(SPEC / "scenario" / "map1-saltwell.json"))
tiles = d["tiles"]
GLYPH = '.:"=,so~^bTYH*O%#_;/+nhPp|w`XGK>'
jsn = ["".join(GLYPH[t] if t < len(GLYPH) else "?" for t in row) for row in tiles]
print("json row20:", jsn[20])
print("json row20 idx:", [(i, c) for i, c in enumerate(jsn[20]) if c != "."])

# try offsets: art inner char i corresponds to json column i + off
for off in range(-3, 4):
    bad = 0
    for y, row in art:
        inner = row[1:-1]
        for i, c in enumerate(inner):
            j = i + off
            if 0 <= j < len(jsn[y]):
                if jsn[y][j] != c:
                    bad += 1
            else:
                bad += 1
    print("offset", off, "mismatches", bad)
