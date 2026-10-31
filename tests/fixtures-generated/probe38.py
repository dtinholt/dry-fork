"""Inspect the compiled overworld map around the raider encounter cell.

Usage: python3 tests/fixtures-generated/probe38.py [x] [y]
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
    x = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    y = int(sys.argv[2]) if len(sys.argv) > 2 else 41
    d = Path(tempfile.mkdtemp())
    scenario.compile(str(W.SCENARIO), str(d))
    m = maps.load_map(str(d), 0)
    print("size", m["size"])
    print("cell (%d,%d) class=%d action=%d image=%d"
          % (x, y, m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x],
             m["cells"]["image"][y][x]))
    rec = maps.record_at(m, x, y)
    print("record:", json.dumps(rec, default=str)[:800])
    print("mobs:", json.dumps([{k: (v.decode('latin-1') if isinstance(v, bytes) else v)
                                for k, v in mob.items()} for mob in m["mobs"]])[:900])
    print("actions keys:", sorted(m["actions"].keys()))
    for c in ("3", "15"):
        if c in m["actions"]:
            print("class", c, "records:", json.dumps(m["actions"][c], default=str)[:1200])
    # dump the class/action grid rows around y
    for yy in range(max(0, y - 2), min(m["size"], y + 3)):
        print("row %d cls:" % yy, "".join("%X" % v for v in m["cells"]["actionClass"][yy][x - 6:x + 7]))
        print("row %d act:" % yy, "".join("%X" % v for v in m["cells"]["action"][yy][x - 6:x + 7]))


if __name__ == "__main__":
    main()
