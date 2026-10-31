"""Probe 360: inspect the M5 runner fixture and reproduce the bump failure.

Prints the harness code that builds the data dir and the runner, then runs the
'bump' scenario through headless.run and dumps the events.
"""
import os
import sys
import json
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))


def show(path, start=None, end=None):
    print("=" * 70)
    print("FILE", path)
    print("=" * 70)
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        print("  cannot read:", e)
        return
    if start is not None:
        lines = lines[start - 1:end]
    for i, l in enumerate(lines, 1 if start is None else start):
        print("%4d %s" % (i, l))


show(os.path.join(ROOT, "tests", "conftest.py"))
show(os.path.join(ROOT, "tests", "test_m5_rules.py"), 1, 120)
show(os.path.join(ROOT, "tests", "test_m5_rules.py"), 430, 520)

# find a compiled data dir
cands = []
for pat in ("tests/fixtures-generated/*data", "tests/fixtures-generated/*data/*"):
    cands.extend(glob.glob(os.path.join(ROOT, pat)))
print("=" * 70)
print("DATA DIR CANDIDATES")
for c in cands:
    if os.path.isdir(c):
        print(" ", c, sorted(os.listdir(c))[:12])
