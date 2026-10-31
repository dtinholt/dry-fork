"""Probe 20: full cell comparison of the compiled Saltwell map vs the JSON.

Run:  python3 tests/fixtures-generated/probe20.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402


def main():
    d = tempfile.mkdtemp(prefix="probe20-")
    import wlengine.scenario as S
    S.compile(str(W.SCENARIO), d)
    import wlengine.maps as M
    m = M.load_map(d, 1)
    src = json.load(open(os.path.join(str(W.SCENARIO), "map1-saltwell.json")))
    cls = src["action_class"]
    act = src["action_value"]
    til = src["tiles"]
    diffs = 0
    for y in range(32):
        for x in range(32):
            g = (m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x], m["cells"]["image"][y][x])
            w = (cls[y][x], act[y][x], til[y][x] + 10)
            if g != w:
                diffs += 1
                if diffs < 40:
                    print("diff (%2d,%2d) engine=%s json=%s" % (x, y, g, w))
    print("total diffs", diffs)
    print("=" * 70)
    print("json row 17 cls:", json.dumps(cls[17]))
    print("json row 17 act:", json.dumps(act[17]))
    print("json row 17 til:", json.dumps(til[17]))
    print("eng  row 17 cls:", json.dumps(m["cells"]["actionClass"][17]))
    print("eng  row 17 img:", json.dumps(m["cells"]["image"][17]))
    print("=" * 70)
    for (x, y) in ((7, 17), (8, 17), (2, 20), (3, 20), (15, 11), (15, 31)):
        print("is_passable(%d,%d) = %s" % (x, y, M.is_passable(m, x, y)))
    print("=" * 70)
    print("action_cells:", json.dumps(src["action_cells"])[:2000])


if __name__ == "__main__":
    main()
