"""Probe 26: dump the engine's combat-related source and run the raider fight.

Run from the project root:  python3 tests/fixtures-generated/probe26.py
"""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "src"))

import wlengine.headless as H  # noqa: E402
import wlengine.rules as R  # noqa: E402


def dump(mod, names):
    for n in names:
        f = getattr(mod, n, None)
        if f is None:
            print("### %s.%s: MISSING" % (mod.__name__, n))
            continue
        try:
            src = inspect.getsource(f)
        except Exception as e:  # noqa: BLE001
            print("### %s.%s: no source (%s)" % (mod.__name__, n, e))
            continue
        print("### %s.%s" % (mod.__name__, n))
        print(src)


def dump_all(mod, skip_prefixes=("__",)):
    for n in sorted(dir(mod)):
        if n.startswith(skip_prefixes):
            continue
        f = getattr(mod, n)
        if inspect.isfunction(f) and getattr(f, "__module__", "") == mod.__name__:
            try:
                print("### %s.%s" % (mod.__name__, n))
                print(inspect.getsource(f))
            except Exception as e:  # noqa: BLE001
                print("### %s.%s: no source (%s)" % (mod.__name__, n, e))


def main():
    print("== headless module names ==")
    print([n for n in dir(H) if not n.startswith("__")])
    print()
    print("== rules module names ==")
    print([n for n in dir(R) if not n.startswith("__")])
    print()
    dump(H, ["build_groups", "encounter_start", "surprise_check", "combat_round",
             "monster_phase1", "party_phase1", "start_combat", "combat"])
    dump(R, ["build_groups", "monster_hp", "ranged_need", "monster_need", "skill_check",
             "check_need", "jam_chance", "damage_member", "speed_order"])
    print()
    print("== full rules.py dump ==")
    dump_all(R)
    print()
    print("== headless combat-ish functions ==")
    for n in sorted(dir(H)):
        if n.startswith("__"):
            continue
        f = getattr(H, n)
        if inspect.isfunction(f) and getattr(f, "__module__", "") == H.__name__:
            if any(k in n for k in ("combat", "encounter", "group", "surprise", "phase",
                                    "round", "attack", "monster", "jam", "reload", "xp",
                                    "promote", "victory", "flee")):
                try:
                    print("### %s.%s" % (H.__name__, n))
                    print(inspect.getsource(f))
                except Exception as e:  # noqa: BLE001
                    print("### %s.%s: no source (%s)" % (H.__name__, n, e))


if __name__ == "__main__":
    main()
