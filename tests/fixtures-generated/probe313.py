"""Probe 313: reference log structure and repeat_until semantics.

Run: python3 tests/fixtures-generated/probe313.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SCEN = os.path.join(PROJ, "SPEC", "scenario")


def main():
    ref = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json")))
    print("type:", type(ref))
    if isinstance(ref, dict):
        print("keys:", list(ref.keys()))
        for k, v in ref.items():
            print("  ", k, type(v), (len(v) if hasattr(v, "__len__") else ""))
        ev = ref.get("events") or ref.get("log") or []
    else:
        ev = ref
    print("events:", len(ev))
    idxs = [i for i, e in enumerate(ev) if e.get("type") == "input" and e.get("key") == "A"]
    print("A inputs at:", idxs)
    for i in range(max(0, (idxs[0] if idxs else 0) - 2), min(len(ev), (idxs[0] if idxs else 0) + 8)):
        print(i, json.dumps(ev[i])[:200])
    print("--- types histogram ---")
    from collections import Counter
    print(Counter(e.get("type") for e in ev))
    print("--- look events ---")
    for i, e in enumerate(ev):
        if e.get("type") == "look":
            print(i, json.dumps(e))
    print("--- first 6 ---")
    for i in range(6):
        print(i, json.dumps(ev[i])[:200])


main()
