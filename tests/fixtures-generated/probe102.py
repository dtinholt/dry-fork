"""Dump the current source of the headless/rules/combat functions relevant to M5.

Run:  python3 tests/fixtures-generated/probe102.py
"""
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import wlengine.headless as H  # noqa: E402
import wlengine.rules as R  # noqa: E402
import wlengine.combat as C  # noqa: E402


def show(mod, names):
    for n in names:
        obj = getattr(mod, n, None)
        if obj is None:
            print("### %s.%s MISSING" % (mod.__name__, n))
            continue
        try:
            src = inspect.getsource(obj)
        except Exception as e:  # pragma: no cover
            print("### %s.%s <no source: %s>" % (mod.__name__, n, e))
            continue
        print("### %s.%s" % (mod.__name__, n))
        print(src)
        print()


show(H, ["save_game", "write_save_files", "load_game", "move", "bump", "bump_effect",
         "hook_get", "bump_lock", "unlock", "pick_member", "skill_attribute", "end_of_round",
         "skill_level", "run", "key_a", "run_repeat", "start_encounter", "combat_key",
         "build_groups", "group_event", "monster_phase1", "party_phase1", "combat_round"])
show(R, ["check_need", "skill_check", "build_groups", "ranged_need", "melee_need",
         "monster_need", "flee_need", "jam_chance", "unarmed_attacks", "melee_damage_bonus",
         "damage_member", "speed_order", "xp_threshold", "level_after", "max_hp"])
show(C, ["__all__"])
print("### combat.py module source")
print(inspect.getsource(C))
