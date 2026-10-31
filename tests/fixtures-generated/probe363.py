"""Probe 363: dump the Saltwell action_class rows 18..22 from the frozen
scenario JSON and from the compiled data, side by side, to see whether the
compiler shifts the cactus.

Also dumps the 'action_cells' entries with class 11 and their coordinates.
"""
import os
import sys
import json
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

SCEN = os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")


def find_data():
    pats = ("tests/fixtures-generated/*data", "tests/fixtures-generated/*/*data",
            "tests/fixtures-generated/*", "tests/fixtures-generated/*/*")
    for pat in pats:
        for c in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.isdir(c) and os.path.isfile(os.path.join(c, "LABTABLES.BIN")):
                return c
    return None


def main():
    with open(SCEN, encoding="utf-8") as fh:
        j = json.load(fh)
    ac = j["action_class"]
    print("JSON action_class rows 18..22 (x 0..8):")
    for y in range(18, 23):
        print("  y=%d %s" % (y, ac[y][:9]))
    print("JSON tiles rows 18..22 (x 0..8):")
    for y in range(18, 23):
        print("  y=%d %s" % (y, j["tiles"][y][:9]))
    print("JSON action_cells with class 11:")
    for c in j["action_cells"]:
        if c.get("class") == 11:
            print("   ", c)

    dd = find_data()
    print("data dir:", dd)
    if dd is None:
        return
    from wlengine import scenario as sc_mod
    sc = sc_mod.Scenario(dd)
    m = sc.map(1)
    print("COMPILED actionClass rows 18..22 (x 0..8):")
    for y in range(18, 23):
        print("  y=%d %s" % (y, m["cells"]["actionClass"][y][:9]))
    print("COMPILED image rows 18..22 (x 0..8):")
    for y in range(18, 23):
        print("  y=%d %s" % (y, m["cells"]["image"][y][:9]))
    print("COMPILED action rows 18..22 (x 0..8):")
    for y in range(18, 23):
        print("  y=%d %s" % (y, m["cells"]["action"][y][:9]))


main()
