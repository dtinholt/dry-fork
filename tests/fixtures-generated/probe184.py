"""Probe 184: dump combat.py, the headless save code, and map cells near (2,20)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src", "wlengine")
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump184.txt")
buf = []


def whole(path):
    buf.append("=" * 70)
    buf.append("FILE " + path)
    for i, ln in enumerate(open(path, encoding="latin-1").read().splitlines()):
        buf.append("%5d %s" % (i + 1, ln))


whole(os.path.join(SRC, "combat.py"))

# headless: save / write_save_files / cell_change / load
lines = open(os.path.join(SRC, "headless.py"), encoding="latin-1").read().splitlines()
for i, ln in enumerate(lines):
    if ("def write_save" in ln or "def save" in ln or "def cell_change" in ln
            or "def load" in ln or "labstate" in ln or "def do_save" in ln):
        buf.append("=" * 70)
        buf.append("headless.py line %d" % (i + 1))
        for j in range(max(0, i - 3), min(len(lines), i + 45)):
            buf.append("%5d %s" % (j + 1, lines[j]))

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
