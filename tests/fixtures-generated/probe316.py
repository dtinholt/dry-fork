"""Probe 316: location names, map image access, and the CLI entry point.

Run: python3 tests/fixtures-generated/probe316.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "src"))

from wlengine import headless, maps, scenario  # noqa: E402

SCEN = os.path.join(PROJ, "SPEC", "scenario")


def main():
    sc_json = json.load(open(os.path.join(SCEN, "scenario.json")))
    print("scenario.json keys:", sorted(sc_json.keys()))
    print(json.dumps(sc_json, indent=1)[:2500])
    for name in ("map0-overworld.json", "map1-saltwell.json"):
        j = json.load(open(os.path.join(SCEN, name)))
        print(name, "name=", j.get("name"), "location=", j.get("location"))
    print("maps.py public:", [n for n in dir(maps) if not n.startswith("_")])
    dd = tempfile.mkdtemp(prefix="probe316-")
    scenario.compile(SCEN, dd)
    sc = headless._load_scenario(dd)
    m = sc.map(1)
    print("compiled map keys:", sorted(m.keys()))
    print("compiled map info:", json.dumps(m["info"]))
    print("scenario attrs:", [n for n in dir(sc) if not n.startswith("_")])
    # location name?
    for n in ("location_name", "names", "locations"):
        print("has", n, hasattr(sc, n))
    print("scenario.json 'locations'?", sc_json.get("locations"))
    # engine
    eng = headless.Engine(dd, seed=1)
    eng.new_game(1)
    print("engine map access:", hasattr(eng, "map"))
    print("maps.is_passable sig ok:", maps.is_passable(m, 14, 20))
    print("maps.record_at(m,14,20):", maps.record_at(m, 14, 20))
    print("maps module funcs:", [n for n in dir(maps) if not n.startswith("_")])


main()
