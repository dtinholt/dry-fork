"""Check the compiled Saltwell map around row 20 and the ref combat opening.

Usage: python3 tests/fixtures-generated/probe41.py
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402
from wlengine import maps, scenario  # noqa: E402


def main():
    d = Path(tempfile.mkdtemp())
    scenario.compile(str(W.SCENARIO), str(d))
    m = maps.load_map(str(d), 1)
    print("compiled Saltwell row 20:")
    print("  cls:", "".join("%X" % v for v in m["cells"]["actionClass"][20]))
    print("  img:", " ".join("%d" % v for v in m["cells"]["image"][20]))
    for x in (1, 2, 3, 4):
        print("  (%d,20) cls=%d img=%d passable=%s"
              % (x, m["cells"]["actionClass"][20][x], m["cells"]["image"][20][x],
                 maps.is_passable(m, x, 20)))
    print("mobs:", [mo["name"] for mo in m["mobs"]])
    print("strings:", [s for s in m["strings"]][:10])
    m0 = maps.load_map(str(d), 0)
    print("overworld strings:", [s for s in m0["strings"]][:12])
    print("overworld mobs:", [(mo["name"], mo["combatRating"]) for mo in m0["mobs"]])
    m3 = maps.load_map(str(d), 3)
    print("pumphouse mobs:", [(mo["name"], mo["combatRating"]) for mo in m3["mobs"]])
    import wl_combat_ref as CR
    ref = CR.opening(20261021)
    print("REF encounter:", json.dumps(ref["encounter"]))
    print("REF check:", json.dumps(ref["check"]))
    print("REF surprised:", ref["surprised"])
    print("REF round0:", json.dumps(ref["round0"]))
    print("REF round1:", json.dumps(ref["round1"]))


if __name__ == "__main__":
    main()
