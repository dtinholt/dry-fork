"""Probe 155: dump map1 records / action_cells / action_class rows and the
reference log bumps.

Run: python3 tests/fixtures-generated/probe155.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    import wl_support as W

    m = W.load_json(W.SCENARIO / "map1-saltwell.json")
    print("records:")
    for cls, recs in m["records"].items():
        print(" class", cls)
        for i, r in enumerate(recs):
            print("   slot %d: %s" % (i + 1, json.dumps(r, sort_keys=True)))
    print("action_class row 20:", m["action_class"][20][:10])
    print("action_value row 20:", m["action_value"][20][:10])
    print("tiles row 20:", m["tiles"][20][:10])
    print("action_cells:")
    for c in m["action_cells"]:
        print("   ", json.dumps(c, sort_keys=True))
    print("--- reference bumps ---")
    ref = W.load_json(W.REFERENCE_LOG)["events"]
    for e in ref:
        if e.get("type") == "bump":
            print(json.dumps(e, sort_keys=True))
    print("--- reference moves loc1 y20 ---")
    for e in ref:
        if e.get("type") == "move" and e.get("location") == 1 and e.get("y") == 20:
            print(json.dumps(e, sort_keys=True))


if __name__ == "__main__":
    main()
