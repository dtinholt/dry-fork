"""probe435: test two hypotheses about the reference log's coordinates against
the frozen scenario JSON maps:

  H0 (unshifted): cell (x, y) is tiles[y][x]
  H1 (shifted):   cell (x, y) is tiles[y][x + 1]

For every move event the target cell must be passable (tile not a wall and
action_class not 11); for every bump event the target cell must be blocked.

Run: python3 tests/fixtures-generated/probe435.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"

WALLS = {15, 16, 19, 24, 25, 26, 27, 28, 29, 30, 31}


def load_maps():
    scen = json.loads((SCEN / "scenario.json").read_text(encoding="utf-8"))
    out = {}
    for loc in scen["locations"]:
        m = json.loads((SCEN / loc["file"]).read_text(encoding="utf-8"))
        out[loc["location"]] = m
    return out


def blocked(m, x, y, shift):
    xx = x + shift
    if xx < 0 or xx >= m["width"] or y < 0 or y >= m["height"]:
        return True
    t = m["tiles"][y][xx]
    ac = m["action_class"][y][xx]
    return t in WALLS or ac == 11


def main():
    maps = load_maps()
    ref = json.loads((SCEN / "walkthrough-reference-log.json").read_text(encoding="utf-8"))
    evs = ref["events"] if isinstance(ref, dict) else ref
    stats = {0: [0, 0], 1: [0, 0]}  # shift -> [ok, bad]
    bad = []
    for e in evs:
        t = e.get("type")
        if t not in ("move", "bump"):
            continue
        loc = e.get("location", 1)
        m = maps.get(loc)
        if m is None:
            continue
        x, y = e["x"], e["y"]
        for shift in (0, 1):
            b = blocked(m, x, y, shift)
            ok = (b if t == "bump" else not b)
            stats[shift][0 if ok else 1] += 1
            if not ok and shift == 0:
                bad.append((t, loc, x, y, m["tiles"][y][x] if 0 <= x < m["width"] else None,
                            m["action_class"][y][x] if 0 <= x < m["width"] else None))
    print("H0 (unshifted): ok=%d bad=%d" % tuple(stats[0]))
    print("H1 (shifted):   ok=%d bad=%d" % tuple(stats[1]))
    print("\nfirst 30 H0 failures:")
    for b in bad[:30]:
        print("  ", b)

    # also: for each location, print the tile rows with a ruler
    for loc, m in sorted(maps.items()):
        print("\n=== location %d %s (%dx%d)" % (loc, m["name"], m["width"], m["height"]))
        for y in range(m["height"]):
            row = "".join("%2d" % t for t in m["tiles"][y])
            print("%2d %s" % (y, row))
        print("x  " + "".join("%2d" % (x % 100) for x in range(m["width"])))


if __name__ == "__main__":
    main()
