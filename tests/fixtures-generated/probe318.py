"""Probe 318: inspect headless.run / Engine API and the first-frame state.

Run: python3 tests/fixtures-generated/probe318.py
"""
from __future__ import annotations

import inspect
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wlengine.headless as H  # noqa: E402

print("=== module attrs ===")
print(sorted(n for n in dir(H) if not n.startswith("__")))

print("=== has first_frame_state:", hasattr(H, "first_frame_state"))

print("=== source of run ===")
try:
    print(inspect.getsource(H.run))
except Exception as e:  # pragma: no cover
    print("ERR", e)

print("=== source of Engine.__init__ ===")
print(inspect.getsource(H.Engine.__init__))

print("=== Engine methods ===")
print([n for n, v in inspect.getmembers(H.Engine, inspect.isfunction)])

print("=== source of Engine.snapshot ===")
print(inspect.getsource(H.Engine.snapshot))

print("=== source of Engine.new_game (if any) ===")
for name in ("new_game", "start", "reset"):
    fn = getattr(H.Engine, name, None)
    if fn is not None:
        print("---", name)
        print(inspect.getsource(fn))

# find the compiled data dir
import wl_support as W  # noqa: E402

print("=== wl_support attrs ===")
print([n for n in dir(W) if not n.startswith("_")])
print("SRC", getattr(W, "SRC", None))
print("SCENARIO", getattr(W, "SCENARIO", None))
print("DATA", getattr(W, "DATA", None))
print("COMPILED", getattr(W, "COMPILED", None))

print("=== source of wl_support.call ===")
print(inspect.getsource(W.call))
print("=== source of wl_support.expect_error ===")
print(inspect.getsource(W.expect_error))
