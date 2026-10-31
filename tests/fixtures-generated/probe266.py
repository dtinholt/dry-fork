"""Probe 266: map0 record at (31,41) and neighbours.

Run: python3 tests/fixtures-generated/probe266.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import wlengine.maps as maps  # noqa: E402
import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402


def main():
    d = Path(tempfile.mkdtemp())
    sc.compile(str(ROOT / "SPEC" / "scenario"), str(d))
    s = hl._load_scenario(str(d))
    m = s.map(0)
    for (x, y) in [(30, 41), (31, 41), (32, 41), (26, 14), (26, 12), (18, 17)]:
        rec = maps.record_at(m, x, y)
        print((x, y), "cls", m["cells"]["actionClass"][y][x],
              "act", m["cells"]["action"][y][x],
              "img", m["cells"]["image"][y][x])
        print("   rec", json.dumps(rec))
    print("=== all class-1 records in map0 ===")
    size = m["size"]
    for y in range(size):
        for x in range(size):
            if m["cells"]["actionClass"][y][x] == 1:
                print((x, y), json.dumps(maps.record_at(m, x, y)))


main()
