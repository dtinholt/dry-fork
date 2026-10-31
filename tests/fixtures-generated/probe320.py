"""Probe 320: compile the scenario and dump the engine's runtime map.

Run: python3 tests/fixtures-generated/probe320.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wlengine.scenario as S  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")
OUT = os.path.join(HERE, "probe320data")
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
S.compile(SCEN, OUT)
print("compiled to", OUT)
print("files:", sorted(os.listdir(OUT)))

sc = S.load(OUT)
print("start:", sc.start)
print("location names:", sc.location_names)
m = sc.map(sc.start["location"])
print("map name:", m.get("name"), "size", m["size"])
img = m["cells"]["image"]
print("image[20]:", img[20])
print("image col20:", [img[y][20] for y in range(32)])
print("image[14]:", img[14])
print("ac[20]:", m["cells"]["actionClass"][20])
print("ac col20:", [m["cells"]["actionClass"][y][20] for y in range(32)])
print("info:", m["info"])
print("party:", json.dumps(sc.premade_party(), indent=1)[:1500])
