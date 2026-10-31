"""Probe 252: run the engine headless with 13 LEFTs on map1 and dump events;
also print the oracle's compiled map1 row 20 actionClass/tiles.

Run: python3 tests/fixtures-generated/probe252.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402

d = Path(tempfile.mkdtemp())
sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(d),
                    str(ROOT / "SPEC" / "scenario")], capture_output=True, text=True)
data = json.loads(r.stdout)
m1 = data["oracle"]["map1"]
cells = m1["cells"]
print("oracle actionClass row 20:", cells["actionClass"][20])
print("oracle tiles row 20:", cells.get("tiles", [None])[20] if "tiles" in cells else "no tiles key")
print("cells keys:", list(cells.keys()))
print("oracle actionValue row 20:", cells["actionValue"][20] if "actionValue" in cells else "?")

ev = hl.run(str(d), {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, 20261021)
for e in ev:
    print(e)
