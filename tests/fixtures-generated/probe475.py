"""Probe 475: dump map1 action_cells and the reference log events near the
start, to find out whether the cactus is at (2,20) or (3,20) in the frozen
sources, and what the reference log says about the pump."""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def load(name):
    with open(os.path.join(SCEN, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    d = load("map1-saltwell.json")
    print("action_cells:")
    for c in d["action_cells"]:
        print("   ", c)
    print()
    print("records keys:", sorted(d["records"].keys()))
    for k, v in d["records"].items():
        print("  class", k, v)
    print()
    print("action_class rows 11 and 20:")
    for y in (11, 20):
        print("  y=%d %s" % (y, d["action_class"][y]))
        print("  tiles y=%d %s" % (y, d["tiles"][y]))
    print()
    log = load("walkthrough-reference-log.json")["events"]
    print("reference log events mentioning x=2 or x=3 with y=20:")
    for e in log:
        if e.get("y") == 20 and e.get("x") in (2, 3, 4):
            print("   ", e)
    print()
    print("first 30 reference events:")
    for e in log[:30]:
        print("   ", e)
    print()
    wt = load("walkthrough.json")
    print("walkthrough script first 40 tokens:")
    print("   ", wt["script"][:40])


if __name__ == "__main__":
    main()
