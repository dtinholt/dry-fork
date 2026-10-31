"""Probe 278: find the first differing event and print context.

Usage: python3 tests/fixtures-generated/probe278.py [seed] [context]
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
    ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]
    wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    ev = hl.run(str(d), {"seed": seed, "script": wt["script"]}, seed)
    n = min(len(ev), len(ref))
    first = None
    for i in range(n):
        if ev[i] != ref[i]:
            first = i
            break
    print("engine events: %d, reference events: %d" % (len(ev), len(ref)))
    if first is None:
        print("no difference in the common prefix")
        return
    print("first difference at index %d" % first)
    for i in range(max(0, first - ctx), min(n, first + ctx + 1)):
        mark = "!!" if ev[i] != ref[i] else "  "
        print("%s %4d ref=%s" % (mark, i, json.dumps(ref[i])[:200]))
        if ev[i] != ref[i]:
            print("        eng=%s" % json.dumps(ev[i])[:200])


main()
