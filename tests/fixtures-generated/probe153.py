"""Probe 153: find the cactus / class-11 cells on Saltwell (location 1) row 20
in the scenario JSON and in the compiled map, plus the reference log bumps.

Run: python3 tests/fixtures-generated/probe153.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    import wl_support as W
    from wlengine import scenario as scen

    # scenario JSON
    maps_json = W.load_json(W.SCENARIO / "maps.json")
    print("maps.json keys:", list(maps_json)[:10])
    for m in maps_json.get("maps", []):
        if m.get("location") == 1 or m.get("name") == "Saltwell":
            print("MAP", json.dumps({k: v for k, v in m.items() if k != "cells"}, sort_keys=True)[:2000])
            cells = m.get("cells") or {}
            print("cell keys:", list(cells))
            for key in cells:
                grid = cells[key]
                if isinstance(grid, list) and grid and isinstance(grid[0], list):
                    print("  %s row20:" % key, grid[20][:8])
            break

    # reference log bumps
    ref = W.load_json(W.REFERENCE_LOG)["events"]
    print("--- reference bumps ---")
    for e in ref:
        if e.get("type") == "bump":
            print(json.dumps(e, sort_keys=True))
    print("--- reference moves on location 1 near y=20 ---")
    for e in ref:
        if e.get("type") == "move" and e.get("location") == 1 and e.get("y") == 20:
            print(json.dumps(e, sort_keys=True))


if __name__ == "__main__":
    main()
