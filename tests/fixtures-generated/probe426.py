"""Probe 426: extract the Saltwell ASCII map straight from SPEC-05 and index it."""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md"), encoding="utf-8").read()
lines = spec.splitlines()
# find the Saltwell section
start = next(i for i, l in enumerate(lines) if l.startswith("### 5.2 Saltwell"))
end = next(i for i, l in enumerate(lines) if i > start and l.startswith("### 5.3"))
block = lines[start:end]
for l in block:
    if l.startswith("  ") and ("|" in l or ";" in l):
        # strip the label
        m = re.match(r"^\s*\d+\s\s(.*)$", l)
        if m:
            row = m.group(1)
            print("len=%d %r" % (len(row), row))
            print("   non-dot:", [(x, c) for x, c in enumerate(row) if c not in ".|"])
