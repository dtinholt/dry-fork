"""Probe 398: compile the scenario with the engine and run the 'bump' script,
dumping events and the map's action_class around (2..5, 20).

Run: python3 tests/fixtures-generated/probe398.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SCEN = os.path.join(ROOT, "SPEC", "scenario")

import wlengine.scenario as S  # noqa: E402
import wlengine.headless as H  # noqa: E402

d = tempfile.mkdtemp(prefix="probe398-")
print("compiling to", d)
S.compile(SCEN, d)
print("compiled files:", sorted(os.listdir(d)))

ev = H.run(d, {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, None)
for e in ev:
    print(json.dumps(e, default=str))

print("=" * 70)
print("### engine map view")
sc = S.load(d) if hasattr(S, "load") else None
print("scenario load:", sc)
