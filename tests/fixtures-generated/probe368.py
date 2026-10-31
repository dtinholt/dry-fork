"""Probe: dump the events of the M5 'bump' scenario (LR-15).

Run: python3 tests/fixtures-generated/probe368.py
"""
import inspect
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from wlengine import headless  # noqa: E402

print("headless attrs:", [a for a in dir(headless) if not a.startswith("_")])
try:
    print("run signature:", inspect.signature(headless.run))
except Exception as exc:  # pragma: no cover
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
        print("call ok with params keys:", sorted(params))
        break
    except Exception as exc:
        print("call failed:", type(exc).__name__, exc)

if ev is None:
    sys.exit(1)

if isinstance(ev, tuple):
    ev = ev[0]
print("n events:", len(ev))
for i, e in enumerate(ev):
    print(i, json.dumps(e, sort_keys=True))
