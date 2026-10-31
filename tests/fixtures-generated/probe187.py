"""Probe 187: dump test_m6_playable.py, conftest, and locate the reference log."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump187.txt")
buf = []


def whole(path, label=None):
    buf.append("=" * 70)
    buf.append("FILE " + (label or path))
    for i, ln in enumerate(open(path, encoding="latin-1").read().splitlines()):
        buf.append("%5d %s" % (i + 1, ln))


whole(os.path.join(ROOT, "tests", "test_m6_playable.py"))
whole(os.path.join(ROOT, "tests", "conftest.py"))

# find reference log files
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    for fn in filenames:
        if "ref" in fn.lower() or "log" in fn.lower():
            buf.append("FOUND %s" % os.path.join(dirpath, fn))

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
