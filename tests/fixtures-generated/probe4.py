"""Probe 4: engine internals for M5 combat + Saltwell row 20."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import wl_support as W  # noqa: E402


def main():
    mj = W.load_json(W.SCENARIO / "map1-saltwell.json")
    print("map1 keys:", sorted(mj.keys()))
    print("size:", mj.get("size"))
    print("row20 action_class:", mj["action_class"][20])
    print("row20 tiles:", mj["tiles"][20])
    print("row20 action_value:", mj["action_value"][20])
    print("action_cells:", json.dumps(mj.get("action_cells"))[:2000])
    print("records keys:", sorted(mj["records"].keys()))
    for c, recs in mj["records"].items():
        print(" class", c, "n=", len(recs))
        for r in recs[:6]:
            print("   ", json.dumps(r)[:300])

    print("=" * 70)
    print("map0 records class 3:")
    m0 = W.load_json(W.SCENARIO / "map0-overworld.json")
    for r in m0["records"].get("3", []):
        print("   ", json.dumps(r)[:400])
    print("map0 mobs:", json.dumps(m0["mobs"])[:600])
    print("map0 start:", m0.get("start"), m0.get("info"))
    print("map0 action_class[41][28:34]:", m0["action_class"][41][28:34])
    print("map0 action_value[41][28:34]:", m0["action_value"][41][28:34])
    print("map0 tiles[41][28:34]:", m0["tiles"][41][28:34])


if __name__ == "__main__":
    main()
