"""Probe 256: dump the reference log checkpoints CP4 and CP5-pre-save and the
engine's, side by side, plus the reference combat events around CP4.

Run: python3 tests/fixtures-generated/probe256.py
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
    ref = W.load_json(W.SCENARIO / "walkthrough-reference-log.json")["events"]
    print("reference log events:", len(ref))
    cps = {e.get("name"): e.get("state") for e in ref if e.get("type") == "checkpoint"}
    print("checkpoint names:", list(cps))
    for name in ("CP4", "CP5-pre-save", "CP5"):
        st = cps.get(name)
        if st is None:
            print(name, "MISSING")
            continue
        print("=== ref", name, "===")
        print("  location/x/y/steps/day/hour/minute:", st.get("location"), st.get("x"), st.get("y"),
              st.get("steps"), st.get("day"), st.get("hour"), st.get("minute"))
        print("  cell_changes:", json.dumps(st.get("cell_changes")))
        print("  party hp:", [m.get("hp") for m in st.get("party") or []])
        print("  party items:", [m.get("items") for m in st.get("party") or []])
        print("  rng_state:", st.get("rng_state"))

    # engine
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    ecps = {e.get("name"): e.get("state") for e in ev if e.get("type") == "checkpoint"}
    for name in ("CP4", "CP5-pre-save", "CP5"):
        st = ecps.get(name)
        if st is None:
            print("engine", name, "MISSING")
            continue
        print("=== engine", name, "===")
        print("  location/x/y/steps/day/hour/minute:", st.get("location"), st.get("x"), st.get("y"),
              st.get("steps"), st.get("day"), st.get("hour"), st.get("minute"))
        print("  cell_changes:", json.dumps(st.get("cell_changes")))
        print("  party hp:", [m.get("hp") for m in st.get("party") or []])
        print("  party items:", [m.get("items") for m in st.get("party") or []])
        print("  rng_state:", st.get("rng_state"))

    # reference combat events around CP4
    print("=== reference events from encounter_start to CP4 ===")
    started = False
    for e in ref:
        if e.get("type") == "encounter_start":
            started = True
        if started:
            print(json.dumps(e))
        if e.get("type") == "checkpoint" and e.get("name") == "CP4":
            break


main()
