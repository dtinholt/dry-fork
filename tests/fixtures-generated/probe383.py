"""Probe 383: compare the engine's compiled Saltwell map cells with the JSON.

Dumps cells.image / cells.actionClass for rows 19..21 and columns 0..8, and
checks both index conventions against SPEC/scenario/map1-saltwell.json.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wlengine.scenario as S  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    d = tempfile.mkdtemp(prefix="probe383-")
    S.compile(SCEN, d)
    sc = S.load(d)
    m = sc.map(1)
    cells = m["cells"]
    img = cells["image"]
    cls = cells["actionClass"]
    j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
    jt, jc = j["tiles"], j["action_class"]
    for y in (19, 20, 21):
        print("y=%d engine img %s" % (y, img[y][:8]))
        print("     engine cls %s" % (cls[y][:8],))
        print("     json   img %s" % ([t + 10 for t in jt[y][:8]],))
        print("     json   cls %s" % (jc[y][:8],))
    # full comparison
    same = all(img[y][x] == jt[y][x] + 10 for y in range(32) for x in range(32))
    trans = all(img[y][x] == jt[x][y] + 10 for y in range(32) for x in range(32))
    print("engine image == json[y][x]+10 :", same)
    print("engine image == json[x][y]+10 :", trans)
    samec = all(cls[y][x] == jc[y][x] for y in range(32) for x in range(32))
    transc = all(cls[y][x] == jc[x][y] for y in range(32) for x in range(32))
    print("engine class == json[y][x] :", samec)
    print("engine class == json[x][y] :", transc)


main()
