"""Probe 261: dump the party state (items, weapon status) at CP3 and the item
records for the ammo items, to see why ammo_boxes() returns 0.

Run: python3 tests/fixtures-generated/probe261.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402
import wl_support as W  # noqa: E402

SEED = 20261021


def main():
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP3":
            break
    ev = hl.run(str(d), {"seed": SEED, "script": script}, SEED)
    ck = None
    for e in ev:
        if e.get("type") == "checkpoint" and e.get("name") == "CP3":
            ck = e
    print("=== CP3 party ===")
    for m in ck["state"]["party"]:
        print(json.dumps({k: v for k, v in m.items() if k != "skills"}))
        print("   skills:", m.get("skills"))
    print("=== items.json ===")
    items = W.load_json(W.SCENARIO / "items.json")["items"]
    for it in items:
        print(json.dumps(it))


main()
