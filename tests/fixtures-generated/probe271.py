"""Probe 271: record_at after the class change (map2 26,14) and (map3 16,6).

Run: python3 tests/fixtures-generated/probe271.py
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
    for loc, x, y in ((2, 26, 14), (3, 16, 6)):
        m = s.map(loc)
        for cls, act in ((4, 2), (4, 1), (4, 5), (4, 4)):
            m["cells"]["actionClass"][y][x] = cls
            m["cells"]["action"][y][x] = act
            rec = maps.record_at(m, x, y)
            print(loc, (x, y), cls, act, "rec", json.dumps(rec),
                  "tail", maps.apply_tail(rec) if rec else None,
                  "img", maps.image_at(m, x, y))
        # restore
        m["cells"]["actionClass"][y][x] = 4
        m["cells"]["action"][y][x] = 2 if loc == 2 else 5


main()
