"""Probe: dump reference expectations vs engine output for M5 combat tests.

Run:  python3 tests/fixtures-generated/probe3.py
"""
from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wl_support as W  # noqa: E402
import wl_combat_ref as CR  # noqa: E402


def show(title, obj):
    print("=" * 70)
    print(title)
    print("-" * 70)
    print(json.dumps(obj, indent=1, default=str))


def mob(js):
    return {"name": js["name"], "sturdiness": js["sturdiness"], "combatRating": js["combat_rating"],
            "randomDamage": js["random_damage"], "maxGroup": js["max_group"], "armorClass": js["armor_class"],
            "fixedDamage": js["fixed_damage"], "weaponType": js["weapon_type"], "type": js["type"],
            "portrait": js["portrait"]}


def main():
    MOBS = W.load_json(W.SCENARIO / "encounters.json")["monsters"]
    print("monsters:")
    for i, m in enumerate(MOBS):
        print("  %d %s" % (i, m["name"]))

    for f in ("map0-overworld.json", "map3-pumphouse.json"):
        mj = W.load_json(W.SCENARIO / f)
        mobs = [mob(x) for x in mj["mobs"]]
        for i, r in enumerate(mj["records"].get("3", [])):
            for seed in (20261021, 3):
                ref = W.RefRng(seed)
                want = W.ref_build_groups(ref, copy.deepcopy(mobs), {"groups": r["groups"]})
                show("%s enc%d seed %d groups=%r" % (f, i + 1, seed, r["groups"]), want)
                try:
                    rng = W.call("rules.Rng", seed)
                    got = W.call("rules.build_groups", rng, copy.deepcopy(mobs), {"groups": r["groups"]})
                    show("  engine got", got)
                except Exception as e:  # noqa: BLE001
                    print("  engine raised %s: %s" % (type(e).__name__, e))

    # surprise check reference
    print("=" * 70)
    print("ref_check_need(2, 15, 30, False) =", W.ref_check_need(2, 15, 30, False))
    print("ref_check_need(2, 11, 6, False) =", W.ref_check_need(2, 11, 6, False))
    print("ref_check_need(1, 12, 35, True) =", W.ref_check_need(1, 12, 35, True))
    print("ref_check_need(0, 13, 0, False) =", W.ref_check_need(0, 13, 0, False))

    # combat ref module surface
    print("=" * 70)
    print("wl_combat_ref names:", [n for n in dir(CR) if not n.startswith("_")])


if __name__ == "__main__":
    main()
