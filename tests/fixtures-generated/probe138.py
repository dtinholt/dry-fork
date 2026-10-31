"""Probe 138: dump the bump scenario events and the Saltwell map row y=20.

Run with:  pytest tests/fixtures-generated/probe138.py -s
"""
import json

import pytest

pytestmark = pytest.mark.milestone("M5")

SEED = 20261021


def test_probe138(runner):
    print("runner attrs:", [a for a in dir(runner) if not a.startswith("__")])
    ev, extra = runner.run("bump", {"seed": SEED,
                                    "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    print("=== events ===")
    for i, e in enumerate(ev):
        print(i, json.dumps(e, default=str))
    print("=== extra ===")
    print(repr(extra)[:2000])

    sc = None
    eng = None
    for attr in ("sc", "scenario", "engine", "game", "state"):
        obj = getattr(runner, attr, None)
        if obj is not None:
            print("runner.%s = %r" % (attr, obj))
            if hasattr(obj, "map"):
                sc = obj
            if hasattr(obj, "sc"):
                eng = obj
    if eng is not None and sc is None:
        sc = getattr(eng, "sc", None)
    if sc is None:
        print("no scenario found on runner")
        return
    m = sc.map(1)
    print("map keys:", sorted(m.keys()))
    print("size:", m["size"])
    cells = m["cells"]
    print("cell keys:", sorted(cells.keys()))
    y = 20
    for x in range(0, 20):
        print("x=%2d cls=%2d act=%2d img=%2d" % (
            x, cells["actionClass"][y][x], cells["action"][y][x],
            cells["image"][y][x]))
    from wlengine import maps
    for x in range(0, 20):
        rec = maps.record_at(m, x, y)
        print("x=%2d passable=%s rec=%s" % (x, maps.is_passable(m, x, y), rec))
    # also dump the whole row for y=19..21 to see the cactus
    for yy in (19, 20, 21):
        row = []
        for x in range(0, 20):
            row.append("%d/%d" % (cells["actionClass"][yy][x],
                                  cells["action"][yy][x]))
        print("y=%d %s" % (yy, " ".join(row)))
    print("info:", m["info"])
    # party start
    if eng is not None:
        print("engine x,y,loc:", getattr(eng, "x", None), getattr(eng, "y", None),
              getattr(eng, "location", None))
