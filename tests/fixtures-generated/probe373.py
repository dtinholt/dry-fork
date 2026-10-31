"""Probe 373: dump Saltwell row y=20 (tiles + action_class + action_value).

Run: python3 tests/fixtures-generated/probe373.py
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
y = 20
print("tiles row 20:", m["tiles"][y][:20])
print("class row 20:", m["action_class"][y][:20])
print("value row 20:", m["action_value"][y][:20])
print()
print("records 11:", json.dumps(m["records"].get("11"), indent=1))
print()
print("tiles.json:")
t = json.loads((W.SCENARIO / "tiles.json").read_text())
print(json.dumps(t, indent=1)[:3000])
