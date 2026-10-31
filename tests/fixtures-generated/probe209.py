"""Probe 209: the three failing M5 tests and the M6 checkpoint test."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump209.txt")
buf = []


def out(s=""):
    buf.append(str(s))


def show(path, pats, before=0, after=40, limit=400):
    full = os.path.join(ROOT, path)
    ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
    hits = [i for i, l in enumerate(ls) if any(p in l for p in pats)]
    shown, rows = set(), []
    for i in hits:
        for j in range(max(0, i - before), min(len(ls), i + after + 1)):
            if j in shown:
                continue
            shown.add(j)
            rows.append("%s:%d: %s" % (path, j + 1, ls[j]))
        rows.append("---")
    out("\n".join(rows[:limit]))


show("tests/test_m5_rules.py", ["def test_bump_is_not_a_step"], after=45)
show("tests/test_m5_rules.py", ["def test_load_restores_state"], after=30)
show("tests/test_m6_playable.py", ["def test_checkpoint_matches_reference"], after=60)
show("tests/test_m6_playable.py", ["def test_", "CP4", "CP5"], after=3, limit=200)

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
