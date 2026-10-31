"""Probe 427: raw SPEC-05 Saltwell rows with column ruler; reference-log bumps."""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md"), encoding="utf-8").read()
lines = spec.splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith("### 5.2 Saltwell"))
end = next(i for i, l in enumerate(lines) if i > start and l.startswith("### 5.3"))
for l in lines[start:end]:
    if l.strip().startswith("|") or l.strip().startswith("0"):
        print(repr(l))
print("ruler:      " + "".join(str(i % 10) for i in range(40)))

d = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")))
for e in d["events"]:
    if e.get("type") == "bump":
        print("bump", e)
