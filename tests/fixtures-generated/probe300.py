"""Probe 300: dump the walkthrough script tokens/macros and the scenario start.

Run: python3 tests/fixtures-generated/probe300.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    wt = json.load(open(os.path.join(SCEN, "walkthrough.json"), encoding="utf-8"))
    print("top keys:", sorted(wt.keys()))
    print("seed:", wt.get("seed"), "start:", wt.get("start"))
    script = wt["script"]
    print("script length:", len(script))
    kinds = {}
    tokens = []
    macros = []
    for item in script:
        if isinstance(item, dict):
            macros.append(item)
            for k in item:
                kinds[k] = kinds.get(k, 0) + 1
        else:
            tokens.append(item)
    print("token count:", len(tokens), "macro count:", len(macros))
    print("macro keys:", kinds)
    print("distinct tokens:", sorted(set(tokens)))
    print("first 40 script items:", script[:40])
    print("macros:")
    for m in macros:
        print("   ", json.dumps(m)[:300])
    print("checkpoints:", [c["name"] for c in wt["checkpoints"]])
    # scenario start
    for name in sorted(os.listdir(SCEN)):
        print("scenario file:", name)
    for cand in ("start.json", "scenario.json", "world.json", "lab.json"):
        p = os.path.join(SCEN, cand)
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8"))
            print("=" * 60)
            print(cand, "keys:", sorted(d.keys()) if isinstance(d, dict) else type(d))
            if isinstance(d, dict) and "start" in d:
                print("start:", json.dumps(d["start"])[:400])


if __name__ == "__main__":
    main()
