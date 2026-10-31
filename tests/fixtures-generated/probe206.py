"""Probe 206: conftest runner fixture, SPEC-05 5.2 art, action_cells, start."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump206.txt")
buf = []


def out(s=""):
    buf.append(str(s))


def cat(path, limit=400):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        out("MISSING " + path)
        return
    ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
    out("=== %s (%d lines) ===" % (path, len(ls)))
    out("\n".join("%d: %s" % (i + 1, ls[i]) for i in range(min(limit, len(ls)))))


cat("tests/conftest.py", 300)

out("=== SPEC/reference ===")
ref = os.path.join(ROOT, "SPEC", "reference")
if os.path.isdir(ref):
    out(str(sorted(os.listdir(ref))))
    for f in sorted(os.listdir(ref)):
        p = os.path.join(ref, f)
        if os.path.isfile(p):
            out("%s: %d bytes" % (f, os.path.getsize(p)))

# SPEC-05 5.2
full = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
for i, l in enumerate(ls):
    if l.strip().startswith("### 5.2"):
        out("=== SPEC-05 5.2 ===")
        out("\n".join("%d: %s" % (j + 1, ls[j]) for j in range(i, min(len(ls), i + 70))))
        break

m1 = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
out("=== map1 action_cells ===")
out(json.dumps(m1["action_cells"])[:3000])
out("=== map1 conventions ===")
out(json.dumps(m1.get("conventions"))[:1000])
sc = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "scenario.json")))
out("=== scenario.json ===")
out(json.dumps(sc, indent=1)[:3000])

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
