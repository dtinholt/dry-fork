"""Dump skills.json, the premade party as the engine builds it, and the loot
record at overworld (30,41).

Usage: python3 tests/fixtures-generated/probe63.py [skills|party|loot|all]
"""
import json
import os
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "tests")

from wlengine import maps, scenario  # noqa: E402

OUT = "tests/fixtures-generated/dd9"


def build():
    if not os.path.isdir(OUT):
        scenario.compile("SPEC/scenario", OUT)
    return scenario.load(OUT)


which = sys.argv[1] if len(sys.argv) > 1 else "all"
sc = build()
if which in ("all", "skills"):
    d = json.load(open("SPEC/scenario/skills.json"))
    print(json.dumps(d, indent=1)[:4000])
if which in ("all", "party"):
    for i, m in enumerate(sc.premade_party()):
        print(i + 1, json.dumps(m, default=str)[:600])
if which in ("all", "loot"):
    m = sc.map(0)
    rec = maps.record_at(m, 30, 41)
    print("record:", json.dumps(rec, indent=1))
    print("tail:", maps.apply_tail(rec))
    print("image:", maps.image_at(m, 30, 41))
    print("class/action:", m["cells"]["actionClass"][41][30], m["cells"]["action"][41][30])
