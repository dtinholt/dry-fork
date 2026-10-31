"""Probe 306: compile the scenario and inspect the compiled map1 arrays.

Run: python3 tests/fixtures-generated/probe306.py
"""
from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    from wlengine import scenario as S, maps
    d = tempfile.mkdtemp(prefix="probe306-")
    S.compile(SCEN, d)
    print("compiled to", d)
    print("files:", sorted(os.listdir(d)))
    sc = S.load(d)
    m = sc.map(1)
    print("map1 keys:", sorted(m.keys()))
    print("size:", m["size"])
    cells = m["cells"]
    print("cells keys:", sorted(cells.keys()))
    img = cells["image"]
    ac = cells["actionClass"]
    av = cells["action"]
    print("image[20][14] =", img[20][14], " image[14][20] =", img[14][20])
    print("image[20][15] =", img[20][15], " image[15][20] =", img[15][20])
    print("ac[20][14] =", ac[20][14], " ac[14][20] =", ac[14][20])
    print("ac[20][2] =", ac[20][2], " ac[2][20] =", ac[2][20])
    print("ac[20][3] =", ac[20][3], " ac[3][20] =", ac[3][20])
    print("av[20][2] =", av[20][2], " av[2][20] =", av[2][20])
    print("av[20][3] =", av[20][3], " av[3][20] =", av[3][20])
    print("row20 image:", img[20])
    print("col14 image:", [img[y][14] for y in range(32)])
    print("row14 image:", img[14])
    print("col20 image:", [img[y][20] for y in range(32)])
    print("info:", m["info"])
    print("strings count:", len(m["strings"]))
    print("records keys:", sorted(m["records"].keys())[:20] if isinstance(m["records"], dict) else type(m["records"]))
    print("start:", sc.start)
    print("party:", [(p["slot"], p["name"], p["hp"], p["max_hp"]) for p in sc.premade_party()])


if __name__ == "__main__":
    main()
