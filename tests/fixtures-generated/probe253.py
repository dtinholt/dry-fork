"""Probe 253: print the oracle 'expected' view of map1 cells row 20 and the
engine's compiled map1 row 20, plus the SPEC art row 20.

Run: python3 tests/fixtures-generated/probe253.py
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

d = Path(tempfile.mkdtemp())
sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(d),
                    str(ROOT / "SPEC" / "scenario")], capture_output=True, text=True)
data = json.loads(r.stdout)
exp = data["expected"]["maps"]["1"]
print("expected map1 keys:", list(exp.keys()))
cells = exp["cells"]
print("expected actionClass row 20:", cells["actionClass"][20])
print("expected action row 20:", cells["action"][20])
print("expected image row 20:", cells["image"][20])

m = json.load(open(ROOT / "SPEC" / "scenario" / "map1-saltwell.json"))
print("json tiles row 20:", m["tiles"][20])
print("json action_class row 20:", m["action_class"][20])

# engine loader
import wlengine.maps as maps  # noqa: E402
mm = maps.load_map(str(d), 1)
print("engine load_map keys:", list(mm.keys()))
for k in ("cells", "action_class", "tiles", "action"):
    if k in mm:
        v = mm[k]
        print("engine", k, "row 20:", v[20] if isinstance(v, list) and len(v) > 20 else v)
