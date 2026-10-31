"""Probe 311: compile the scenario, then inspect the scenario object API and
the engine's first-frame state.

Run: python3 tests/fixtures-generated/probe311.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "src"))

from wlengine import headless, scenario  # noqa: E402

SCEN = os.path.join(PROJ, "SPEC", "scenario")


def main():
    dd = tempfile.mkdtemp(prefix="probe311-")
    scenario.compile(SCEN, dd)
    print("data dir:", dd)
    print("files:", sorted(os.listdir(dd)))
    sc = headless._load_scenario(dd)
    print("sc type:", type(sc))
    names = [n for n in dir(sc) if not n.startswith("__")]
    print("attrs:", names)
    print("start:", getattr(sc, "start", None))
    for n in names:
        v = getattr(sc, n)
        if callable(v):
            continue
        try:
            s = repr(v)
        except Exception as e:
            s = "<%s>" % e
        print("  %s = %s" % (n, s[:300]))
    print("map-ish attrs:", [n for n in names if "map" in n.lower() or "loc" in n.lower()])
    pp = sc.premade_party()
    print("premade party:", json.dumps(pp, default=str)[:900])

    eng = headless.Engine(dd, seed=20261021)
    eng.new_game(20261021)
    print("engine location/x/y:", eng.location, eng.x, eng.y)
    print("engine hour/minute/day:", eng.hour, eng.minute, eng.day)
    print("engine events:", eng.events)
    print("engine attrs with map:", [n for n in dir(eng) if "map" in n.lower() or "loc" in n.lower()])
    print("engine sc attrs:", [n for n in dir(eng.sc) if "map" in n.lower() or "loc" in n.lower()])
    # try to get the map for location 1
    for meth in ("map_for_location", "location_map", "map_at", "get_map", "map"):
        fn = getattr(eng.sc, meth, None)
        if fn is None:
            continue
        try:
            m = fn(1)
            print("sc.%s(1) ->" % meth, type(m), (list(m.keys()) if isinstance(m, dict) else dir(m))[:40])
        except Exception as e:
            print("sc.%s(1) failed: %r" % (meth, e))
    # location name
    for meth in ("location_name", "name_of_location", "location"):
        fn = getattr(eng.sc, meth, None)
        if fn is None:
            continue
        try:
            print("sc.%s(1) ->" % meth, fn(1))
        except Exception as e:
            print("sc.%s(1) failed: %r" % (meth, e))


main()
