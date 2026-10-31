"""Compare the SPEC-05 ASCII art rows with the map JSON arrays."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = (ROOT / "SPEC" / "SPEC-05-scenario.md").read_text().splitlines()

out = []
# find the Saltwell art block: lines that start with "  NN  " and contain '|'
start = None
for i, ln in enumerate(spec):
    if ln.strip().startswith("00000000001111111111222222222233"):
        start = i
        break
out.append("header line index %r" % start)
for j in range(start, start + 36):
    ln = spec[j]
    out.append("%3d |%s| len=%d" % (j, ln, len(ln)))

# Saltwell art: the second header
hdr = [i for i, ln in enumerate(spec) if ln.strip().startswith("00000000001111111111222222222233")]
out.append("headers at %r" % hdr)
h = hdr[1] if len(hdr) > 1 else hdr[0]
out.append("=== saltwell art (header %d) ===" % h)
rows = {}
for j in range(h + 1, h + 34):
    ln = spec[j]
    m = re.match(r"^\s*(\d+)\s+(.*)$", ln)
    if not m:
        out.append("skip %r" % ln)
        continue
    y = int(m.group(1))
    body = m.group(2)
    rows[y] = body
    out.append("y=%2d len=%2d %r" % (y, len(body), body))

d = json.loads((ROOT / "SPEC" / "scenario" / "map1-saltwell.json").read_text())
ac = d["action_class"]
tiles = d["tiles"]
out.append("=== JSON action_class rows 18..22 ===")
for y in range(18, 23):
    out.append("y=%2d %r" % (y, ac[y]))
out.append("=== JSON tiles rows 18..22 ===")
for y in range(18, 23):
    out.append("y=%2d %r" % (y, tiles[y]))

# Where is tile 11 (cactus) in the JSON?
out.append("=== tile 11 positions ===")
pos = [(x, y) for y in range(32) for x in range(32) if tiles[y][x] == 11]
out.append(repr(pos))
out.append("=== class 11 positions ===")
pos = [(x, y) for y in range(32) for x in range(32) if ac[y][x] == 11]
out.append(repr(pos))

# ASCII art: where is 'Y'?
out.append("=== 'Y' positions in the art ===")
pos = [(x, y) for y, body in rows.items() for x, ch in enumerate(body) if ch == "Y"]
out.append(repr(sorted(pos)))
out.append("=== ';' positions in the art ===")
pos = [(x, y) for y, body in rows.items() for x, ch in enumerate(body) if ch == ";"]
out.append(repr(sorted(pos)[:40]))

Path(__file__).with_name("dump175.txt").write_text("\n".join(out))
print("wrote dump175.txt")
