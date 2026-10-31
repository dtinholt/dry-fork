"""Probe 157: dump the walkthrough script head and the reference log's first
events (moves/bumps) to see where the cactus bump really is.

Run: python3 tests/fixtures-generated/probe157.py
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

    wt = W.load_json(W.SCENARIO / "walkthrough.json")
    print("walkthrough keys:", list(wt))
    script = wt["script"]
    print("script len", len(script))
    for i, item in enumerate(script[:80]):
        print("%3d %s" % (i, json.dumps(item)))

    ref = W.load_json(W.REFERENCE_LOG)["events"]
    print("--- reference events 0..80 ---")
    for e in ref[:80]:
        print(json.dumps(e, sort_keys=True))


if __name__ == "__main__":
    main()
