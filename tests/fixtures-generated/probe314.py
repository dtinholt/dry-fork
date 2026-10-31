"""Probe 314: compare compiled map image/actionClass with the JSON scenario map
in both index orders, to explain the look test's expectation.

Run: python3 tests/fixtures-generated/probe314.py
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
    dd = tempfile.mkdtemp(prefix="probe314-")
    scenario.compile(SCEN, dd)
    sc = headless._load_scenario(dd)
    m = sc.map(1)
    img = m["cells"]["image"]
    ac = m["cells"]["actionClass"]
    print("compiled image[20][14] =", img[20][14], " image[14][20] =", img[14][20])
    print("compiled image[20][15] =", img[20][15], " image[15][20] =", img[15][20])
    print("compiled image[20][16] =", img[20][16], " image[16][20] =", img[16][20])
    print("compiled ac[20][14] =", ac[20][14], " ac[14][20] =", ac[14][20])
    print("compiled ac[20][15] =", ac[20][15], " ac[15][20] =", ac[15][20])
    print("compiled ac[20][16] =", ac[20][16], " ac[16][20] =", ac[16][20])

    j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
    t = j["tiles"]
    print("json tiles[20][14] =", t[20][14], " tiles[14][20] =", t[14][20])
    print("json tiles[20][15] =", t[20][15], " tiles[15][20] =", t[15][20])
    print("json tiles[20][16] =", t[20][16], " tiles[16][20] =", t[16][20])
    print("json tiles[20][13:17] =", t[20][13:17])
    print("json tiles[14][18:22] =", t[14][18:22])
    print("json tiles[15][18:22] =", t[15][18:22])
    print("json tiles[16][18:22] =", t[16][18:22])
    print("json info:", json.dumps(j["info"])[:400])
    print("json action_class[20][13:17] =", j["action_class"][20][13:17])
    print("json action_class[14][18:22] =", j["action_class"][14][18:22])
    print("json action_class[15][18:22] =", j["action_class"][15][18:22])
    print("json action_class[16][18:22] =", j["action_class"][16][18:22])
    print("json keys:", list(j.keys()))


main()
