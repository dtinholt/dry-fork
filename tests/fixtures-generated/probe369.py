"""Probe 369: dump the M5 'bump' scenario events and the movement code.

Run: python3 tests/fixtures-generated/probe369.py
"""
import inspect
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from wlengine import headless  # noqa: E402

print("=== headless module attrs ===")
print([a for a in dir(headless) if not a.startswith("_")])
try:
    print("run signature:", inspect.signature(headless.run))
except Exception as exc:
    print("no run:", exc)

SEED = 12345
script = ["LEFT"] * 13 + [{"checkpoint": "a"}]

ev = None
for params in (
    {"seed": SEED, "script": script},
    {"seed": SEED, "script": script, "scenario": "bump"},
):
    try:
        out = headless.run("bump", params)
        ev = out
        print("=== call ok with params keys:", sorted(params))
        break
    except Exception as exc:
        print("call failed:", type(exc).__name__, exc)

if ev is not None:
    if isinstance(ev, tuple):
        ev = ev[0]
    print("=== n events:", len(ev))
    for i, e in enumerate(ev):
        print(i, json.dumps(e, sort_keys=True))
else:
    print("=== no events produced")

print()
print("=== grep movement / step code in headless.py ===")
src = open(os.path.join(ROOT, "src", "wlengine", "headless.py")).read()
lines = src.splitlines()
pat = re.compile(r"step|bump|move|LEFT|blocked|class 11|action_class")
for i, ln in enumerate(lines, 1):
    if pat.search(ln):
        print("%4d %s" % (i, ln))

print()
print("=== grep movement / step code in rules.py ===")
src2 = open(os.path.join(ROOT, "src", "wlengine", "rules.py")).read()
for i, ln in enumerate(src2.splitlines(), 1):
    if pat.search(ln):
        print("%4d %s" % (i, ln))

print()
print("=== grep movement / step code in scenario.py ===")
src3 = open(os.path.join(ROOT, "src", "wlengine", "scenario.py")).read()
for i, ln in enumerate(src3.splitlines(), 1):
    if pat.search(ln):
        print("%4d %s" % (i, ln))
