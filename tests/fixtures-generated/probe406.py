"""Probe 406: compile the scenario fresh and run the bump/look scripts."""
import sys
import pathlib
import json
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from wlengine import headless, scenario

SCEN = ROOT / "SPEC" / "scenario"
if not SCEN.is_dir():
    for cand in ROOT.rglob("scenario"):
        if cand.is_dir() and (cand / "walkthrough.json").is_file():
            SCEN = cand
            break
print("SCEN:", SCEN)

d = pathlib.Path(tempfile.mkdtemp("probe406"))
scenario.compile(str(SCEN), str(d))
print("compiled to", d)
SEED = 20261021

for name, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                     ("look", ["L", "LEFT", {"checkpoint": "a"}])):
    try:
        ev = headless.run(str(d), script, SEED)
        print("==== %s ====" % name)
        for e in ev:
            if e.get("type") == "checkpoint":
                st = e["state"]
                print("   checkpoint", {k: st[k] for k in ("location", "x", "y", "steps", "hour", "minute", "mode")})
            else:
                print("   ", json.dumps(e, sort_keys=True))
    except Exception as exc:
        print("==== %s failed: %s %s" % (name, type(exc).__name__, exc))
