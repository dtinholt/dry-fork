"""Probe 121: compile the scenario and run the CP6 script, printing the traceback."""
import json
import os
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    from wlengine import scenario, headless
    d = tempfile.mkdtemp(prefix="probe121-")
    scenario.compile(SCEN, d)
    print("compiled to", d)
    wt = json.load(open(os.path.join(SCEN, "walkthrough.json")))
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP6":
            break
    print("script len", len(script))
    try:
        ev = headless.run(d, json.dumps({"seed": 20261021, "script": script}))
    except Exception:
        traceback.print_exc()
        return
    print("events", len(ev))


if __name__ == "__main__":
    main()
