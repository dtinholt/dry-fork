"""Probe 199: print source regions of interest (reads are budgeted).

Prints, for each (path, pattern) pair, every matching line with a little
context, so that the next iteration can inspect code without spending the
read budget.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump199.txt")
_buf = []


def out(s=""):
    _buf.append(str(s))


def show(path, pats, before=0, after=0, limit=400):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        out("MISSING " + path)
        return
    lines = open(full, encoding="utf-8", errors="replace").read().split("\n")
    hits = []
    for i, l in enumerate(lines):
        if any(p in l for p in pats):
            hits.append(i)
    shown = set()
    rows = []
    for i in hits:
        lo = max(0, i - before)
        hi = min(len(lines), i + after + 1)
        for j in range(lo, hi):
            if j in shown:
                continue
            shown.add(j)
            rows.append("%s:%d: %s" % (path, j + 1, lines[j]))
        rows.append("---")
    out("\n".join(rows[:limit]))


out("=== headless snapshot / cell changes ===")
show("src/wlengine/headless.py", ["def snapshot", "def sorted_cell_changes",
                                  "cell_changes.append", "def record_cell",
                                  "def bump", "def step", "def move"], before=2, after=14)

out("=== headless save/load ===")
show("src/wlengine/headless.py", ["def save", "def load", "def to_state", "def from_state",
                                  "def dump_state"], before=2, after=25)

out("=== scenario cactus / class ===")
show("src/wlengine/scenario.py", ["cactus", "class 11", "impassable", "walkable",
                                  "action_class", "def compile"], before=3, after=10)

out("=== combat orders / ammo ===")
show("src/wlengine/combat.py", ["reload", "def auto_orders", "ammo", "status",
                                "loaded", "def fire", "def jam"], before=3, after=12)

out("=== rules xp / rank ===")
show("src/wlengine/rules.py", ["xp_threshold", "rank", "skill_points", "promot",
                               "def level_after"], before=3, after=12)

out("=== files ===")
for d in ("SPEC", "SPEC/scenario", "src/wlengine"):
    full = os.path.join(ROOT, d)
    if os.path.isdir(full):
        out("%s %s" % (d, sorted(os.listdir(full))))

open(OUT, "w", encoding="utf-8").write("\n".join(_buf))
print("wrote", OUT, len(_buf), "lines")
