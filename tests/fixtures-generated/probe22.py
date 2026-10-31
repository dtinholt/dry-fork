"""Probe 22: dump engine encounter/combat code and opening events.

Usage:
  python3 tests/fixtures-generated/probe22.py src encounter
  python3 tests/fixtures-generated/probe22.py run
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
import wlengine.rules as R  # noqa: E402


def dump_source(mod, needle):
    print("=" * 70)
    print("MODULE", mod.__name__, "needle", needle)
    print("=" * 70)
    for name, obj in vars(mod).items():
        if not (inspect.isfunction(obj) or inspect.isclass(obj)):
            continue
        try:
            src = inspect.getsource(obj)
        except Exception:
            continue
        if needle in src or needle in name:
            print(src)
            print("-" * 70)


def run_opening(seed):
    import wl_support as W
    walkthrough = W.load_json(W.SCENARIO / "walkthrough.json")
    script = W.opening_script(walkthrough)
    runner = H.Runner()
    ev, _ = runner.run("opening", {"seed": seed, "script": script}, seed)
    for e in ev:
        print(json.dumps(e, default=str))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "src"
    if mode == "src":
        needle = sys.argv[2] if len(sys.argv) > 2 else "encounter"
        dump_source(H, needle)
        dump_source(R, needle)
    elif mode == "run":
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261021
        run_opening(seed)


if __name__ == "__main__":
    main()
