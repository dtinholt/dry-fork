"""Probe 372: dump Saltwell (map1) cells around y=20, x=0..16.

Run: python3 tests/fixtures-generated/probe372.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wl_support as W  # noqa: E402

m = json.loads((W.SCENARIO / "map1-saltwell.json").read_text())
print("top keys:", list(m.keys()))
print(json.dumps({k: v for k, v in m.items() if k != "tiles"}, indent=1)[:4000])
