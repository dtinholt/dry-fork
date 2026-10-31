"""Probe: compare SPEC-05 Saltwell ASCII art with map1-saltwell.json tiles,
and dump the first move events of the walkthrough reference log."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "SPEC"

# --- extract the Saltwell art block from SPEC-05 -----------------------------
txt = (SPEC / "SPEC-05-scenario.md").read_text()
start = txt.index("### 5.2 Saltwell")
end = txt.index("Non-plain cells other than walls", start)
block = txt[start:end]
art = []
for line in block.splitlines():
    m = re.match(r"^\s*(\d+)\s+(\|.*\|)\s*$", line)
    if m:
        art.append((int(m.group(1)), m.group(2)))
print("art rows:", len(art))
for y, row in art[:3] + art[19:22]:
    print(y, len(row), row)

d = json.load(open(SPEC / "scenario" / "map1-saltwell.json"))
tiles = d["tiles"]
print("json rows:", len(tiles), "row len:", len(tiles[0]))

GLYPH = '.:"=,so~^bTYH*O%#_;/+nhPp|w`XGK>'
for y, row in art:
    jr = tiles[y]
    # try both alignments
    a = "".join(GLYPH[t] if t < len(GLYPH) else "?" for t in jr)
    print("y=%2d art=%s" % (y, row))
    print("      jsn=%s" % a)
    break

# full comparison for all rows, alignment 0 (x == index)
bad0 = []
for y, row in art:
    jr = tiles[y]
    a = "".join(GLYPH[t] if t < len(GLYPH) else "?" for t in jr)
    if a != row:
        bad0.append(y)
print("rows where json index==art column fails:", bad0)

# --- reference log -----------------------------------------------------------
ref = json.load(open(SPEC / "scenario" / "walkthrough-reference-log.json"))
ev = ref["events"]
print("note:", ref["note"])
for e in ev[:30]:
    print(json.dumps(e, sort_keys=True))
