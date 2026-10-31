"""Probe 99: Saltwell (location 1) cells around y=20, x=0..16.

Prints, for the compiled data and for the SPEC-05 map JSON, the action class,
action, image and passability of each cell in row 20, so the cactus cell that
test_bump_is_not_a_step bumps into can be located.
"""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"
sys.path.insert(0, str(ROOT / "src"))


def show_map(m, label):
    print("==== %s ====" % label)
    print("size", m.get("size"), "keys", sorted(m.keys()))
    cells = m["cells"]
    for y in (19, 20, 21):
        row = []
        for x in range(0, 17):
            row.append("%2d/%d/%d%s" % (cells["actionClass"][y][x], cells["action"][y][x],
                                        cells["image"][y][x],
                                        "" if cells.get("passable", [[1] * 64] * 64)[y][x] else "!"))
        print("y=%2d %s" % (y, " ".join(row)))
    print()


def main():
    from wlengine import scenario
    d = Path(tempfile.mkdtemp(prefix="probe99-"))
    scenario.compile(str(SCEN), str(d))
    sc = scenario.load(str(d))
    show_map(sc.map(1), "compiled location 1 (Saltwell)")

    # raw SPEC-05 map json, if present
    for name in sorted(p.name for p in SCEN.glob("*.json")):
        if "map" in name or "salt" in name.lower():
            print("scenario json:", name)
    maps_json = SCEN / "maps.json"
    if maps_json.is_file():
        data = json.loads(maps_json.read_text())
        print("maps.json keys:", sorted(data.keys()) if isinstance(data, dict) else type(data))
        maps = data.get("maps") if isinstance(data, dict) else data
        if isinstance(maps, list):
            for i, m in enumerate(maps):
                print("map %d: %s" % (i, {k: v for k, v in m.items() if k not in ("cells", "tiles", "npcs")}))
                if i == 1:
                    show_map(m, "SPEC-05 map 1")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
