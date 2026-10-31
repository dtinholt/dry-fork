"""Probe 17: compile the scenario, run the opening script, dump combat events.

Run:  python3 tests/fixtures-generated/probe17.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402


def compile_data():
    d = tempfile.mkdtemp(prefix="probe17-")
    import wlengine.scenario as S
    S.compile(str(W.SCENARIO), d)
    return d


def opening_script(walkthrough):
    out = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            return out + ["A"]
        out.append(item)
    raise AssertionError("no repeat_until")


def main():
    walkthrough = W.load_json(W.SCENARIO / "walkthrough.json")
    script = opening_script(walkthrough)
    d = compile_data()
    print("compiled to", d)
    import wlengine.headless as H
    for seed in (1,):
        ev = H.run(d, {"script": script}, seed)
        print("=" * 70)
        print("seed", seed, "n events", len(ev))
        for e in ev:
            t = e.get("type")
            if t in ("encounter_start", "check", "surprised", "round_start", "round_orders",
                     "attack", "jam", "click", "monster_dies", "unconscious", "death",
                     "group_closes", "combat_end", "message", "paragraph", "input", "bump",
                     "cell_change", "money", "xp", "checkpoint", "new_game"):
                print(json.dumps(e)[:400])
    import wl_combat_ref as CR
    ref = CR.opening(1)
    print("=" * 70)
    print("REFERENCE")
    print(json.dumps(ref, indent=1)[:4000])


if __name__ == "__main__":
    main()
