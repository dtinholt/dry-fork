"""Probe 381: dump reference-log bumps and the events around them; also print
the spec ASCII Saltwell row 20 with indices.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REF = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")
SPEC = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")


def main():
    ev = json.load(open(REF))["events"]
    bumps = [(i, e) for i, e in enumerate(ev) if e.get("type") == "bump"]
    print("bumps:", len(bumps))
    for i, e in bumps:
        print("  idx", i, json.dumps(e, sort_keys=True))
    print("--- events 118..140")
    for i in range(118, 141):
        print(" ", i, json.dumps(ev[i], sort_keys=True)[:200])
    lines = open(SPEC).read().splitlines()
    starts = [i for i, ln in enumerate(lines)
              if ln.strip().startswith("00000000001111111111222222222233")]
    start = starts[1]
    row = lines[start + 2 + 20]
    m = re.match(r"^\s*(\d{1,2})\s{2,}(\S{32})\s*$", row)
    s = m.group(2)
    print("spec row 20:", s)
    print("index      :", "".join(str(i % 10) for i in range(32)))
    print("chars      :", " ".join(s))


main()
