"""Probe 364: print every bump event in the frozen walkthrough reference log,
plus the surrounding input/move events, to learn the true cactus coordinate.
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")


def main():
    with open(P, encoding="utf-8") as fh:
        log = json.load(fh)
    if isinstance(log, dict):
        print("keys:", list(log)[:20])
        log = log.get("events") or log.get("log") or []
    print("n events", len(log))
    for i, e in enumerate(log):
        if e.get("type") == "bump":
            ctx = log[max(0, i - 3):i + 3]
            print("---- bump at index", i)
            for c in ctx:
                print("   ", json.dumps(c)[:200])


main()
