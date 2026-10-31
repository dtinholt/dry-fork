"""Probe 395: locate the 'bump' scenario definition and run it through the
engine's headless.run, dumping the event stream.

Run: python3 tests/fixtures-generated/probe395.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SCEN = os.path.join(ROOT, "SPEC", "scenario")
print("scenario files:", sorted(os.listdir(SCEN)))

for fn in sorted(os.listdir(SCEN)):
    if not fn.endswith(".json"):
        continue
    p = os.path.join(SCEN, fn)
    try:
        d = json.load(open(p))
    except Exception as e:  # noqa: BLE001
        print("!!", fn, e)
        continue
    txt = json.dumps(d)
    if '"bump"' in txt:
        print("=" * 70)
        print("### %s mentions 'bump'" % fn)
        print("=" * 70)
        if isinstance(d, dict):
            for k, v in d.items():
                if "bump" in json.dumps(v):
                    print("key", k, "->", json.dumps(v)[:2000])
        else:
            print(txt[:2000])
