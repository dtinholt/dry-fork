"""Probe 7: extract the Saltwell ASCII block from SPEC-05 and compare to JSON."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")


def main():
    text = open(SPEC, encoding="utf-8").read()
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("00000000001111111111222222222233") and len(ln.strip()) == 32:
            print("Saltwell header at", i)
            for j in range(i, i + 36):
                print("%3d len=%2d %r" % (j, len(lines[j]), lines[j]))
            break
    mj = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
    print("JSON row20:", "".join(str(c) for c in mj["action_class"][20]))
    print("JSON row20 tiles:", mj["tiles"][20])


if __name__ == "__main__":
    main()
