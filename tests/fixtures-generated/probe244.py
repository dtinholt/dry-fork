"""Probe 244: extract the SPEC-05 Saltwell art and compare with the JSON."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent

txt = (ROOT / "SPEC" / "SPEC-05-scenario.md").read_text().splitlines()
# find the Saltwell art block: lines starting with "  0  |" ... " 31  ||"
start = None
for i, ln in enumerate(txt):
    if re.match(r"^\s+0\s+\|", ln):
        start = i
        break
lines = []
for ln in txt[start:start + 40]:
    m = re.match(r"^\s+(\d+)\s+(.*)$", ln)
    if not m:
        break
    lines.append((int(m.group(1)), m.group(2)))

d = json.loads((ROOT / "SPEC" / "scenario" / "map1-saltwell.json").read_text())
out = []
for y, art in lines:
    tiles = d["tiles"][y]
    cls = d["action_class"][y]
    # art: '|' wall, '.' plain, ';' path, 'Y' cactus, '#' building, '_' floor, etc.
    diff = []
    for x, ch in enumerate(art):
        t = tiles[x]
        if ch == "|" and t != 25:
            diff.append((x, ch, t))
        elif ch == "." and t != 0:
            diff.append((x, ch, t))
        elif ch == "Y" and t != 11:
            diff.append((x, ch, t))
        elif ch == ";" and t != 18:
            diff.append((x, ch, t))
    out.append("y=%2d art=%s" % (y, art))
    out.append("      tiles=%s" % tiles)
    if diff:
        out.append("      DIFF: %s" % diff)
    else:
        out.append("      ok")

(OUT / "dump248.txt").write_text("\n".join(out))
print("ok", len(lines))
