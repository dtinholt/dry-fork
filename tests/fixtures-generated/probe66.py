"""Run the engine on the opening script and dump the events (M5 combat probe).

Run: python3 tests/fixtures-generated/probe66.py [seed] [mode]

mode: tail (default) prints from the encounter_start on; all prints everything.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

from wlengine import headless  # noqa: E402

DATA = os.path.join(ROOT, "tests", "fixtures-generated", "dd9")
WALK = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough.json")))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261021
mode = sys.argv[2] if len(sys.argv) > 2 else "tail"


def opening_script(walkthrough):
    out = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            return out + ["A"]
        out.append(item)
    raise AssertionError("no repeat_until")


script = opening_script(WALK)
ev = headless.run(DATA, {"seed": seed, "script": script}, seed)
start = 0
if mode == "tail":
    for i, e in enumerate(ev):
        if e.get("type") == "encounter_start":
            start = max(0, i - 4)
            break
for e in ev[start:]:
    print(json.dumps(e))
