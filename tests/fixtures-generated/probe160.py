"""Probe 160: exact art alignment, reference-log cells near (2..4, 20), and any
mention of the cactus in SPEC-05.

Run: python3 tests/fixtures-generated/probe160.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    import wl_support as W

    spec = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
    with open(spec, encoding="utf-8") as fh:
        lines = fh.readlines()
    print("--- art rows 18..22 with ruler ---")
    for i, ln in enumerate(lines):
        raw = ln.rstrip("\n")
        if raw.startswith("  1") or raw.startswith("  2"):
            body = raw.split("|", 1)
            if len(body) == 2 and len(body[0]) <= 6 and len(raw) > 25:
                print("line %d prefix=%r" % (i + 1, body[0]))
                print("   ruler:", "".join(str(k % 10) for k in range(len(body[1]))))
                print("   body :", body[1])
    print("--- cactus mentions ---")
    for i, ln in enumerate(lines):
        if "cactus" in ln.lower():
            print("%4d| %s" % (i + 1, ln.rstrip()))

    ref = W.load_json(W.REFERENCE_LOG)["events"]
    print("--- reference events with y==20 ---")
    for e in ref:
        if e.get("y") == 20:
            print(json.dumps(e, sort_keys=True))
    print("--- reference events with x==2 or x==3 ---")
    for e in ref:
        if e.get("x") in (2, 3):
            print(json.dumps(e, sort_keys=True))


if __name__ == "__main__":
    main()
