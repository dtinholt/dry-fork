"""Probe 27: saltwell row 20, action_cells, and the engine's compiled map."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SCEN = PROJECT / "SPEC" / "scenario"
sys.path.insert(0, str(PROJECT / "src"))

m = json.load(open(SCEN / "map1-saltwell.json"))
print("keys:", list(m.keys()))
print("width/height:", m.get("width"), m.get("height"))
print("action_class[20] =", m["action_class"][20])
print("action_value[20] =", m["action_value"][20])
print("tiles[20] =", m["tiles"][20])
print()
print("action_cells:")
for c in m["action_cells"]:
    print("  ", json.dumps(c))
print()
print("records keys:", list(m["records"].keys()))
for k, v in m["records"].items():
    print("class", k, "n=", len(v))
    for i, r in enumerate(v):
        print("   slot", i + 1, json.dumps(r)[:200])
