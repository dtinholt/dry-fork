"""Probe 16: run the opening script and dump the combat events.

Run:  python3 tests/fixtures-generated/probe16.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))


def main():
    import wl_support as W
    walkthrough = W.load_json(W.SCENARIO / "walkthrough.json")
    script = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            script = script + ["A"]
            break
        script.append(item)
    print("opening script:", json.dumps(script)[:2000])
    import wlengine.headless as H
    for seed in (1,):
        ev = H.run(seed=seed, script=script)
        print("=" * 70)
        print("seed", seed, "n events", len(ev))
        for e in ev:
            t = e.get("type")
            if t in ("encounter_start", "check", "surprised", "round_start", "round_orders",
                     "attack", "jam", "click", "monster_dies", "unconscious", "death",
                     "group_closes", "combat_end", "message", "paragraph", "input", "bump",
                     "cell_change", "money", "xp", "checkpoint"):
                print(json.dumps(e)[:300])


if __name__ == "__main__":
    main()
