"""Probe 371: dump Saltwell (location 1) cells around y=20, x=0..16.

Run: python3 tests/fixtures-generated/probe371.py
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
from wlengine import headless, maps, scenario  # noqa: E402

d = tempfile.mkdtemp(prefix="probe371-")
scenario.compile(str(W.SCENARIO), d)

loc = json.loads((W.SCENARIO / "locations.json").read_text())
print("locations keys:", list(loc.keys())[:10])
print(json.dumps(loc, indent=1)[:3000])
