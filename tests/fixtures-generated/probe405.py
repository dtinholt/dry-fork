"""Probe 405: run the bump and look scenarios correctly (run(data_dir, script, seed))."""
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
SEED = 20261021

for name, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                     ("look", ["L", "LEFT", {"checkpoint": "a"}])):
    try:
        ev = headless.run(str(DATA), script, SEED)
        print("==== %s ====" % name)
        for e in ev:
            print("   ", json.dumps(e, sort_keys=True))
    except Exception as exc:
        print("==== %s failed: %s %s" % (name, type(exc).__name__, exc))
