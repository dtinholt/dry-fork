"""Probe 186: dump the rest of wl_combat_ref.py (orders/victory checks)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump186.txt")
src = open(os.path.join(ROOT, "tests", "wl_combat_ref.py"), encoding="latin-1").read()
lines = src.splitlines()
buf = []
for i, ln in enumerate(lines):
    buf.append("%5d %s" % (i + 1, ln))
open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(lines))
