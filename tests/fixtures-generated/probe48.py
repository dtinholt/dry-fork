"""Probe 48: decode the compiled GAME1 (tests/fixtures-generated/dd) and print
row 20 of the action-class array for map 1, plus run the engine's bump script.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))


def main():
    from wlengine import scenario
    sc = scenario.load(str(ROOT / "tests" / "fixtures-generated" / "dd"))
    m = sc.map(1)
    cls = m["cells"]["actionClass"]
    img = m["cells"]["image"]
    print("map1 size", m["size"])
    for y in (19, 20, 21):
        print("y=%d class %s" % (y, cls[y]))
        print("y=%d image %s" % (y, img[y]))
    print("cells keys:", list(m["cells"].keys()))
    # engine run
    from wlengine import headless
    ev = headless.run(str(ROOT / "tests" / "fixtures-generated" / "dd"),
                      {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    for e in ev:
        print(json.dumps(e))


if __name__ == "__main__":
    main()
