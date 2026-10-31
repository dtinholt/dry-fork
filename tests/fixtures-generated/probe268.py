"""Probe 268: CP6 segment diff (engine vs reference).

Run: python3 tests/fixtures-generated/probe268.py
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


def strip(e):
    return {k: v for k, v in e.items() if k != "seq"}


def segments(events):
    out, cur = {}, []
    for e in events:
        cur.append(strip(e))
        if e.get("type") == "checkpoint":
            out[e.get("name")] = cur
            cur = []
    return out


def main():
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    wt = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough.json"))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    ref = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json"))["events"]
    g = segments(ev)
    w = segments(ref)
    for name in ("CP6", "CP7", "CP8", "CP9", "CP10"):
        a, b = g.get(name, []), w.get(name, [])
        print("=== segment", name, "len", len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                print("  first diff at", i)
                for j in range(max(0, i - 6), min(len(b), i + 6)):
                    print("   ", j, "REF", json.dumps(b[j]))
                    print("   ", j, "ENG", json.dumps(a[j]) if j < len(a) else "-")
                break
        else:
            if len(a) != len(b):
                print("  length differs")


main()
