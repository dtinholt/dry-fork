"""Probe 279: dump party weapons/items at the pump-crawler encounter.

Usage: python3 tests/fixtures-generated/probe279.py [seed]
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261021
    wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    eng = hl.Engine(str(d), seed, {"seed": seed, "script": wt["script"]})
    # run until the encounter at seq 743
    while True:
        ev = eng.step()
        if ev is None:
            break
        if ev.get("type") == "encounter_start":
            break
    print("encounter:", json.dumps(ev))
    for i, m in enumerate(eng.party):
        print("member %d name=%s hp=%s items=%s" % (i + 1, m.get("name"), m.get("hp"),
                                                    m.get("items")))
        items = m.get("items") or []
        if items:
            rec = eng.item_record(items[0][0])
            print("   weapon rec:", json.dumps(rec))
    print("combat:", json.dumps(eng.combat)[:600])


main()
