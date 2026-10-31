"""probe453: inspect the frozen reference log and scenario.json for the party
start and any bump/look events, and grep the M5/M6 tests for coordinate
expectations.

Run: python3 tests/fixtures-generated/probe453.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")
SCEN = os.path.join(SPEC, "scenario")


def main():
    log = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json"), encoding="utf-8"))
    print("reference log type:", type(log).__name__, "len", len(log))
    kinds = {}
    for e in log:
        kinds[e.get("type")] = kinds.get(e.get("type"), 0) + 1
    print("event kinds:", kinds)
    for i, e in enumerate(log):
        if e.get("type") in ("bump", "look", "move"):
            print(i, json.dumps(e)[:200])
    print()
    print("== first 6 events ==")
    for e in log[:6]:
        print(json.dumps(e)[:400])
    print()
    sc = json.load(open(os.path.join(SCEN, "scenario.json"), encoding="utf-8"))
    print("scenario.json keys:", sorted(sc.keys()))
    print(json.dumps(sc)[:1500])
    print()
    print("== grep tests for coordinates ==")
    for fn in ("test_m5_rules.py", "test_m6_playable.py"):
        txt = open(os.path.join(ROOT, "tests", fn), encoding="utf-8").read().splitlines()
        for i, l in enumerate(txt):
            if re.search(r'"x":|"y":|\(1[0-9], ?[0-9]+\)|\([0-9], ?[0-9]+\)', l):
                print("%s:%d: %s" % (fn, i + 1, l.strip()[:160]))


if __name__ == "__main__":
    main()
