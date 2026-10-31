"""Probe 8: compare SPEC-05 Saltwell ASCII art with map1-saltwell.json tiles."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")


def main():
    text = open(SPEC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(text)
                 if ln.strip().startswith("00000000001111111111222222222233") and len(ln.strip()) == 32)
    art = []
    for j in range(start + 2, start + 34):
        ln = text[j]
        body = ln[5:-1] if ln.endswith("|") else ln[5:]
        art.append(body)
    mj = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
    tiles = mj["tiles"]
    cls = mj["action_class"]
    print("art row lengths:", sorted(set(len(r) for r in art)))
    for y in range(32):
        print("y=%2d art=%r" % (y, art[y]))
        print("      jsn=%r" % "".join("." if t == 0 else "#" for t in tiles[y]))
        print("      cls=%r" % "".join("." if c == 0 else str(c) for c in cls[y]))


if __name__ == "__main__":
    main()
