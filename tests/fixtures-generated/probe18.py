"""Probe 18: bump test + compiled map cell dump.

Run:  python3 tests/fixtures-generated/probe18.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402


def main():
    d = tempfile.mkdtemp(prefix="probe18-")
    import wlengine.scenario as S
    S.compile(str(W.SCENARIO), d)
    import wlengine.headless as H
    ev = H.run(d, {"script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, 20261021)
    for e in ev:
        if e.get("type") in ("input", "bump", "checkpoint", "map_change"):
            print(json.dumps(e)[:200])
    print("=" * 70)
    import wlengine.maps as M
    m = M.load_map(d, 1)
    print("size", m["size"])
    for y in range(18, 23):
        print("y=%d cls=%s" % (y, m["cells"]["actionClass"][y]))
        print("     act=%s" % (m["cells"]["action"][y],))
        print("     img=%s" % (m["cells"]["image"][y],))
    print("=" * 70)
    src = json.load(open(os.path.join(str(W.SCENARIO), "map1-saltwell.json")))
    for y in range(18, 23):
        print("json y=%d cls=%s" % (y, src["action_class"][y]))
        print("     act=%s" % (src["action_value"][y],))
        print("     til=%s" % (src["tiles"][y],))


if __name__ == "__main__":
    main()
