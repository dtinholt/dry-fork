"""Probe 6: raw ASCII map lines from SPEC-05 and the reference log bumps."""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")


def main():
    text = open(SPEC, encoding="utf-8").read()
    lines = text.splitlines()
    # find the Saltwell ascii block
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("00000000001111111111222222222233"):
            start = i
            break
    print("header line index", start)
    for j in range(start, start + 34):
        ln = lines[j]
        print("%3d len=%2d %r" % (j, len(ln), ln))

    print("=" * 70)
    ref = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")))
    evs = ref["events"] if isinstance(ref, dict) else ref
    for e in evs:
        if e.get("type") == "bump":
            print("bump", e)
    print("=" * 70)
    print("reference keys:", list(ref.keys()) if isinstance(ref, dict) else "list")


if __name__ == "__main__":
    main()
