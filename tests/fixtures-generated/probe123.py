"""Probe 123: reference-log cell_change analysis.

Prints every cell_change in the reference log, plus the class/action of the
cell in the scenario JSON, so we can tell when a tail of 255 still emits one.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    log = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json")))
    ev = log["events"] if isinstance(log, dict) else log
    maps = {}
    for i in range(4):
        maps[i] = json.load(open(os.path.join(SCEN, "map%d-%s.json" % (
            i, ["overworld", "saltwell", "ninemile", "pumphouse"][i]))))
    for e in ev:
        if e.get("type") == "cell_change":
            loc, x, y = e["location"], e["x"], e["y"]
            j = maps[loc]
            cell = None
            for c in j["action_cells"]:
                if c["x"] == x and c["y"] == y:
                    cell = c
            print("seq %4d loc %d (%2d,%2d) -> class %2d action %2d image %3d | json %s"
                  % (e["seq"], loc, x, y, e["action_class"], e["action"], e["image"],
                     cell))
    print("--- moves onto class-1 cells with new_class 255")
    for e in ev:
        if e.get("type") == "move":
            loc, x, y = e["location"], e["x"], e["y"]
            j = maps[loc]
            for c in j["action_cells"]:
                if c["x"] == x and c["y"] == y and c["class"] == 1:
                    recs = j["records"]["1"]
                    rec = recs[c["action"] - 1]
                    print("seq %4d move loc %d (%2d,%2d) class1 action %d new_class %s"
                          % (e["seq"], loc, x, y, c["action"], rec.get("new_class")))


if __name__ == "__main__":
    main()
