"""Probe 119: introspect combat/headless API needed by the victory-loot fix.

Prints:
  * module-level constants of wlengine.combat (SALVAGE, RANGED_SKILLS, ...)
  * whether combat.py imports maps
  * the source of CombatMixin.victory / best_salvage
  * which attributes the headless engine exposes (x, y, apply_tail, ...)
  * the keys of a live combat dict (does it carry "record"?)
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from wlengine import combat  # noqa: E402


def show_consts():
    print("== combat module constants ==")
    for name in dir(combat):
        if name.isupper():
            val = getattr(combat, name)
            if isinstance(val, (int, str, tuple, list, dict, set)):
                print("  %s = %r" % (name, val))
    print("== combat module imports ==")
    for name in ("maps", "rules", "containers", "strings"):
        print("  %s: %s" % (name, hasattr(combat, name)))


def show_source():
    print("== victory source ==")
    try:
        print(inspect.getsource(combat.CombatMixin.victory))
    except Exception as exc:  # noqa: BLE001
        print("  err", exc)
    print("== best_salvage source ==")
    try:
        print(inspect.getsource(combat.CombatMixin.best_salvage))
    except Exception as exc:  # noqa: BLE001
        print("  err", exc)


def show_headless():
    from wlengine import headless
    print("== headless Engine attrs ==")
    cls = headless.Engine
    for name in ("x", "y", "apply_tail", "apply_loot", "cell_class_action",
                 "cell_change", "show_message", "attr_value", "skill_attribute",
                 "ATTR_ORDER", "ATTR_OFFSETS", "skill_level"):
        print("  %s: %s" % (name, hasattr(cls, name)))
    print("== headless module constants ==")
    for name in dir(headless):
        if name.isupper():
            val = getattr(headless, name)
            if isinstance(val, (int, str, tuple, list, dict, set)):
                print("  %s = %r" % (name, val))


def show_combat_keys():
    print("== combat dict keys (from start_encounter) ==")
    try:
        print(inspect.getsource(combat.CombatMixin.start_encounter))
    except Exception as exc:  # noqa: BLE001
        print("  err", exc)


if __name__ == "__main__":
    show_consts()
    show_source()
    show_headless()
    show_combat_keys()
