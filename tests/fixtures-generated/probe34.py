"""Probe 34: test the nibble-swap hypothesis for the class array.

Hypothesis A (current engine): class(x,y) = high nibble of byte (y*S+x)>>1 when
x is even, low nibble when x is odd.
Hypothesis B (swapped): class(x,y) = low nibble when x is even, high when odd.

Check both against every bump and cell_change in the reference log, and against
the SPEC-05 Saltwell ASCII art.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SCEN = PROJECT / "SPEC" / "scenario"

ref = json.load(open(SCEN / "walkthrough-reference-log.json"))["events"]
maps = {}
for loc, f in ((0, "map0-overworld.json"), (1, "map1-saltwell.json"),
               (2, "map2-ninemile.json"), (3, "map3-pumphouse.json")):
    maps[loc] = json.load(open(SCEN / f))


def cls_at(m, x, y, swap):
    row = m["action_class"][y]
    if swap:
        return row[x + 1] if x % 2 == 0 else row[x - 1]
    return row[x]


def act_at(m, x, y, swap):
    row = m["action_value"][y]
    if swap:
        return row[x + 1] if x % 2 == 0 else row[x - 1]
    return row[x]


print("== bumps: which hypothesis matches? ==")
for e in ref:
    if e.get("type") != "bump":
        continue
    x, y = e["x"], e["y"]
    hits = []
    for loc, m in maps.items():
        for swap in (False, True):
            if cls_at(m, x, y, swap) == e["action_class"] and act_at(m, x, y, swap) == e["action"]:
                hits.append((loc, "swap" if swap else "plain"))
    print("bump (%d,%d) cls %d act %d -> %s" % (x, y, e["action_class"], e["action"], hits))

print()
print("== saltwell row 20 under both hypotheses ==")
m = maps[1]
print("plain:", [cls_at(m, x, 20, False) for x in range(8)])
print("swap :", [cls_at(m, x, 20, True) for x in range(8)])
print("tiles:", m["tiles"][20][:8])

print()
print("== saltwell art vs both hypotheses (class 11 where non-walkable) ==")
text = (PROJECT / "SPEC" / "SPEC-05-scenario.md").read_text(encoding="utf-8")
i = text.index("### 5.2 Saltwell")
j = text.index("### 5.3", i)
block = re.findall(r"```text\n(.*?)```", text[i:j], re.S)[0]
art = {}
for ln in block.split("\n"):
    if not ln.strip():
        continue
    mm = re.match(r"\s*(\d+)\s\s(.*)$", ln)
    if mm:
        art[int(mm.group(1))] = mm.group(2)
for swap in (False, True):
    bad = []
    for y in range(32):
        for x in range(32):
            g = art[y][x]
            want = 11 if g in "|#_/n hYTPwb" else 0
            got = cls_at(m, x, y, swap)
            if want != got:
                bad.append((x, y, g, want, got))
    print("swap=%s mismatches=%d first=%s" % (swap, len(bad), bad[:6]))
