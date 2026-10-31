"""probe336: print the frozen map1-saltwell rows/columns needed to test the
"transposed reading" hypothesis against the M5 pump and transition tests.

Prints orig row 15 (tiles and action classes), the transposed column x=15, and
the specific cells the pump test (15,11) and the transition test (15,31) name,
under both the normal and the transposed reading.
Read-only.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC", "scenario")


def main():
    m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
    tiles, ac = m["tiles"], m["action_class"]
    print("orig row 15 tiles:", tiles[15])
    print("orig row 15 ac   :", ac[15])
    print("orig row 11 tiles:", tiles[11])
    print("orig row 11 ac   :", ac[11])
    print("orig row 31 tiles:", tiles[31])
    print("orig row 31 ac   :", ac[31])
    print()
    print("transposed column x=15 (E(15,y) = orig(y,15) = orig[15][y]):")
    for y in range(32):
        print("   E(15,%2d) = orig(%2d,15) tile=%2d image=%2d ac=%d" % (y, y, tiles[15][y], tiles[15][y] + 10, ac[15][y]))
    print()
    print("named cells, normal vs transposed:")
    for (x, y) in [(15, 11), (15, 31), (16, 31), (3, 20), (2, 20), (14, 20), (15, 20)]:
        print("   (%2d,%2d) normal tile=%2d image=%2d ac=%d | transposed tile=%2d image=%2d ac=%d"
              % (x, y, tiles[y][x], tiles[y][x] + 10, ac[y][x], tiles[x][y], tiles[x][y] + 10, ac[x][y]))


if __name__ == "__main__":
    main()
