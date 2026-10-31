"""probe431: inspect SPEC/scenario/map1-saltwell.json conventions/info, and
search the walkthrough + reference log for look/bump events with coordinates.

Run: python3 tests/fixtures-generated/probe431.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"


def main():
    j = json.loads((SCEN / "map1-saltwell.json").read_text(encoding="utf-8"))
    print("conventions:", json.dumps(j.get("conventions"), indent=1))
    print("info:", json.dumps(j.get("info"), indent=1))
    print("location:", j.get("location"), "name:", j.get("name"), "tileset:", j.get("tileset"))
    print("width/height:", j.get("width"), j.get("height"))

    # print rows 19-21 with a ruler
    tiles = j["tiles"]
    for y in (19, 20, 21):
        print("y=%d %s" % (y, "".join("%2d" % t for t in tiles[y])))
    print("x   " + "".join("%2d" % (x % 100) for x in range(32)))

    wt = json.loads((SCEN / "walkthrough.json").read_text(encoding="utf-8"))
    print("\nwalkthrough keys:", sorted(wt.keys()))
    print("start:", wt.get("start"))
    script = wt["script"]
    print("script len:", len(script))
    for i, tok in enumerate(script):
        s = json.dumps(tok)
        if "look" in s.lower() or "L" == tok or "bump" in s.lower():
            print("  tok %d: %s" % (i, s))

    ref = json.loads((SCEN / "walkthrough-reference-log.json").read_text(encoding="utf-8"))
    print("\nreference log type:", type(ref).__name__)
    evs = ref if isinstance(ref, list) else ref.get("events", [])
    print("events:", len(evs))
    kinds = {}
    for e in evs:
        kinds[e.get("type")] = kinds.get(e.get("type"), 0) + 1
    print("kinds:", kinds)
    for e in evs:
        if e.get("type") in ("look", "bump"):
            print("  ", json.dumps(e))


if __name__ == "__main__":
    main()
