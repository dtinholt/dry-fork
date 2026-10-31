"""Probe 307: hunt for the source of the look test's expected image 28.

Run: python3 tests/fixtures-generated/probe307.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    from wlengine import scenario as S
    d = tempfile.mkdtemp(prefix="probe307-")
    S.compile(SCEN, d)
    sc = S.load(d)
    m = sc.map(1)
    img = m["cells"]["image"]
    ac = m["cells"]["actionClass"]
    av = m["cells"]["action"]
    cells = [(14, 20), (15, 20), (16, 20), (15, 19), (15, 21), (14, 19), (14, 21),
             (20, 14), (20, 15), (20, 16), (19, 15), (21, 15), (14, 18), (18, 14)]
    for (x, y) in cells:
        print("(%2d,%2d) image=%3d class=%2d action=%2d" % (x, y, img[y][x], ac[y][x], av[y][x]))
    print()
    print("all cells with image 28 in map1:")
    for y in range(32):
        for x in range(32):
            if img[y][x] == 28:
                print("   (%d,%d)" % (x, y))
    print()
    print("start:", sc.start)
    print("map0 image at (14,20),(15,20):")
    m0 = sc.map(0)
    if m0:
        print("   ", m0["cells"]["image"][20][14], m0["cells"]["image"][20][15])
    print()
    ref = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json"), encoding="utf-8"))
    evs = ref["events"]
    print("first 25 reference events:")
    for e in evs[:25]:
        print("   ", json.dumps(e)[:200])
    print()
    print("reference events with image 28:")
    for e in evs:
        if e.get("image") == 28:
            print("   ", json.dumps(e)[:200])
    print()
    print("reference events with x==14 and y==20:")
    for e in evs:
        if e.get("x") == 14 and e.get("y") == 20:
            print("   ", json.dumps(e)[:200])
    print()
    print("reference events with type look/bump:")
    for e in evs:
        if e.get("type") in ("look", "bump"):
            print("   ", json.dumps(e)[:200])
    print()
    wt = json.load(open(os.path.join(SCEN, "walkthrough.json"), encoding="utf-8"))
    for cp in wt["checkpoints"]:
        if cp["name"] in ("CP1", "CP2"):
            print(cp["name"], "expected:", json.dumps(cp["expected"])[:400])


if __name__ == "__main__":
    main()
