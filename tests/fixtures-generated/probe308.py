"""Probe 308: read the SPEC-05 5.2 Saltwell art and check the neighbourhood of
the start (15,20); also check every map at (14,20).

Run: python3 tests/fixtures-generated/probe308.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
SCEN = os.path.join(ROOT, "SPEC", "scenario")
SPEC05 = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")


def main():
    text = open(SPEC05, encoding="utf-8").read()
    # find the Saltwell section
    i = text.find("### 5.2 Saltwell")
    j = text.find("### 5.3", i)
    sec = text[i:j]
    print(sec[:3000])
    print("...")
    # extract lines that look like art rows
    rows = []
    for line in sec.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and len(s) > 30:
            rows.append(s)
    print("art rows found:", len(rows))
    for k, r in enumerate(rows):
        print("%2d %s" % (k, r))
    print()
    # compiled maps
    from wlengine import scenario as S
    d = tempfile.mkdtemp(prefix="probe308-")
    S.compile(SCEN, d)
    sc = S.load(d)
    for loc in (0, 1, 2, 3):
        m = sc.map(loc)
        if m is None:
            print("map", loc, "missing")
            continue
        img = m["cells"]["image"]
        ac = m["cells"]["actionClass"]
        print("map", loc, "size", m["size"],
              "(14,20)=", img[20][14], "ac", ac[20][14],
              "(20,14)=", img[14][20], "ac", ac[14][20],
              "(15,19)=", img[19][15], "ac", ac[19][15],
              "(14,19)=", img[19][14], "ac", ac[19][14],
              "(15,21)=", img[21][15], "ac", ac[21][15],
              "(14,21)=", img[21][14], "ac", ac[21][14])


if __name__ == "__main__":
    main()
