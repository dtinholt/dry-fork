"""Probe 171: fresh compile, map1 class-11 cells, JSON class-11 cells, bump run.

Settles whether the action_class arrays are [y][x] or [x][y] and where the
cactus really is.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wlengine.headless as H  # noqa: E402
import wlengine.maps as M  # noqa: E402
import wlengine.scenario as S  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")
SEED = 20261021


def main():
    out = tempfile.mkdtemp(prefix="probe171-")
    S.compile(SCEN, out)
    print("compiled to", out)

    m = M.load_map(out, 1)
    ac = m["cells"]["actionClass"]
    print("=== engine map1 class-11 cells (y,x) ===")
    cells = [(y, x) for y in range(32) for x in range(32) if ac[y][x] == 11]
    print(cells)

    j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
    jac = j["action_class"]
    print("=== JSON class-11 cells (i,j) ===")
    jcells = [(i, k) for i in range(32) for k in range(32) if jac[i][k] == 11]
    print(jcells)
    print("=== JSON class-11 as (x=k, y=i) ===")
    print(sorted((k, i) for i, k in jcells))
    print("=== engine class-11 as (x, y) ===")
    print(sorted((x, y) for y, x in cells))

    print("=== engine row 20 x=0..6 ===")
    print([(x, ac[20][x]) for x in range(7)])
    print("=== JSON row 20 x=0..6 (jac[20][x]) ===")
    print([(x, jac[20][x]) for x in range(7)])
    print("=== JSON jac[2][20], jac[20][2], jac[11][15], jac[15][11] ===")
    print(jac[2][20], jac[20][2], jac[11][15], jac[15][11])

    ev = H.run(out, {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    print("=== bump run events ===")
    for e in ev:
        if e.get("type") in ("move", "bump", "checkpoint"):
            print(json.dumps(e, sort_keys=True)[:200])


main()
