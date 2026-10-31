"""Probe 309: how does the engine know a location's name? Dump
containers.read_tables keys and look for names; also dump LABSTR tables.

Run: python3 tests/fixtures-generated/probe309.py
"""
from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    from wlengine import scenario as S, containers, strings
    d = tempfile.mkdtemp(prefix="probe309-")
    S.compile(SCEN, d)
    t = containers.read_tables(os.path.join(d, "LABTABLES.BIN"))
    print("read_tables keys:", sorted(t.keys()))
    for k, v in t.items():
        s = repr(v)
        print("  %s = %s" % (k, s[:300]))
    print()
    labstr = strings.read_labstr(os.path.join(d, "LABSTR.BIN"))
    print("labstr type:", type(labstr), "len:", len(labstr))
    for i, tbl in enumerate(labstr):
        print("table", i, "len", len(tbl), "first 12:", tbl[:12])
    print()
    # grep src for location_name
    for root, _dirs, files in os.walk(os.path.join(SRC, "wlengine")):
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            p = os.path.join(root, f)
            for i, line in enumerate(open(p, encoding="utf-8").read().splitlines(), 1):
                if "location_name" in line or "locationName" in line or "names" in line:
                    print("%s:%d| %s" % (f, i, line))


if __name__ == "__main__":
    main()
