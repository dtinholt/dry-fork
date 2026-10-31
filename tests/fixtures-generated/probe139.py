"""Probe 139: discover the test support API and dump the bump-test map cells.

Run from the project root:  python3 tests/fixtures-generated/probe139.py
"""
import os
import sys
import json
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TESTS = os.path.join(ROOT, "tests")
for p in (ROOT, os.path.join(ROOT, "src"), TESTS, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

print("== modules in tests dir ==")
for fn in sorted(os.listdir(TESTS)):
    print("  ", fn)

print("== try importing support modules ==")
SUP = None
for name in ("wl_support", "conftest", "support", "wl_test_support"):
    try:
        mod = __import__(name)
        print("imported", name, "->", mod.__file__)
        print("   names:", [a for a in dir(mod) if not a.startswith("_")])
        if SUP is None:
            SUP = mod
    except Exception as exc:
        print("fail", name, repr(exc))

print("== try importing test module ==")
try:
    tm = __import__("test_m5_rules")
    print("imported test_m5_rules", tm.__file__)
    print("   names:", [a for a in dir(tm) if not a.startswith("_")][:80])
except Exception:
    traceback.print_exc()

print("== scenario dirs ==")
for cand in ("scenario", "SPEC/scenario", "tests/scenario", "fixtures/scenario"):
    p = os.path.join(ROOT, cand)
    if os.path.isdir(p):
        print("  ", cand, sorted(os.listdir(p))[:40])

print("== generated dirs ==")
for cand in ("tests/fixtures-generated/dd", "tests/fixtures-generated/dd117"):
    p = os.path.join(ROOT, cand)
    if os.path.isdir(p):
        print("  ", cand, sorted(os.listdir(p)))
