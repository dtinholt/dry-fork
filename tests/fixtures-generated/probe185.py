"""Probe 185: bump map cells, reference CP4 items, combat-ref order rules."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump185.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


# 1. combat reference consistency rules
src = open(os.path.join(ROOT, "tests", "wl_combat_ref.py"), encoding="latin-1").read()
p("=" * 70)
p("wl_combat_ref.py")
p(src)

# 2. reference log: CP4 party items
for name in ("reflog.txt", "reflog2.txt", "reflog3.txt", "reflog4.txt", "refdump.txt", "ref.txt"):
    fp = os.path.join(ROOT, "tests", "fixtures-generated", name)
    if not os.path.isfile(fp):
        continue
    t = open(fp, encoding="latin-1").read()
    i = t.find("CP4")
    p("=" * 70)
    p("REF", name, "CP4 at", i)
    if i >= 0:
        p(t[max(0, i - 100):i + 2000])
    break

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
