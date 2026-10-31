"""Probe 310: dump walkthrough.json token_rules / expected_rule / summary, and
grep SPEC-03/04/07 for look/interact semantics.

Run: python3 tests/fixtures-generated/probe310.py
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")
SPEC = os.path.join(ROOT, "SPEC")


def main():
    wt = json.load(open(os.path.join(SCEN, "walkthrough.json"), encoding="utf-8"))
    for k in ("token_rules", "expected_rule", "summary"):
        print("=" * 70)
        print(k)
        print("=" * 70)
        print(json.dumps(wt[k], indent=1)[:4000])
    print("=" * 70)
    print("grep look/interact in SPEC-03, SPEC-04, SPEC-07")
    print("=" * 70)
    for name in ("SPEC-03-maps.md", "SPEC-04-rules.md", "SPEC-07-acceptance.md"):
        p = os.path.join(SPEC, name)
        for i, line in enumerate(open(p, encoding="utf-8").read().splitlines(), 1):
            low = line.lower()
            if "look" in low or "interact" in low:
                print("%s:%d| %s" % (name, i, line))


if __name__ == "__main__":
    main()
