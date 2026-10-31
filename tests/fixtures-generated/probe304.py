"""Probe 304: map info keys, location names, look reference events.

Run: python3 tests/fixtures-generated/probe304.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    m = json.load(open(os.path.join(SCEN, "map1-saltwell.json"), encoding="utf-8"))
    print("map1 keys:", sorted(m.keys()))
    print("info:", json.dumps(m["info"])[:800])
    print("tiles[20]:", m["tiles"][20])
    print("tiles[20][14]:", m["tiles"][20][14], "tiles[20][15]:", m["tiles"][20][15])
    print("action_class[20][14]:", m["action_class"][20][14])
    print("image? keys:", [k for k in m if "image" in k])
    sc = json.load(open(os.path.join(SCEN, "scenario.json"), encoding="utf-8"))
    print("scenario locations:", json.dumps(sc["locations"])[:1200])
    print("scenario scenario:", json.dumps(sc["scenario"])[:800])
    print("scenario content keys:", sorted(sc["content"].keys()) if isinstance(sc["content"], dict) else type(sc["content"]))
    # reference log look events
    ref = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json"), encoding="utf-8"))
    evs = ref["events"]
    print("ref events:", len(evs))
    looks = [e for e in evs if e.get("type") == "look"]
    print("look events:", looks[:5])
    # any location_name in checkpoints?
    for e in evs:
        if e.get("type") == "checkpoint":
            print("checkpoint", e["name"], "state keys:", sorted(e["state"].keys()))
            break
    # strings.json / labstr tables
    st = json.load(open(os.path.join(SCEN, "strings.json"), encoding="utf-8"))
    print("strings.json keys:", sorted(st.keys()) if isinstance(st, dict) else type(st))
    print(json.dumps(st)[:1500])


if __name__ == "__main__":
    main()
