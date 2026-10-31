"""Probe 281: member 6 stats and melee need at the pump-crawler fight.

Usage: python3 tests/fixtures-generated/probe281.py [seed]
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
        if type_ == "round_orders" and ev.get("seq", 0) > 700:
            for i, m in enumerate(eng.party):
                rec, iid = eng.member_weapon(m)
                print("member %d attrs=%s skills=%s weapon=%s skill_level=%s" % (
                    i + 1, m.get("attrs"), m.get("skills"), iid,
                    eng.skill_level(m, rec.get("skill", 0)) if rec else None))
            print("orders:", json.dumps(ev["orders"]))
        return ev

    eng.emit = emit
    eng.new_game(seed)
    eng.run_script(wt["script"])


main()
