import json, os
d = json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "SPEC", "scenario", "map1-saltwell.json")))
ac = d["action_class"]
tl = d["tiles"]
print("as [y][x]:")
for (x, y) in [(15, 20), (15, 19), (15, 12), (14, 12), (14, 11), (14, 8), (13, 8), (9, 8), (2, 20), (3, 20)]:
    print("  ", (x, y), "ac", ac[y][x], "tile", tl[y][x])
print("as [x][y]:")
for (x, y) in [(15, 20), (15, 19), (15, 12), (14, 12), (14, 11), (14, 8), (13, 8), (9, 8), (2, 20), (3, 20)]:
    print("  ", (x, y), "ac", ac[x][y], "tile", tl[x][y])
