"""Probe 14: run the engine's opening script and print only combat events.

Usage: python3 tests/fixtures-generated/probe14.py [seed]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "tests"))

import wl_support as W  # noqa: E402

KEYS = ("encounter_start", "check", "surprised", "round_start", "round_orders",
        "attack", "jam", "click", "reload", "unjammed", "monster_dies",
        "unconscious", "death", "group_closes", "advance", "combat_end", "xp",
        "promote", "loot", "message", "paragraph", "map_change")


def opening_script(walkthrough):
    out = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            return out + ["A"]
        out.append(item)
    raise AssertionError("no repeat_until")


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261021
    data_dir = PROJECT / "tests/fixtures-generated/dd3"
    walkthrough = W.load_json(W.SCENARIO / "walkthrough.json")
    script = opening_script(walkthrough)
    from wlengine import headless
    ev = headless.run(str(data_dir), {"seed": seed, "script": script}, seed)
    print("== engine events (combat-relevant) ==")
    for e in ev:
        if e.get("type") in KEYS:
            print(json.dumps(e, default=str)[:300])
    print("== reference opening ==")
    import wl_combat_ref as CR
    ref = CR.opening(seed)
    print(json.dumps(ref, indent=1, default=str))


if __name__ == "__main__":
    main()
