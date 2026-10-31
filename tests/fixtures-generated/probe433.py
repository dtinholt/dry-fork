"""probe433: compile SPEC/scenario, dump LOCATIONS.JSON, decode GAME1 map 1
cells, and run the two failing scripts.

Run: python3 tests/fixtures-generated/probe433.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from wlengine import headless, scenario  # noqa: E402

SCEN = ROOT / "SPEC" / "scenario"
SEED = 20261021


def main():
    d = Path(tempfile.mkdtemp("compiled"))
    scenario.compile(str(SCEN), str(d))
    print("compiled into", d)
    loc = json.loads((d / "LOCATIONS.JSON").read_text())
    print("LOCATIONS.JSON:", json.dumps(loc)[:2000])

    for key, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                        ("look", ["L", "LEFT", {"checkpoint": "a"}])):
        res = headless.run(str(d), {"seed": SEED, "script": script})
        print("\n=== %s === type=%s" % (key, type(res).__name__))
        if isinstance(res, tuple):
            print("tuple len", len(res))
            ev = res[0]
        else:
            ev = res
        for e in ev:
            print("  ", json.dumps(e))


if __name__ == "__main__":
    main()
