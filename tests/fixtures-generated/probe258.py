"""Probe 258: dump the reference combat checker source and our combat module
source, so the jam/unjam/reload bookkeeping can be compared without burning
read budget.

Also prints the reference log's raider fight orders and the engine's orders
side by side, and the reference's ammo/jam bookkeeping expectations.

Run: python3 tests/fixtures-generated/probe258.py
"""
from __future__ import annotations

import inspect
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_combat_ref as CR  # noqa: E402
import wlengine.combat as C  # noqa: E402
import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402
import wl_support as W  # noqa: E402

SEED = 20261021


def dump_source(mod, name):
    print("=" * 70)
    print(name)
    print("=" * 70)
    try:
        print(inspect.getsource(mod))
    except Exception as exc:  # pragma: no cover
        print("cannot introspect:", exc)


def fight(events):
    out = []
    started = False
    for e in events:
        if e.get("type") == "encounter_start":
            started = True
        if started:
            out.append(e)
        if e.get("type") == "combat_end":
            break
    return out


def orders(events):
    return [(e.get("round"), e.get("orders")) for e in events
            if e.get("type") == "round_orders"]


def main():
    dump_source(CR, "wl_combat_ref.py")
    dump_source(C, "wlengine/combat.py")

    ref = W.load_json(W.SCENARIO / "walkthrough-reference-log.json")["events"]
    rf = fight(ref)
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    ef = fight(ev)
    print("=" * 70)
    print("reference orders")
    print("=" * 70)
    for r, o in orders(rf):
        print(r, json.dumps(o))
    print("=" * 70)
    print("engine orders")
    print("=" * 70)
    for r, o in orders(ef):
        print(r, json.dumps(o))
    print("=" * 70)
    print("reference jam/unjam/reload events")
    print("=" * 70)
    for e in rf:
        if e.get("type") in ("jam", "unjammed", "reload", "out_of_ammo", "advance"):
            print(json.dumps(e))
    print("=" * 70)
    print("engine jam/unjam/reload events")
    print("=" * 70)
    for e in ef:
        if e.get("type") in ("jam", "unjammed", "reload", "out_of_ammo", "advance"):
            print(json.dumps(e))


main()
