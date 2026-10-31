"""Probe 46: dump reference-log combat events and the scenario item/mob data."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"


def log_events(a, b):
    d = json.loads((SCEN / "walkthrough-reference-log.json").read_text())
    ev = d["events"] if isinstance(d, dict) else d
    for e in ev:
        if a <= e.get("seq", -1) <= b:
            print(json.dumps(e))


def main():
    print("== raider fight tail (260-340) ==")
    log_events(260, 340)
    print("== pump crawler fight (780-830) ==")
    log_events(780, 830)
    print("== items ==")
    items = json.loads((SCEN / "items.json").read_text())["items"]
    for it in items:
        if it["id"] in (1, 3, 4, 5, 6, 7, 9, 11):
            print(json.dumps(it))
    print("== pumphouse mobs ==")
    m3 = json.loads((SCEN / "map3-pumphouse.json").read_text())
    print(json.dumps(m3["mobs"]))
    print("== overworld mobs ==")
    m0 = json.loads((SCEN / "map0-overworld.json").read_text())
    print(json.dumps(m0["mobs"]))
    print("== skills ==")
    print(json.dumps(json.loads((SCEN / "skills.json").read_text()))[:1500])
    print("== npcs ==")
    print(json.dumps(json.loads((SCEN / "npcs.json").read_text()))[:2000])


if __name__ == "__main__":
    main()
