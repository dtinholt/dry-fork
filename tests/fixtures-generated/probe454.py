"""probe454: inspect the frozen reference log structure and scenario.json.

Run: python3 tests/fixtures-generated/probe454.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")
SCEN = os.path.join(SPEC, "scenario")


def main():
    log = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json"), encoding="utf-8"))
    print("keys:", sorted(log.keys()))
    for k, v in log.items():
        print(" ", k, type(v).__name__, (len(v) if hasattr(v, "__len__") else ""))
    ev = log.get("events") or log.get("log") or []
    kinds = {}
    for e in ev:
        kinds[e.get("type")] = kinds.get(e.get("type"), 0) + 1
    print("event kinds:", kinds)
    for i, e in enumerate(ev):
        if e.get("type") in ("bump", "look"):
            print(i, json.dumps(e)[:200])
    print("first 4:", json.dumps(ev[:4])[:600])
    print()
    sc = json.load(open(os.path.join(SCEN, "scenario.json"), encoding="utf-8"))
    print("scenario.json:", json.dumps(sc)[:1200])
    print()
    print("== grep tests for coordinates ==")
    for fn in ("test_m5_rules.py", "test_m6_playable.py"):
        txt = open(os.path.join(ROOT, "tests", fn), encoding="utf-8").read().splitlines()
        for i, l in enumerate(txt):
            if re.search(r'"x":|"y":|\(1[0-9], ?[0-9]+\)|\([0-9], ?[0-9]+\)', l):
                print("%s:%d: %s" % (fn, i + 1, l.strip()[:170]))


if __name__ == "__main__":
    main()
