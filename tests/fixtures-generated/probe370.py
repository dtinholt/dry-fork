"""Probe 370: reproduce the M5 'bump' run and dump events.

Run: python3 tests/fixtures-generated/probe370.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wl_support as W  # noqa: E402
from wlengine import headless, scenario  # noqa: E402

d = tempfile.mkdtemp(prefix="probe370-")
scenario.compile(str(W.SCENARIO), d)
print("compiled to", d)
print("files:", sorted(os.listdir(d)))

SEED = 12345
script = ["LEFT"] * 13 + [{"checkpoint": "a"}]
ev = headless.run(d, {"seed": SEED, "script": script})
if isinstance(ev, tuple):
    ev = ev[0]
print("n events:", len(ev))
for i, e in enumerate(ev):
    print(i, json.dumps(e, sort_keys=True))
