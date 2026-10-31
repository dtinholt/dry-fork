"""Probe 274: dump engine vs reference events in a seq window.

Usage: python3 tests/fixtures-generated/probe274.py [lo] [hi]
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


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 700
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]
    wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    ev = hl.run(str(d), {"seed": SEED, "script": wt["script"]}, SEED)
    by = {e.get("seq"): e for e in ev}
    for i in range(lo, hi + 1):
        a = by.get(i)
        b = ref[i] if i < len(ref) else None
        mark = "  " if a == b else "!!"
        print("%s %4d ref=%s" % (mark, i, json.dumps(b)[:220]))
        if a != b:
            print("        eng=%s" % json.dumps(a)[:220])


main()
