"""Probe 154: dump map1-saltwell.json structure and the reference log bumps.

Run: python3 tests/fixtures-generated/probe154.py
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
    print("top keys:", list(m))
    for k, v in m.items():
        if isinstance(v, list):
            print("  %s: list len %d" % (k, len(v)))
        elif isinstance(v, dict):
            print("  %s: dict keys %s" % (k, list(v)[:20]))
        else:
            print("  %s: %r" % (k, v))
    cells = m.get("cells") or {}
    print("cells keys:", list(cells))
    for key, grid in cells.items():
        if isinstance(grid, list) and grid and isinstance(grid[0], list):
            print("  %s row20:" % key, grid[20][:10])
    # records
    for key in ("actions", "records", "actionRecords"):
        if key in m:
            print("---", key)
            for r in m[key]:
                if r.get("y") == 20 and r.get("x", 99) < 8:
                    print("   ", json.dumps(r, sort_keys=True))
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
