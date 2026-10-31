"""probe463: raw repr of the SPEC-05 Saltwell ASCII art rows, and the
column of each non-plain glyph, to settle the off-by-one question.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
SCEN = SPEC / "scenario"

text = (SPEC / "SPEC-05-scenario.md").read_text()
i = text.index("### 5.2 Saltwell")
j = text.index("### 5.3", i)
sec = text[i:j]
lines = sec.splitlines()
# find the code fence
start = next(k for k, l in enumerate(lines) if l.strip() == "```text")
end = next(k for k, l in enumerate(lines[start + 1:], start + 1) if l.strip() == "```")
art = lines[start + 1:end]
print("art lines:", len(art))
for k, l in enumerate(art):
    print(k, repr(l))

# Now: for each art row, strip the prefix (everything before the first '|')
# and index interior chars.
print()
print("=== interior glyph columns (map x = interior index + 1) ===")
for k, l in enumerate(art):
    if "|" not in l:
        continue
    p = l.index("|")
    body = l[p:]
    if not body.endswith("|"):
        continue
    interior = body[1:-1]
    row = k - 2  # art rows 0,1 are the header lines
    marks = [(idx + 1, c) for idx, c in enumerate(interior) if c != "."]
    print("row %2d prefix=%r len=%d marks=%s" % (row, l[:p], len(body), marks))

# JSON comparison
m = json.loads((SCEN / "map1-saltwell.json").read_text())
print()
print("=== JSON non-plain cells per row (tile!=0 or class!=0) ===")
for y in range(m["height"]):
    marks = []
    for x in range(m["width"]):
        t = m["tiles"][y][x]
        c = m["action_class"][y][x]
        if t != 0 or c != 0:
            marks.append((x, t, c))
    print("row %2d %s" % (y, marks))
