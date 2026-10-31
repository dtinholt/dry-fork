"""Probe 137: inspect the Saltwell map cells around (2..5, 20).

Prints the scenario JSON rows for map1-saltwell.json (action_class / action /
image) around y=20, x=0..8, and the compiled map's cells for the same region,
plus the result of maps.is_passable for each cell.  This is the diagnosis for
test_bump_is_not_a_step: the party must be able to step into (3,20) and bump
(2,20).
"""
import sys
import os
import json
import shutil
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, SRC)
sys.path.insert(0, TESTS)

import wl_support as W  # noqa: E402
from wlengine import maps  # noqa: E402

OUT = os.path.join(HERE, "dump137.txt")
out = open(OUT, "w")


def w(line=""):
    out.write(line + "\n")


def main():
    raw = json.loads((W.SCENARIO / "map1-saltwell.json").read_text())
    w("map1 keys: %s" % sorted(raw.keys()))
    for key in ("action_class", "action", "image", "tiles"):
        if key in raw:
            rows = raw[key]
            w("--- raw %s rows 18..22 ---" % key)
            for y in range(18, 23):
                w("y=%2d %s" % (y, rows[y][:10]))
    w()

    d = Path(tempfile.mkdtemp(prefix="probe137-"))
    fn = W.api("scenario.compile")
    W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)
    m = maps.load_map(str(d), 1)
    w("compiled map size %s" % m["size"])
    for y in range(18, 23):
        w("y=%2d class=%s" % (y, m["cells"]["actionClass"][y][:10]))
        w("y=%2d action=%s" % (y, m["cells"]["action"][y][:10]))
        w("y=%2d image=%s" % (y, m["cells"]["image"][y][:10]))
        w("y=%2d pass=%s" % (y, [maps.is_passable(m, x, y) for x in range(10)]))
    w()
    for x in range(0, 8):
        rec = maps.record_at(m, x, 20)
        w("(x=%d,y=20) rec=%s" % (x, json.dumps(rec, sort_keys=True)))
    w()
    w("hooks: %s" % json.dumps([h for h in W.load_json(W.SCENARIO / "hooks.json").get("hooks", [])
                                if h.get("location") == 1 and h.get("y") == 20], sort_keys=True))
    out.close()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
