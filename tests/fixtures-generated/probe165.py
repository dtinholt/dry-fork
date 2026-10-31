"""Probe 165: tiles.json, map2 rows 20/21, reference events around seq 595-610,
and the SPEC-05 Ninemile art.

Run: python3 tests/fixtures-generated/probe165.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
SPEC = os.path.join(ROOT, "SPEC")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    import wl_support as W

    tiles = W.load_json(W.SCENARIO / "tiles.json")
    print("tiles.json keys:", list(tiles))
    for t in tiles.get("tiles", []):
        print("  ", json.dumps(t, sort_keys=True))

    m2 = W.load_json(W.SCENARIO / "map2-ninemile.json")
    print("map2 action_class[21]:", m2["action_class"][21])
    print("map2 tiles[21]:", m2["tiles"][21])
    print("map2 action_value[21]:", m2["action_value"][21])
    print("map2 action_class[20]:", m2["action_class"][20])
    print("map2 records:", json.dumps(m2["records"], sort_keys=True)[:1500])
    print("map2 action_cells:", json.dumps(m2["action_cells"], sort_keys=True)[:2000])

    ref = W.load_json(W.REFERENCE_LOG)["events"]
    print("--- reference events 590..615 ---")
    for e in ref[590:615]:
        print(json.dumps(e, sort_keys=True))

    # SPEC-05 Ninemile art
    with open(os.path.join(SPEC, "SPEC-05-scenario.md"), encoding="utf-8") as fh:
        lines = fh.readlines()
    start = end = None
    for i, ln in enumerate(lines):
        if ln.startswith("### 5.3 Ninemile"):
            start = i
        elif start is not None and ln.startswith("### 5.4"):
            end = i
            break
    for i in range(start, min(end, start + 60)):
        sys.stdout.write("%4d| %s" % (i + 1, lines[i]))


if __name__ == "__main__":
    main()
