"""Probe 21: dump the engine's encounter/combat code and the opening events.

Run:  python3 tests/fixtures-generated/probe21.py
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


def main():
    needle = sys.argv[1] if len(sys.argv) > 1 else "encounter"
    dump_source(H, needle)
    dump_source(R, needle)


if __name__ == "__main__":
    main()
