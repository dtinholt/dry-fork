"""Probe 183: dump source sections needed for the M5 fixes into dump183.txt."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src", "wlengine")
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump183.txt")

buf = []


def show(path, pattern, before=6, after=30, limit=6):
    buf.append("=" * 70)
    buf.append("FILE %s PATTERN %s" % (path, pattern))
    lines = open(path, encoding="latin-1").read().splitlines()
    hits = 0
    for i, ln in enumerate(lines):
        if re.search(pattern, ln):
            hits += 1
            if hits > limit:
                break
            lo = max(0, i - before)
            hi = min(len(lines), i + after)
            buf.append("--- line %d ---" % (i + 1))
            for j in range(lo, hi):
                buf.append("%5d %s" % (j + 1, lines[j]))
    if hits == 0:
        buf.append("(no match)")


show(os.path.join(SRC, "headless.py"), r"def .*bump|bump\"|'bump'")
show(os.path.join(SRC, "headless.py"), r"steps \+=|self\.steps")
show(os.path.join(SRC, "headless.py"), r"reload")
show(os.path.join(SRC, "headless.py"), r"def auto_orders|def .*orders")
show(os.path.join(SRC, "rules.py"), r"rank|skill_points|promot")
show(os.path.join(SRC, "labstate.py"), r".*", before=0, after=60, limit=1)

for name in ("reflog.txt", "refdump.txt", "reflog4.txt"):
    p = os.path.join(ROOT, "tests", "fixtures-generated", name)
    if os.path.isfile(p):
        txt = open(p, encoding="latin-1").read()
        idx = txt.find("cell_changes")
        buf.append("=" * 70)
        buf.append("REF %s cell_changes at %d" % (name, idx))
        if idx >= 0:
            buf.append(txt[idx:idx + 1500])
        break

tp = os.path.join(ROOT, "tests", "test_m5_rules.py")
txt = open(tp, encoding="latin-1").read()
for name in ("test_bump_is_not_a_step", "test_raider_fight_rules", "test_save_labstate"):
    i = txt.find("def " + name)
    if i >= 0:
        buf.append("=" * 70)
        buf.append("TEST " + name)
        buf.append(txt[i:i + 2500])

for name in ("ref.txt", "refdump.txt"):
    p = os.path.join(ROOT, "tests", "fixtures-generated", name)
    if os.path.isfile(p):
        t = open(p, encoding="latin-1").read()
        for key in ("CP4", "CP5-pre-save"):
            i = t.find(key)
            buf.append("=" * 70)
            buf.append("REF %s %s at %d" % (name, key, i))
            if i >= 0:
                buf.append(t[max(0, i - 200):i + 1500])
        break

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf), "lines")
