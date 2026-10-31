"""Probe 305: check transposed vs normal indexing for the look and bump tests.

Run: python3 tests/fixtures-generated/probe305.py
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    m = json.load(open(os.path.join(SCEN, "map1-saltwell.json"), encoding="utf-8"))
    tiles = m["tiles"]
    ac = m["action_class"]
    print("tiles[20][14] =", tiles[20][14], "-> image", tiles[20][14] + 10)
    print("tiles[14][20] =", tiles[14][20], "-> image", tiles[14][20] + 10)
    print("ac[20][14] =", ac[20][14], " ac[14][20] =", ac[14][20])
    print("tiles[20][15] =", tiles[20][15], "-> image", tiles[20][15] + 10)
    print()
    print("bump test: tiles[20][3] =", tiles[20][3], " tiles[20][2] =", tiles[20][2])
    print("bump test transposed: tiles[3][20] =", tiles[3][20], " tiles[2][20] =", tiles[2][20])
    print("ac[20][3] =", ac[20][3], " ac[20][2] =", ac[20][2])
    print("ac[3][20] =", ac[3][20], " ac[2][20] =", ac[2][20])
    print()
    print("row 14:", tiles[14])
    print("col 20:", [tiles[y][20] for y in range(32)])
    print("row 20:", tiles[20])
    print("col 14:", [tiles[y][14] for y in range(32)])
    print()
    print("action_cells keys:", sorted(m["action_cells"].keys()) if isinstance(m["action_cells"], dict) else type(m["action_cells"]))
    print("records sample:", json.dumps(m["records"][:3])[:600] if isinstance(m["records"], list) else json.dumps(m["records"])[:600])
    print("action_value[20][14] =", m["action_value"][20][14], "action_value[14][20] =", m["action_value"][14][20])


if __name__ == "__main__":
    main()
