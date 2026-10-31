"""Probe 317: where does the location name 'Saltwell' live in the compiled data?

Run: python3 tests/fixtures-generated/probe317.py
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
    dd = tempfile.mkdtemp(prefix="probe317-")
    scenario.compile(SCEN, dd)
    print("data dir:", dd)
    for name in sorted(os.listdir(dd)):
        p = os.path.join(dd, name)
        with open(p, "rb") as fh:
            data = fh.read()
        for needle in (b"Saltwell", b"Ninemile", b"Pumphouse", b"Dry Fork"):
            i = data.find(needle)
            if i >= 0:
                print("  %-16s %-10s at %d" % (name, needle.decode(), i))
    sc = headless._load_scenario(dd)
    print("labstr tables:", len(sc.labstr))
    for ti, tbl in enumerate(sc.labstr):
        print("table", ti, "len", len(tbl))
        for i, s in enumerate(tbl[:40]):
            if s:
                print("   ", i, repr(s[:80]))
    print("map_string(1, 0..8):")
    for i in range(9):
        try:
            print("   ", i, repr(sc.map_string(1, i)))
        except Exception as e:
            print("   ", i, "err", repr(e))
    print("hooks keys:", sorted(sc.hooks[0].keys()) if sc.hooks else None)
    print("hooks sample:", json.dumps(sc.hooks[:3], default=str)[:600])
    # scenario.py source: look for location name handling
    src = open(os.path.join(PROJ, "src", "wlengine", "scenario.py"), encoding="utf-8").read()
    for i, line in enumerate(src.splitlines(), 1):
        if "name" in line and ("location" in line.lower() or "loc" in line.lower()):
            print("scenario.py:%d %s" % (i, line.strip()))
    print("scenario.json locations names:", [l["name"] for l in
          json.load(open(os.path.join(SCEN, "scenario.json")))["locations"]])


main()
