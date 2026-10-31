"""Probe 262: CP5-pre-save cell_changes vs LABSTATE.BIN, and the reference log
segment around the save.

Run: python3 tests/fixtures-generated/probe262.py
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

SEED = 20261021


def main():
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP5-pre-save":
            break
    ev = hl.run(str(d), {"seed": SEED, "script": script}, SEED)
    ck = None
    for e in ev:
        if e.get("type") == "checkpoint" and e.get("name") == "CP5-pre-save":
            ck = e
    st = ck["state"]
    print("=== checkpoint cell_changes (raw order) ===")
    print(json.dumps(st.get("cell_changes")))
    print("=== checkpoint cell_changes (sorted loc,y,x) ===")
    print(json.dumps(sorted(st.get("cell_changes") or [], key=lambda c: (c[0], c[2], c[1]))))
    print("steps", ck["state"].get("steps"), "day", ck["state"].get("day"),
          "rng", ck["state"].get("rng_state"))
    # now run the save script (CP5-pre-save + S)
    script2 = list(script) + ["S"]
    ev2 = hl.run(str(d), {"seed": SEED, "script": script2}, SEED)
    for e in ev2:
        if e.get("type") == "checkpoint" and e.get("name") == "CP5-pre-save":
            st = e["state"]
    print("=== after save: checkpoint cell_changes (sorted) ===")
    print(json.dumps(sorted(st.get("cell_changes") or [], key=lambda c: (c[0], c[2], c[1]))))
    lab = d / "LABSTATE.BIN"
    raw = lab.read_bytes()
    print("LABSTATE.BIN len", len(raw))
    n = int.from_bytes(raw[0x14:0x16], "little")
    print("n", n, "steps", int.from_bytes(raw[8:12], "little"),
          "day", int.from_bytes(raw[12:14], "little"),
          "sec", raw[14], "pad", raw[15],
          "rng", int.from_bytes(raw[16:20], "little"))
    recs = [list(raw[0x16 + 6 * i:0x16 + 6 * i + 6]) for i in range(n)]
    print("records:", json.dumps(recs))
    print("=== all cell_change events in the run ===")
    for e in ev:
        if e.get("type") == "cell_change":
            print(json.dumps(e))


main()
