"""Probe 280: dump party weapons/items at the pump-crawler encounter.

Usage: python3 tests/fixtures-generated/probe280.py [seed]
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
    orig = eng.emit

    def emit(type_, **kw):
        ev = orig(type_, **kw)
        if type_ == "encounter_start" and ev.get("seq", 0) > 700:
            print("encounter:", json.dumps(ev))
            for i, m in enumerate(eng.party):
                print("member %d name=%s hp=%s items=%s" % (
                    i + 1, m.get("name"), m.get("hp"), m.get("items")))
                items = m.get("items") or []
                if items:
                    rec = eng.item_record(items[0][0])
                    print("   weapon rec:", json.dumps(rec))
            for gi, g in enumerate(eng.combat["groups"]):
                print("group %d band=%s hp=%s mob=%s" % (
                    gi + 1, g.get("band"), g["hp"], json.dumps(g["mob"])[:200]))
            print("global band:", eng.combat.get("band"))
        return ev

    eng.emit = emit
    eng.new_game(seed)
    eng.run_script(wt["script"])


main()
