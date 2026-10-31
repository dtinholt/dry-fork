"""Probe 208: SPEC-03 9.2/9.8/9.9, SPEC-05 5.6, M4 cell checks, fixtures_gen
scenario compiler, map2 healer cot."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump208.txt")
buf = []


def out(s=""):
    buf.append(str(s))


def section(path, heading, nlines=90):
    full = os.path.join(ROOT, path)
    ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
    for i, l in enumerate(ls):
        if l.strip().startswith("#") and heading.lower() in l.lower():
            out("=== %s :: %s (line %d) ===" % (path, heading, i + 1))
            out("\n".join("%d: %s" % (j + 1, ls[j]) for j in range(i, min(len(ls), i + nlines))))
            return
    out("NOT FOUND %s in %s" % (heading, path))


section("SPEC/SPEC-03-maps.md", "9.2 Action byte and tables", 70)
section("SPEC/SPEC-03-maps.md", "9.9 Encoder rules for lab map blocks", 70)
section("SPEC/SPEC-05-scenario.md", "5.6 Encoding checks", 60)

out("=== test_m4_scenario.py cell checks ===")
full = os.path.join(ROOT, "tests", "test_m4_scenario.py")
ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
for i, l in enumerate(ls):
    if any(p in l for p in ("action_class", "actionClass", "cells", "tiles", "def test_", "class 11")):
        out("%d: %s" % (i + 1, l))

out("=== fixtures_gen.py: scenario compile? ===")
full = os.path.join(ROOT, "SPEC", "reference", "fixtures_gen.py")
ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
for i, l in enumerate(ls):
    if any(p in l for p in ("def ", "class ", "action_class", "walkable", "impassable", "class 11")):
        out("%d: %s" % (i + 1, l))

out("=== oracle_tool.py: scenario compile? ===")
full = os.path.join(ROOT, "tests", "oracle_tool.py")
ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
for i, l in enumerate(ls):
    if any(p in l for p in ("def ", "class ", "action_class", "walkable", "impassable")):
        out("%d: %s" % (i + 1, l))

m2 = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map2-ninemile.json")))
out("=== map2 action_cells ===")
out(json.dumps(m2["action_cells"])[:2000])
out("map2 tiles row 21: %s" % m2["tiles"][21])
out("map2 action_class row 21: %s" % m2["action_class"][21])

tiles = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "tiles.json")))
out("=== tiles.json ===")
out(json.dumps(tiles)[:3000])

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
