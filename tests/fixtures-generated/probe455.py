"""probe455: compare the frozen reference log's bump/cell_change coordinates
against the frozen scenario JSON under two hypotheses:
  H0: engine cell (x,y) == JSON tiles[y][x]
  H1: engine cell (x,y) == JSON tiles[y][x+1]   (map shifted one column left)

Run: python3 tests/fixtures-generated/probe455.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")

MAPS = {}
for loc in range(4):
    MAPS[loc] = json.load(open(os.path.join(SCEN, "map%d-%s.json" % (loc, ["overworld", "saltwell", "ninemile", "pumphouse"][loc])), encoding="utf-8"))


def cell(loc, x, y):
    m = MAPS[loc]
    t = m["tiles"]
    if not (0 <= y < len(t)) or not (0 <= x < len(t[0])):
        return None
    return {"tile": t[y][x], "class": m["action_class"][y][x], "value": m["action_value"][y][x]}


def main():
    log = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json"), encoding="utf-8"))["events"]
    loc = 1
    print("== reference log bumps / cell_changes with JSON cells ==")
    for e in log:
        if e.get("type") == "map_change":
            loc = e.get("location")
        if e.get("type") in ("bump", "cell_change"):
            x, y = e.get("x"), e.get("y")
            l = e.get("location", loc)
            c0 = cell(l, x, y)
            c1 = cell(l, x + 1, y)
            print("%-11s loc=%s (%2d,%2d) ev=%s | H0=%s | H1=%s" % (
                e["type"], l, x, y,
                json.dumps({k: e[k] for k in ("action_class", "action", "image") if k in e}),
                json.dumps(c0), json.dumps(c1)))
    print()
    print("== JSON map1 rows ==")
    m = MAPS[1]
    for y in (17, 18, 19, 20, 21, 29, 30, 31):
        print("y=%2d tiles:" % y, " ".join("%2d" % v for v in m["tiles"][y]))
        print("      class:", " ".join("%2d" % v for v in m["action_class"][y]))
    print()
    print("== JSON map1 action_cells ==")
    for c in m["action_cells"]:
        print("  ", json.dumps(c))
    print()
    print("== JSON map2 action_cells ==")
    for c in MAPS[2]["action_cells"]:
        print("  ", json.dumps(c))
    print()
    print("== JSON map3 action_cells ==")
    for c in MAPS[3]["action_cells"]:
        print("  ", json.dumps(c))
    print()
    print("== JSON map0 action_cells ==")
    for c in MAPS[0]["action_cells"]:
        print("  ", json.dumps(c))


if __name__ == "__main__":
    main()
