"""Probe 24: compile the scenario fresh, dump map1 row 20, and run the bump
script to see the actual events."""
from __future__ import annotations

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wlengine.scenario as S  # noqa: E402
import wlengine.headless as H  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    d = tempfile.mkdtemp(prefix="probe24-")
    S.compile(SCEN, d)
    sc = S.load(d)
    m = sc.map(1)
    print("compiled map1 y=20 cls", m["cells"]["actionClass"][20][:8])
    print("compiled map1 y=20 act", m["cells"]["action"][20][:8])
    print("compiled map1 y=20 tiles", m["cells"].get("tiles", [None] * 32)[20][:8]
          if "tiles" in m["cells"] else "no tiles key")
    ev = H.run(d, {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    for e in ev:
        if e.get("type") in ("move", "bump", "blocked", "checkpoint", "input"):
            print(json.dumps(e)[:200])


if __name__ == "__main__":
    main()
