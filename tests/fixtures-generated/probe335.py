"""probe335: locate the pump head (tile 23), the transitions (class 10) and the
cells the M5 tests name, in the frozen map1-saltwell.json.

Prints:
  * every cell with tile 23 (pump head) and its action class;
  * every cell with action class 10 (transition) and its tile;
  * the map records (action records) with their class and coordinates, so the
    pump hook and the transition destinations can be read off;
  * the tiles/classes of (15,11), (16,11), (15,31), (16,31), (15,12), (14,20).
Read-only.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC", "scenario")


def main():
    m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
    tiles, ac, av = m["tiles"], m["action_class"], m["action_value"]
    n = len(tiles)
    print("cells with tile 23 (pump head):")
    for y in range(n):
        for x in range(n):
            if tiles[y][x] == 23:
                print("   (x=%d,y=%d) ac=%d av=%d" % (x, y, ac[y][x], av[y][x]))
    print("cells with action class 10 (transition):")
    for y in range(n):
        for x in range(n):
            if ac[y][x] == 10:
                print("   (x=%d,y=%d) tile=%d av=%d" % (x, y, tiles[y][x], av[y][x]))
    print("cells with action class 11 (blocked):")
    for y in range(n):
        for x in range(n):
            if ac[y][x] == 11:
                print("   (x=%d,y=%d) tile=%d av=%d" % (x, y, tiles[y][x], av[y][x]))
    print()
    print("named cells:")
    for (x, y) in [(15, 11), (16, 11), (15, 12), (16, 12), (15, 31), (16, 31), (14, 20), (15, 20), (2, 20), (3, 20)]:
        print("   (x=%d,y=%d) tile=%d image=%d ac=%d av=%d" % (x, y, tiles[y][x], tiles[y][x] + 10, ac[y][x], av[y][x]))
    print()
    print("records:")
    for r in m.get("records", []):
        print("   ", json.dumps(r)[:200])
    print()
    print("action_cells:")
    print("   ", json.dumps(m.get("action_cells"))[:1000])


if __name__ == "__main__":
    main()
