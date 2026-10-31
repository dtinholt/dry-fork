"""Probe 404: run the bump and look scenarios and print events only."""
import sys
import pathlib
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from wlengine import headless

DATA = None
for p in sorted(ROOT.rglob("LABTABLES.BIN")):
    DATA = p.parent
    break
print("DATA:", DATA)
SEED = 1

for name, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                     ("look", ["L", "LEFT", {"checkpoint": "a"}])):
    try:
        ev, st = headless.run(str(DATA), {"seed": SEED, "script": script})
        print("==== %s ====" % name)
        for e in ev:
            print("   ", json.dumps(e, sort_keys=True))
        print("state:", json.dumps(st, sort_keys=True))
    except Exception as exc:
        print("==== %s failed: %s %s" % (name, type(exc).__name__, exc))
