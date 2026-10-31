"""Probe 210: inspect the engine's combat/order code and the failing tests.

Writes dump210.txt with:
  * the rest of src/wlengine/combat.py (orders, rounds, victory)
  * the movement/bump code in src/wlengine/headless.py
  * the class-1 tail handling in headless.py / maps.py
  * the reference log lines around the CP4/CP5 checkpoints
  * the M5 tests for bump / labstate / orders
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump210.txt")
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


def whole(path, a, b):
    full = os.path.join(ROOT, path)
    ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
    for j in range(a - 1, min(len(ls), b)):
        out("%s:%d: %s" % (path, j + 1, ls[j]))
    out("---")


out("=== combat.py 200-520 ===")
whole("src/wlengine/combat.py", 200, 520)
out("=== headless.py: bump/move/step ===")
show("src/wlengine/headless.py", ["def move", "def bump", "bump", "steps", "cell_change"],
     after=25, limit=400)
out("=== headless.py: class 1 / print / tail ===")
show("src/wlengine/headless.py", ["class 1", "new_class", "new_action", "PRINT", "paragraph"],
     after=20, limit=300)
out("=== maps.py: tail ===")
show("src/wlengine/maps.py", ["new_class", "new_action", "tail"], after=20, limit=200)
out("=== reference log CP4/CP5 ===")
show("tests/fixtures-generated/reflog.txt", ["CP4", "CP5"], before=5, after=5, limit=100)
out("=== test_m5_rules: save_labstate / orders ===")
show("tests/test_m5_rules.py", ["def test_save_labstate", "def test_raider_fight_rules"],
     after=45, limit=200)
out("=== wl_combat_ref consistency ===")
show("tests/wl_combat_ref.py", ["def consistency", "PARTY_CP3"], after=45, limit=200)
out("=== labstate.py ===")
whole("src/wlengine/labstate.py", 1, 60)

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
