"""Probe 283: compile SPEC/scenario, run the bump script, dump the map around
(0..6, 20) from the compiled data and from the SPEC JSON."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SPEC = os.path.join(ROOT, "SPEC", "scenario")

from wlengine import scenario as scen  # noqa: E402
from wlengine import headless as H  # noqa: E402
from wlengine import maps as M  # noqa: E402

d = tempfile.mkdtemp(prefix="probe283-")
scen.compile(SPEC, d)
print("compiled to", d)
print(sorted(os.listdir(d)))

ev = H.run(d, {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
print("--- events ---")
for e in ev:
    print(e)

# Now the map.
sc = scen.load(d)
print("scenario attrs:", [a for a in dir(sc) if not a.startswith("_")])
