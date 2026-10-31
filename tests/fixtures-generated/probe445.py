"""probe445: raw dump of JSON rows vs ASCII rows for Saltwell, plus the first
events of the reference log, to find the true coordinate convention."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")

text = open(os.path.join(SPEC, "SPEC-05-scenario.md"), encoding="utf-8").read()
m = re.search(r"### 5\.2 Saltwell.*?```text\n(.*?)```", text, re.S)
art = m.group(1).splitlines()
rows = {}
for line in art:
    mm = re.match(r"\s*(\d+)\s\s(.*)$", line)
    if mm:
        rows[int(mm.group(1))] = mm.group(2)

d = json.load(open(os.path.join(SPEC, "scenario", "map1-saltwell.json"), encoding="utf-8"))
tiles = d["tiles"]
ac = d["action_class"]
av = d["action_value"]
acells = d.get("action_cells")

print("width/height:", d["width"], d["height"])
print("len(tiles):", len(tiles), "widths:", sorted(set(len(r) for r in tiles)))
print("len(ac):", len(ac), "widths:", sorted(set(len(r) for r in ac)))
print("action_cells:", json.dumps(acells)[:400] if acells is not None else None)

for y in (11, 20, 31):
    s = rows[y]
    print("--- row %d ---" % y)
    print("ascii len", len(s), repr(s))
    print("json  len", len(tiles[y]), tiles[y])
    print("ac        ", ac[y])
    print("av        ", av[y])
    print("idx       ", "".join(str(x % 10) for x in range(len(tiles[y]))))

log = json.load(open(os.path.join(SPEC, "scenario", "walkthrough-reference-log.json"), encoding="utf-8"))
ev = log["events"]
print("--- first 40 reference events ---")
for e in ev[:40]:
    print(json.dumps(e, sort_keys=True))
