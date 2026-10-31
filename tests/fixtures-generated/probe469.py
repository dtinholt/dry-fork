"""probe469: run the engine headless on the bump/look scripts and dump events.

Also dump the engine's compiled map cells around (2..5, 20) and (13..16, 20)
so we can see where the cactus and the street column land in the engine's view.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wlengine.headless as H  # noqa: E402
import wlengine.scenario as S  # noqa: E402

SEED = 20261021

# compile the scenario into a temp dir
import tempfile
out = tempfile.mkdtemp(prefix="probe469-")
S.compile(os.path.join(ROOT, "SPEC", "scenario"), out)
print("compiled to", out)

ev = H.run(out, {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
print("=== bump run events (last 8) ===")
for e in ev[-8:]:
    print(json.dumps(e))

ev2 = H.run(out, {"seed": SEED, "script": ["L", "LEFT", {"checkpoint": "a"}]})
print("=== look run events ===")
for e in ev2:
    print(json.dumps(e))

# engine's map view
sc = S.load(out)
m = sc.map(1) if hasattr(sc, "map") else None
print("=== scenario attrs:", [a for a in dir(sc) if not a.startswith("_")][:40])
