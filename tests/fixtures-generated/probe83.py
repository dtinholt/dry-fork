"""Measure the SPEC-05 ASCII map rows for Saltwell."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lines = open(os.path.join(ROOT, "SPEC/SPEC-05-scenario.md"), encoding="utf-8").read().splitlines()
start = None
for i, l in enumerate(lines):
    if l.strip().startswith("0  ||||"):
        start = i
        break
print("start line", start + 1)
for k in range(0, 33):
    l = lines[start + k]
    body = l[5:]
    print("%2d len=%d %r" % (k, len(body), body))
