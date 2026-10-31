"""Probe 5: map decode nibble convention + engine combat events."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wl_support as W  # noqa: E402


def main():
    mj = W.load_json(W.SCENARIO / "map1-saltwell.json")
    print("conventions:", json.dumps(mj.get("conventions")))
    print("width/height:", mj.get("width"), mj.get("height"))
    print("row20 cls:", mj["action_class"][20])
    print("row20 tiles:", mj["tiles"][20])
    # column 20
    print("col20 cls:", [mj["action_class"][y][20] for y in range(32)])
    print("col20 tiles:", [mj["tiles"][y][20] for y in range(32)])

    # compiled map
    import wlengine.maps as maps
    import wlengine.scenario as scen
    out = os.path.join(HERE, "dd3")
    scen.compile(os.path.join(ROOT, "SPEC", "scenario"), out)
    m = maps.load_map(out, 1)
    print("compiled row20 cls:", m["cells"]["actionClass"][20])
    print("compiled row20 img:", m["cells"]["image"][20])
    print("compiled row20 act:", m["cells"]["action"][20])


if __name__ == "__main__":
    main()
