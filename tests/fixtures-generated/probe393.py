"""Probe 393: find the runner fixture used by tests/test_m5_rules.py and run the
failing 'bump' scenario, dumping the full event stream plus engine state.

Run: python3 tests/fixtures-generated/probe393.py
"""
import inspect
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402


def show(name):
    fn = getattr(W, name, None)
    if fn is None:
        print("!! wl_support has no", name)
        return
    try:
        print("=" * 70)
        print("### wl_support.%s" % name)
        print("=" * 70)
        print(inspect.getsource(fn))
    except Exception as e:  # noqa: BLE001
        print("!! cannot get source of", name, e)


def main():
    print("wl_support names with 'run':", [n for n in dir(W) if "run" in n.lower()])
    print("wl_support names with 'seed':", [n for n in dir(W) if "seed" in n.lower()])
    print("wl_support names with 'engine':", [n for n in dir(W) if "engine" in n.lower()])
    for n in ("SEED", "SEED0", "run_scenario", "make_runner", "Runner", "runner"):
        if hasattr(W, n):
            print(n, "=", getattr(W, n))
    # conftest
    for cand in ("conftest.py",):
        p = os.path.join(ROOT, "tests", cand)
        if os.path.exists(p):
            print("=" * 70)
            print("### tests/%s" % cand)
            print("=" * 70)
            print(open(p).read())
    # find runner fixture in test file
    tf = os.path.join(ROOT, "tests", "test_m5_rules.py")
    src = open(tf).read()
    i = src.find("def runner")
    print("=" * 70)
    print("### test_m5_rules.py runner fixture")
    print("=" * 70)
    print(src[max(0, i - 200): i + 2000])


if __name__ == "__main__":
    main()
