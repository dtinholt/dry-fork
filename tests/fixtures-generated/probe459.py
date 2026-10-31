"""Compile the scenario and dump the engine's view of map 1 (Saltwell).

Prints rows 19..21 and 10..12 with x indices, plus the JSON rows for comparison,
so we can see whether the engine's compiled map matches SPEC/scenario JSON.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
sys.path.insert(0, str(ROOT / "src"))

from wlengine import scenario as S  # noqa: E402


def main():
    out = Path(tempfile.mkdtemp(prefix="probe458-"))
    S.compile(str(SPEC / "scenario"), str(out))
    sc = S.load(str(out))
    m = sc.map(1)
    print("map keys:", sorted(m.keys()))
    cells = m.get("cells", {})
    print("cells keys:", sorted(cells.keys()))
    img = cells.get("image")
    cls = cells.get("actionClass")
    act = cells.get("actionValue")
    for y in (19, 20, 21, 10, 11, 12, 30, 31):
        print("engine y=%2d img=%s" % (y, img[y]))
        print("           cls=%s" % (cls[y],))
        if act:
            print("           act=%s" % (act[y],))
    d = json.loads((SPEC / "scenario" / "map1-saltwell.json").read_text())
    for y in (19, 20, 21, 10, 11, 12, 30, 31):
        print("json   y=%2d tiles=%s" % (y, d["tiles"][y]))
        print("           cls=%s" % (d["action_class"][y],))
        print("           val=%s" % (d["action_value"][y],))
    print("info:", m.get("info"))


if __name__ == "__main__":
    main()
