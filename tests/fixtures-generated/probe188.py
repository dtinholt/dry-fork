"""Probe 188: dump wl_support helpers (run, ref_labstate, REFERENCE_LOG)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump188.txt")
buf = []
for name in ("wl_support.py",):
    path = os.path.join(ROOT, "tests", name)
    buf.append("=" * 70)
    buf.append("FILE " + name)
    for i, ln in enumerate(open(path, encoding="latin-1").read().splitlines()):
        buf.append("%5d %s" % (i + 1, ln))
open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
