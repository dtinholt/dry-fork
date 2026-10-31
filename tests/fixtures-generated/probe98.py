"""Probe 98: reference-log event shapes + a live bump run.

Part A: distinct event types in SPEC/scenario/walkthrough-reference-log.json
        with the union of their keys, and the first example of each.
Part B: compile SPEC/scenario with wlengine.scenario.compile into a temp dir,
        then run headless.run on the bump script (13 LEFT) and print the last
        events plus the checkpoint state, to diagnose test_bump_is_not_a_step.
Part C: run the opening script (walkthrough prefix up to the repeat_until
        macro + "A") and print the combat events, to compare with the
        reference log.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"
sys.path.insert(0, str(ROOT / "src"))


def part_a():
    ref = json.loads((SCEN / "walkthrough-reference-log.json").read_text())
    ev = ref["events"] if isinstance(ref, dict) else ref
    order = []
    keys = {}
    first = {}
    for e in ev:
        t = e.get("type")
        if t not in keys:
            order.append(t)
            keys[t] = set()
            first[t] = e
        keys[t].update(e.keys())
    print("==== reference log: %d events, %d types ====" % (len(ev), len(order)))
    for t in order:
        print("%-16s n=%-4d keys=%s" % (t, sum(1 for e in ev if e.get("type") == t),
                                        sorted(keys[t])))
    print()
    print("==== first example of each type ====")
    for t in order:
        print("%-16s %s" % (t, json.dumps(first[t])))
    print()


def compile_data():
    from wlengine import scenario
    d = Path(tempfile.mkdtemp(prefix="probe98-"))
    scenario.compile(str(SCEN), str(d))
    return d


def part_b(d):
    from wlengine import headless
    script = {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}
    ev = headless.run(str(d), script, None)
    print("==== bump run: last 8 events ====")
    for e in ev[-8:]:
        print(json.dumps(e))
    for e in ev:
        if e.get("type") == "checkpoint":
            print("checkpoint:", json.dumps(e["state"])[:400])
    print()


def part_c(d):
    from wlengine import headless
    wt = json.loads((SCEN / "walkthrough.json").read_text())
    out = []
    for item in wt["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            out.append("A")
            break
        out.append(item)
    for seed in (20261021, 1):
        ev = headless.run(str(d), {"seed": seed, "script": out}, seed)
        print("==== opening run seed %d: events from encounter_start ====" % seed)
        i = next((k for k, e in enumerate(ev) if e.get("type") == "encounter_start"), None)
        for e in ev[i or 0:]:
            print(json.dumps(e))
        print()


def main():
    part_a()
    d = compile_data()
    print("compiled to", d)
    part_b(d)
    part_c(d)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
