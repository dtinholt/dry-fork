#!/usr/bin/env python3
"""Probe the compiled fixture data: dump cell classes / actions / images.

Usage:
    python3 tests/fixtures-generated/probe.py cells 1 20      # row y=20 of loc 1
    python3 tests/fixtures-generated/probe.py col 1 2         # column x=2 of loc 1
    python3 tests/fixtures-generated/probe.py move 1 15 20 LEFT 13
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

DD = os.path.join(HERE, "dd")


def main():
    from wlengine import headless
    cmd = sys.argv[1]
    if cmd == "cells":
        loc, y = int(sys.argv[2]), int(sys.argv[3])
        sc = headless._load_scenario(DD)
        m = sc.map(loc)
        print("size", m["size"])
        print("cls ", m["cells"]["actionClass"][y])
        print("act ", m["cells"]["action"][y])
        print("img ", m["cells"]["image"][y])
    elif cmd == "col":
        loc, x = int(sys.argv[2]), int(sys.argv[3])
        sc = headless._load_scenario(DD)
        m = sc.map(loc)
        print("cls ", [m["cells"]["actionClass"][y][x] for y in range(m["size"])])
        print("act ", [m["cells"]["action"][y][x] for y in range(m["size"])])
        print("img ", [m["cells"]["image"][y][x] for y in range(m["size"])])
    elif cmd == "move":
        loc, x, y = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        keys = sys.argv[5:]
        ev = headless.run(DD, {"script": keys}, 20261021)
        for e in ev:
            print(json.dumps(e))
    else:
        print("unknown command")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
