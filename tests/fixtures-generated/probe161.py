"""Probe 161: exact lengths and reprs of the JSON map1 rows, plus the raw JSON
text of the action_class block.

Run: python3 tests/fixtures-generated/probe161.py
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
    for key in ("action_class", "action_value", "tiles"):
        grid = m[key]
        print(key, "rows:", len(grid), "lens:", sorted(set(len(r) for r in grid)))
    print("action_class[20] =", m["action_class"][20])
    print("tiles[20]        =", m["tiles"][20])
    print("action_class[17] =", m["action_class"][17])
    print("action_class[11] =", m["action_class"][11])
    print("action_class[4]  =", m["action_class"][4])

    path = W.SCENARIO / "map1-saltwell.json"
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    i = text.find('"action_class"')
    print("--- raw action_class block ---")
    print(text[i:i + 3000])


if __name__ == "__main__":
    main()
