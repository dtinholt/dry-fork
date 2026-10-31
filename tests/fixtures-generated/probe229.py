"""Probe 229: render the JSON tiles/action_class grid of map1 and compare with
the SPEC-05 art."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "dump229.txt"
SC = ROOT / "SPEC" / "scenario"

m = json.loads((SC / "map1-saltwell.json").read_text())
tiles = m["tiles"]
ac = m["action_class"]
with OUT.open("w") as f:
    f.write("tiles[11]=%s\n" % tiles[11])
    f.write("tiles[15]=%s\n" % tiles[15])
    f.write("ac[11]=%s\n" % ac[11])
    f.write("ac[15]=%s\n" % ac[15])
    f.write("\n--- tiles grid (row-major, index [y][x]) ---\n")
    for y in range(32):
        f.write("%2d %s\n" % (y, " ".join("%2d" % v for v in tiles[y])))
    f.write("\n--- action_class grid ---\n")
    for y in range(32):
        f.write("%2d %s\n" % (y, " ".join("%2d" % v for v in ac[y])))
    f.write("\n--- action_value grid ---\n")
    av = m["action_value"]
    for y in range(32):
        f.write("%2d %s\n" % (y, " ".join("%2d" % v for v in av[y])))
print("wrote", OUT)
