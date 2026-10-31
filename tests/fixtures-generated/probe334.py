"""probe334: find which reading of the Saltwell map puts image 28 (street,
tile 18) at (14,20), and image 21 (cactus) / class 11 at (2,20).

Prints:
  * tiles[y][x] and tiles[x][y] for the cells the M5 bump test and the M6 look
    test name;
  * the whole transposed column tiles[x][20] for x = 0..31;
  * the whole row tiles[20][x] for x = 0..31;
  * every cell of the map whose tile is 18 (street) or 11 (cactus), with its
    action class, so the two candidate readings can be compared directly.
Read-only.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC", "scenario")


def main():
    m = json.load(open(os.path.join(SPEC, "map1-saltwell.json")))
    tiles, ac = m["tiles"], m["action_class"]
    n = len(tiles)
    print("size", n)
    print("row 20  tiles[20][x] x=0..31:", tiles[20])
    print("row 20  ac[20][x]    x=0..31:", ac[20])
    print("col 20  tiles[x][20] x=0..31:", [tiles[x][20] for x in range(n)])
    print("col 20  ac[x][20]    x=0..31:", [ac[x][20] for x in range(n)])
    print()
    print("cells with tile 18 (street, image 28):")
    for y in range(n):
        for x in range(n):
            if tiles[y][x] == 18:
                print("   (x=%d,y=%d) ac=%d" % (x, y, ac[y][x]))
    print("cells with tile 11 (cactus, image 21):")
    for y in range(n):
        for x in range(n):
            if tiles[y][x] == 11:
                print("   (x=%d,y=%d) ac=%d" % (x, y, ac[y][x]))
    print()
    print("transposed cells with tile 18:")
    for y in range(n):
        for x in range(n):
            if tiles[x][y] == 18:
                print("   (x=%d,y=%d) ac[x][y]=%d" % (x, y, ac[x][y]))
    print("transposed cells with tile 11:")
    for y in range(n):
        for x in range(n):
            if tiles[x][y] == 11:
                print("   (x=%d,y=%d) ac[x][y]=%d" % (x, y, ac[x][y]))


if __name__ == "__main__":
    main()
