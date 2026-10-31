"""Gather the remaining facts needed for the combat implementation.

Run: python3 tests/fixtures-generated/probe69.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))


def show(path, a, b):
    print("=" * 70)
    print("### %s lines %d-%d" % (path, a, b))
    full = os.path.join(ROOT, path)
    with open(full, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if a <= i <= b:
                print("%4d %s" % (i, line.rstrip("\n")))


show("tests/wl_combat_ref.py", 140, 200)

print("=" * 70)
print("### items.json ids 4, 6, 8, 10, 11")
d = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "items.json")))
for it in d["items"]:
    if it["id"] in (4, 6, 8, 10, 11, 12):
        print(json.dumps(it))

print("=" * 70)
print("### shop record keys")
from wlengine import containers  # noqa: E402
raw = open(os.path.join(ROOT, "tests", "fixtures-generated", "dd9", "GAME1"), "rb").read()
tables = containers.read_tables(os.path.join(ROOT, "tests", "fixtures-generated", "dd9", "LABTABLES.BIN"))
base = tables["savegameOffsets"][0] + tables["savegameSize"]
rel = tables["shopListRelOffsets"]
sl = containers.decode_shop_list(raw, base + rel[0])
print("shop keys:", list(sl))
print("header:", sl.get("header"))
recs = sl["items"]
print("n recs:", len(recs))
for i in (0, 2, 3, 4, 5, 6, 8, 9, 10):
    print(i, json.dumps(recs[i]))

print("=" * 70)
print("### CR.opening round0 for seeds")
import wl_combat_ref as CR  # noqa: E402
for seed in (1, 2, 3, 20261021):
    o = CR.opening(seed)
    print("seed", seed, "surprised", o["surprised"])
    print("  check", json.dumps(o["check"]))
    print("  round0", json.dumps(o["round0"]))
    print("  round1", json.dumps(o["round1"]))

print("=" * 70)
print("### test_m6_playable.py grep")
full = os.path.join(ROOT, "tests", "test_m6_playable.py")
with open(full, "r", encoding="utf-8", errors="replace") as fh:
    for i, line in enumerate(fh, 1):
        if any(k in line for k in ("orders", "melee", "advance", "unarmed", "combat")):
            print("%4d %s" % (i, line.rstrip("\n")))
