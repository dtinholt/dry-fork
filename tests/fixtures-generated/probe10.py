"""Probe 10: run the bump script and the opening script; dump events."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wl_support as W  # noqa: E402

SEED = 20261021


def main():
    import wlengine.scenario as scen
    out = os.path.join(HERE, "dd4")
    scen.compile(os.path.join(ROOT, "SPEC", "scenario"), out)
    ev = W.call("headless.run", out, json.dumps({"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}), SEED)
    for e in ev:
        if e.get("type") in ("bump", "move", "checkpoint", "blocked"):
            print(json.dumps(e)[:200])

    print("=" * 70)
    wt = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough.json")))
    script = []
    for item in wt["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            script.append("A")
            break
        script.append(item)
    ev = W.call("headless.run", out, json.dumps({"seed": SEED, "script": script}), SEED)
    for e in ev:
        if e.get("type") in ("encounter_start", "check", "surprised", "round_start", "round_orders",
                             "attack", "jam", "click", "monster_dies", "unconscious", "death",
                             "group_closes", "combat_end", "input"):
            print(json.dumps(e)[:300])


if __name__ == "__main__":
    main()
