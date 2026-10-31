"""probe470: compare SPEC-05 5.2 ASCII art with map1 JSON, and check the
reference log's moves/bumps against the JSON map."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")

GLYPH = {'.': 0, ':': 1, '"': 2, '=': 3, ',': 4, 's': 5, 'o': 6, '~': 7, '^': 8,
         'b': 9, 'T': 10, 'Y': 11, 'H': 12, '*': 13, 'O': 14, '%': 15, '#': 16,
         '_': 17, ';': 18, '/': 19, '+': 20, 'n': 21, 'h': 22, 'P': 23, 'p': 24,
         '|': 25, 'w': 26, '`': 27, 'X': 28, 'G': 29, 'K': 30, '>': 31}

s5 = open(os.path.join(SPEC, "SPEC-05-scenario.md")).read()
j = s5.find("### 5.2 Saltwell")
k = s5.find("### 5.3", j)
block = s5[j:k]
rows = {}
for line in block.splitlines():
    mm = re.match(r"^\s*(\d+)\s+(.*)$", line)
    if mm:
        rows[int(mm.group(1))] = mm.group(2)
print("=== ascii row lengths:", {y: len(r) for y, r in sorted(rows.items())})
for y in sorted(rows):
    print(y, repr(rows[y]))

m1 = json.load(open(os.path.join(SPEC, "scenario", "map1-saltwell.json")))
tiles = m1["tiles"]
ac = m1["action_class"]
av = m1["action_value"]

print("=== ascii vs json tiles mismatches (art index -> json index) ===")
for y in sorted(rows):
    art = rows[y]
    for x, ch in enumerate(art):
        want = GLYPH.get(ch)
        got = tiles[y][x] if x < len(tiles[y]) else None
        if want is not None and want != got:
            print("row %d col %d: art %r=%d json=%s" % (y, x, ch, want, got))

print("=== ascii vs json action_class (class 11 where art is non-walkable) ===")
# just print rows where json class != 0 and art char
for y in sorted(rows):
    art = rows[y]
    for x, ch in enumerate(art):
        if ac[y][x] != 0:
            print("row %d col %d: art %r tile=%d class=%d val=%d" % (y, x, ch, tiles[y][x], ac[y][x], av[y][x]))

print("=== reference log events for location 1 (moves/bumps) ===")
ref = json.load(open(os.path.join(SPEC, "scenario", "walkthrough-reference-log.json")))
for e in ref["events"]:
    t = e.get("type")
    if t == "move" and e.get("location") == 1:
        x, y = e["x"], e["y"]
        print("move  (%2d,%2d) tile=%d class=%d val=%d" % (x, y, tiles[y][x], ac[y][x], av[y][x]))
    elif t == "bump":
        x, y = e["x"], e["y"]
        print("BUMP  (%2d,%2d) tile=%d class=%d val=%d  (log says class=%d action=%d)" % (
            x, y, tiles[y][x], ac[y][x], av[y][x], e["action_class"], e["action"]))
