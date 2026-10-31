"""Run the engine on the opening script and dump the combat events.

Usage: python3 tests/fixtures-generated/probe37.py [seed]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

SCEN = W.SCENARIO


def opening_script(walkthrough):
    out = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            return out + ["A"]
        out.append(item)
    raise AssertionError("no repeat_until")


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261021
    wt = W.load_json(SCEN / "walkthrough.json")
    script = {"seed": seed, "script": opening_script(wt)}
    print("SCRIPT:", json.dumps(script)[:2000])
    # compile into a temp dir
    import tempfile
    d = Path(tempfile.mkdtemp())
    from wlengine import scenario as sc
    sc.compile(str(SCEN), str(d))
    ev = W.call("headless.run", str(d), json.loads(json.dumps(script)), seed)
    for i, e in enumerate(ev):
        print(i, json.dumps(e)[:400])


def combat_only():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261021
    wt = W.load_json(SCEN / "walkthrough.json")
    script = {"seed": seed, "script": opening_script(wt)}
    import tempfile
    d = Path(tempfile.mkdtemp())
    from wlengine import scenario as sc
    sc.compile(str(SCEN), str(d))
    ev = W.call("headless.run", str(d), json.loads(json.dumps(script)), seed)
    keep = ("encounter_start", "check", "surprised", "round_start", "round_orders",
            "attack", "jam", "click", "monster_dies", "unconscious", "death",
            "combat_end", "group_closes", "message", "cell_change", "money")
    for i, e in enumerate(ev):
        if e.get("type") in keep:
            print(i, json.dumps(e)[:400])


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "combat":
        combat_only()
    else:
        main()
