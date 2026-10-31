"""Probe 23: dump the compiled map cells around (2,20) and (3,20) in Saltwell,
plus the JSON action_class row 20, to settle the bump coordinate question."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wlengine.scenario as S  # noqa: E402

DATA = os.path.join(ROOT, "tests", "fixtures-generated", "dd3")


def main():
    sc = S.load(DATA)
    m = sc.map(1)
    print("map1 size", m["size"])
    for y in (19, 20, 21):
        print("y=%d cls" % y, m["cells"]["actionClass"][y][:8])
        print("y=%d act" % y, m["cells"]["action"][y][:8])
    j = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
    print("json cls row20", j["action_class"][20][:8])
    print("json act row20", j["action_value"][20][:8])
    print("json tiles row20", j["tiles"][20][:8])
    print("action_cells sample", json.dumps(j["action_cells"][:6], indent=1))


if __name__ == "__main__":
    main()
