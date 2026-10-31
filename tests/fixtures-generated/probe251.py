"""Probe 251: compile the scenario with the engine, then ask the oracle tool
for its view of the compiled data; print the oracle's map1 action cells and
the expected view. Also print the engine's own compiled map1 cells.

Run: python3 tests/fixtures-generated/probe251.py
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
print("compiled to", d)
print("files:", sorted(p.name for p in d.iterdir()))

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(d),
                    str(ROOT / "SPEC" / "scenario")], capture_output=True, text=True)
print("oracle rc", r.returncode)
if r.stderr:
    print("stderr:", r.stderr[-3000:])
data = json.loads(r.stdout)
print("keys", list(data.keys()))
print("errors", data.get("errors"))
print("oracle sections", list(data.get("oracle", {}).keys()))
print("expected sections", list(data.get("expected", {}).keys()))
for sec in ("maps", "map1", "cells"):
    if sec in data.get("oracle", {}):
        print("=== oracle", sec, "===")
        print(json.dumps(data["oracle"][sec], indent=1)[:4000])
