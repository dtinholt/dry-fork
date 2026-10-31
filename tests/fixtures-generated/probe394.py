"""Probe 394: dump the rest of conftest Runner.run and the test_m5_rules runner
fixture + scenario definitions ('bump', 'pump', 'rest').

Run: python3 tests/fixtures-generated/probe394.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

cf = os.path.join(ROOT, "tests", "conftest.py")
src = open(cf).read()
i = src.find("class Runner")
print("=" * 70)
print("### conftest.py from class Runner")
print("=" * 70)
print(src[i:])

tf = os.path.join(ROOT, "tests", "test_m5_rules.py")
tsrc = open(tf).read()
j = tsrc.find("def runner")
print("=" * 70)
print("### test_m5_rules.py runner fixture")
print("=" * 70)
print(tsrc[j: j + 2500])

k = tsrc.find("SCENARIOS")
print("=" * 70)
print("### test_m5_rules.py SCENARIOS")
print("=" * 70)
print(tsrc[k: k + 3000])
