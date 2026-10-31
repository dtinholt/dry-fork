"""Probe 201: save path, victory/loot, and reference events around the fight."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump201.txt")
buf = []


def out(s=""):
    buf.append(str(s))


def show(path, pats, before=2, after=20, limit=600):
    full = os.path.join(ROOT, path)
    lines = open(full, encoding="utf-8", errors="replace").read().split("\n")
    hits = [i for i, l in enumerate(lines) if any(p in l for p in pats)]
    shown, rows = set(), []
    for i in hits:
        for j in range(max(0, i - before), min(len(lines), i + after + 1)):
            if j in shown:
                continue
            shown.add(j)
            rows.append("%s:%d: %s" % (path, j + 1, lines[j]))
        rows.append("---")
    out("\n".join(rows[:limit]))


out("=== headless: save / labstate / victory / loot ===")
show("src/wlengine/headless.py",
     ["def save", "labstate", "def victory", "def loot", "def combat_end",
      "def end_combat", "def win", "def do_save", "def write_save"],
     before=3, after=30)

out("=== reference events 430..480 ===")
ref = json.load(open(os.path.join(ROOT, "SPEC", "scenario",
                                  "walkthrough-reference-log.json")))
for i, e in enumerate(ref["events"]):
    if 425 <= i <= 480:
        out("%d: %s" % (i, json.dumps(e)[:400]))

out("=== reference events 120..140 (first cell change) ===")
for i, e in enumerate(ref["events"]):
    if 120 <= i <= 140:
        out("%d: %s" % (i, json.dumps(e)[:300]))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
