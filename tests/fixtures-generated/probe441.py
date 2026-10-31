"""probe441: compile the scenario, run the bump/look scripts, print events and
the engine's start position."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402

tmp = Path(tempfile.mkdtemp())
sc.compile(str(ROOT / "SPEC/scenario"), str(tmp))
print("compiled ->", tmp)
print(sorted(p.name for p in tmp.iterdir()))

for key, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                    ("look", ["L", "LEFT", {"checkpoint": "a"}]),
                    ("pump", ["UP"] * 9 + [{"checkpoint": "a"}])):
    ev = hl.run(str(tmp), {"seed": 19880101, "script": script})
    print("=== %s ===" % key)
    for e in ev:
        print("   ", json.dumps(e))
