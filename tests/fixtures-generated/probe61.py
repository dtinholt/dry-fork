"""Compile the scenario and dump the item table, skill table, map mobs and the
encounter record at overworld (30,41).

Usage: python3 tests/fixtures-generated/probe61.py [items|skills|mobs|enc|all]
"""
import json
import os
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "tests")

from wlengine import scenario  # noqa: E402

OUT = "tests/fixtures-generated/dd9"


def build():
    if not os.path.isdir(OUT):
        scenario.compile("SPEC/scenario", OUT)
    return scenario.load(OUT)


def show_items(sc):
    tbl = getattr(sc, "items", None)
    print("items attr:", type(tbl))
    if tbl is None:
        fn = getattr(sc, "item_table", None)
        tbl = fn() if fn else None
    if isinstance(tbl, dict):
        for k in sorted(tbl):
            print(k, tbl[k])
    elif isinstance(tbl, list):
        for i, v in enumerate(tbl):
            print(i + 1, v)


def show_skills(sc):
    print("skill_table:", getattr(sc, "skill_table", None))


def show_mobs(sc):
    for loc in range(4):
        m = sc.map(loc)
        print("=== location %d mobs ===" % loc)
        for i, mob in enumerate(m.get("mobs", [])):
            print(i + 1, mob)


def show_enc(sc):
    m = sc.map(0)
    print("keys:", sorted(m.keys()))
    print("info:", m.get("info"))
    for y in range(38, 44):
        row = []
        for x in range(28, 34):
            row.append((m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x]))
        print(y, row)
    rec = None
    try:
        from wlengine import maps
        rec = maps.record_at(m, 30, 41)
    except Exception as e:  # noqa: BLE001
        print("record_at failed:", e)
    print("record at (30,41):", json.dumps(rec, indent=1) if rec else rec)


which = sys.argv[1] if len(sys.argv) > 1 else "all"
sc = build()
if which in ("all", "items"):
    show_items(sc)
if which in ("all", "skills"):
    show_skills(sc)
if which in ("all", "mobs"):
    show_mobs(sc)
if which in ("all", "enc"):
    show_enc(sc)
