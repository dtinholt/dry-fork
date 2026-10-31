"""Probe 270: map2 record at (26,14) and map3 at (16,6).

Run: python3 tests/fixtures-generated/probe270.py
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
    for loc, x, y in ((2, 26, 14), (3, 16, 6), (2, 26, 12), (3, 21, 4)):
        m = s.map(loc)
        rec = maps.record_at(m, x, y)
        print(loc, (x, y), "cls", m["cells"]["actionClass"][y][x],
              "act", m["cells"]["action"][y][x],
              "img", m["cells"]["image"][y][x])
        print("   rec", json.dumps(rec))
        print("   tail", maps.apply_tail(rec) if rec else None)
    print("=== map2 class-4 records ===")
    m = s.map(2)
    size = m["size"]
    for y in range(size):
        for x in range(size):
            if m["cells"]["actionClass"][y][x] == 4:
                print((x, y), json.dumps(maps.record_at(m, x, y)))


main()
