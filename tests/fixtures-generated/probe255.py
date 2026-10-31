"""Probe 255: M6 CP4/CP5 investigation.

Prints:
  * the walkthrough script up to CP4 and the engine party hp at CP4 for the M6
    seed 20261021, plus the whole combat event stream;
  * the reference log entries around CP4 (locating the log file used by
    tests/test_m6_playable.py);
  * for CP5-pre-save: the checkpoint cell_changes and the LABSTATE.BIN records.

Run: python3 tests/fixtures-generated/probe255.py
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


def find_log():
    for p in sorted((ROOT / "tests").rglob("*")):
        if p.is_file() and p.suffix in (".json", ".txt", ".jsonl", ".log"):
            try:
                txt = p.read_text(errors="replace")
            except Exception:
                continue
            if "CP4" in txt and "checkpoint" in txt:
                print("candidate log:", p.relative_to(ROOT), len(txt))
    return None


def main():
    find_log()
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP4":
            break
    ev = hl.run(str(d), {"seed": SEED, "script": script}, SEED)
    ck = None
    for e in ev:
        if e.get("type") == "checkpoint" and e.get("name") == "CP4":
            ck = e
    print("=== CP4 checkpoint ===")
    if ck:
        print(json.dumps({k: v for k, v in ck.items() if k != "seq"}, indent=1)[:4000])
    print("=== combat events ===")
    started = False
    for e in ev:
        if e.get("type") == "encounter_start":
            started = True
        if started:
            print(json.dumps(e))
        if e.get("type") == "combat_end":
            break

    # CP5-pre-save: cell_changes vs LABSTATE.BIN
    script2 = []
    for item in wt["script"]:
        script2.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP5-pre-save":
            break
    ev2 = hl.run(str(d), {"seed": SEED, "script": script2}, SEED)
    ck2 = None
    for e in ev2:
        if e.get("type") == "checkpoint" and e.get("name") == "CP5-pre-save":
            ck2 = e
    print("=== CP5-pre-save cell_changes ===")
    if ck2:
        print(json.dumps(ck2.get("cell_changes"), indent=1))
    lab = d / "LABSTATE.BIN"
    if lab.exists():
        raw = lab.read_bytes()
        print("LABSTATE.BIN len", len(raw))
        recs = []
        for i in range(0, len(raw), 6):
            recs.append(list(raw[i:i + 6]))
        print("records:", json.dumps(recs, indent=1))
    else:
        print("no LABSTATE.BIN at", lab)


main()
