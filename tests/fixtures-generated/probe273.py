"""Probe 273: dump the decoded loot records for map2 (26,12) and map3 (9,6).

Run: python3 tests/fixtures-generated/probe273.py
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
    for loc, x, y in ((2, 26, 12), (2, 10, 23), (3, 9, 6), (3, 16, 6), (3, 21, 4)):
        m = s.map(loc)
        rec = maps.record_at(m, x, y)
        print("loc", loc, (x, y), "class", m["cells"]["actionClass"][y][x],
              "action", m["cells"]["action"][y][x])
        print("   rec:", json.dumps(rec))
        print("   tail:", maps.apply_tail(rec) if rec else None)
        print("   img:", maps.image_at(m, x, y))


main()
