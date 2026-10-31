"""Probe 15: dump the combat-related engine source and run the raider opening.

Run:  python3 tests/fixtures-generated/probe15.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))


def show(path, a, b):
    p = os.path.join(ROOT, path)
    print("=" * 70)
    print("%s lines %d-%d" % (path, a, b))
    print("=" * 70)
    with open(p) as f:
        for i, line in enumerate(f, 1):
            if a <= i <= b:
                print("%4d| %s" % (i, line.rstrip("\n")))


def grep(path, pat):
    p = os.path.join(ROOT, path)
    print("=" * 70)
    print("grep %r in %s" % (pat, path))
    print("=" * 70)
    with open(p) as f:
        for i, line in enumerate(f, 1):
            if pat in line:
                print("%4d| %s" % (i, line.rstrip("\n")))


def run_opening(seed):
    """Run the walkthrough prefix up to CP3 and print the combat events."""
    import wl_support as W
    walkthrough = W.load_json(W.SCENARIO / "walkthrough.json")
    print("=" * 70)
    print("walkthrough keys:", list(walkthrough)[:20])
    print("=" * 70)
    steps = walkthrough.get("steps") or walkthrough.get("walkthrough") or []
    print("n steps:", len(steps))
    for i, s in enumerate(steps[:80]):
        print(i, json.dumps(s)[:160])


def main():
    show("src/wlengine/headless.py", 440, 500)
    show("src/wlengine/headless.py", 940, 1000)
    show("src/wlengine/rules.py", 1, 330)
    grep("src/wlengine/headless.py", "def ")
    grep("src/wlengine/scenario.py", "def ")
    run_opening(1)


if __name__ == "__main__":
    main()
