"""Dump scenario JSON bits needed for the combat implementation.

Run: python3 tests/fixtures-generated/probe67.py [what]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")


def load(name):
    return json.load(open(os.path.join(SC, name)))


WHAT = sys.argv[1] if len(sys.argv) > 1 else "all"

if WHAT in ("all", "skills"):
    d = load("skills.json")
    print("=== skills.json ===")
    print(json.dumps(d, indent=1)[:4000])

if WHAT in ("all", "items"):
    d = load("items.json")
    print("=== items.json (first 12) ===")
    items = d["items"] if isinstance(d, dict) else d
    for it in items[:12]:
        print(json.dumps(it))

if WHAT in ("all", "map0"):
    d = load("map0-overworld.json")
    print("=== map0 keys ===", list(d))
    print("conventions:", json.dumps(d.get("conventions")))
    print("action_cells:", json.dumps(d.get("action_cells")))
    print("encounters:", json.dumps(d.get("encounters"))[:2000])
    print("loot:", json.dumps(d.get("loot"))[:2000])
    print("mobs:", json.dumps(d.get("mobs"))[:2000])

if WHAT in ("all", "party"):
    d = load("party.json")
    print("=== party.json ===")
    print(json.dumps(d, indent=1)[:4000])

if WHAT in ("all", "scenario"):
    d = load("scenario.json")
    print("=== scenario.json ===")
    print(json.dumps(d, indent=1)[:3000])
