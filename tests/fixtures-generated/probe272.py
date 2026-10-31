"""Probe 272: diff engine checkpoints vs the reference log for the walkthrough.

Prints, for every checkpoint name:
  * the engine's cell_changes vs the reference's cell_changes (element by element)
  * the engine's party items vs the reference's party items
  * the engine's cell_change events vs the reference's cell_change events

Run: python3 tests/fixtures-generated/probe272.py
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

SEED = 20261021


def find_ref():
    cands = sorted((ROOT / "SPEC" / "scenario").glob("*reference*log*.json"))
    cands += sorted((ROOT / "SPEC" / "scenario").glob("*log*reference*.json"))
    if not cands:
        raise SystemExit("no reference log found")
    return cands[0]


def cps(events):
    return {e.get("name"): e.get("state") for e in events if e.get("type") == "checkpoint"}


def main():
    ref_path = find_ref()
    print("reference log:", ref_path)
    ref = json.loads(ref_path.read_text())
    if isinstance(ref, dict):
        ref = ref["events"]
    wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    got = cps(ev)
    want = cps(ref)
    for name in [c["name"] for c in wt["checkpoints"]]:
        g, w = got.get(name), want.get(name)
        print("=" * 70)
        print("checkpoint", name)
        if g is None or w is None:
            print("  missing:", "engine" if g is None else "", "ref" if w is None else "")
            continue
        gc, wc = g.get("cell_changes"), w.get("cell_changes")
        if gc != wc:
            print("  cell_changes differ")
            for i in range(max(len(gc or []), len(wc or []))):
                a = (gc or [])[i] if i < len(gc or []) else None
                b = (wc or [])[i] if i < len(wc or []) else None
                mark = "  " if a == b else "!!"
                print("   %s [%d] ref=%s eng=%s" % (mark, i, b, a))
        gp, wp = g.get("party"), w.get("party")
        if gp != wp:
            print("  party differs")
            for i in range(max(len(gp or []), len(wp or []))):
                a = (gp or [])[i] if i < len(gp or []) else None
                b = (wp or [])[i] if i < len(wp or []) else None
                if a == b:
                    continue
                print("   !! slot %d" % i)
                for k in sorted(set(list((a or {}).keys()) + list((b or {}).keys()))):
                    if (a or {}).get(k) != (b or {}).get(k):
                        print("      %-12s ref=%s eng=%s" % (k, (b or {}).get(k), (a or {}).get(k)))
        for k in sorted(set(list(g.keys()) + list(w.keys()))):
            if k in ("cell_changes", "party"):
                continue
            if g.get(k) != w.get(k):
                print("  %-12s ref=%s eng=%s" % (k, w.get(k), g.get(k)))
    print("=" * 70)
    print("cell_change events")
    ge = [e for e in ev if e.get("type") == "cell_change"]
    we = [e for e in ref if e.get("type") == "cell_change"]
    for i in range(max(len(ge), len(we))):
        a = ge[i] if i < len(ge) else None
        b = we[i] if i < len(we) else None
        mark = "  " if a == b else "!!"
        print(" %s [%d] ref=%s eng=%s" % (mark, i, b, a))


main()
