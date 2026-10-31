"""Probe 202: spec text for ammo/orders + the test consistency checker."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump202.txt")
buf = []


def out(s=""):
    buf.append(str(s))


def section(path, heading, nlines=120):
    full = os.path.join(ROOT, path)
    lines = open(full, encoding="utf-8", errors="replace").read().split("\n")
    start = None
    for i, l in enumerate(lines):
        if l.strip().startswith("#") and heading.lower() in l.lower():
            start = i
            break
    if start is None:
        out("NOT FOUND %s in %s" % (heading, path))
        return
    out("=== %s :: %s (line %d) ===" % (path, heading, start + 1))
    out("\n".join(lines[start:start + nlines]))


section("SPEC/SPEC-04-rules.md", "9.4 Armour, ammunition and jams", 90)
section("SPEC/SPEC-04-rules.md", "9.1 Rounds and orders", 70)
section("SPEC/SPEC-02-containers.md", "4.4 Character record", 60)

out("=== tests dir ===")
out(str(sorted(os.listdir(os.path.join(ROOT, "tests")))))

# find the consistency checker
for fn in sorted(os.listdir(os.path.join(ROOT, "tests"))):
    if not fn.endswith(".py"):
        continue
    p = os.path.join(ROOT, "tests", fn)
    txt = open(p, encoding="utf-8", errors="replace").read()
    if "def consistency" in txt:
        out("=== consistency in %s ===" % fn)
        lines = txt.split("\n")
        for i, l in enumerate(lines):
            if "def consistency" in l:
                out("\n".join("%d: %s" % (j + 1, lines[j]) for j in range(i, min(len(lines), i + 90))))
                break

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
