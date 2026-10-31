"""Probe 164: walkthrough start, SPEC-05 section 14, and any 'cactus' mention
in the tests.

Run: python3 tests/fixtures-generated/probe164.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
SPEC = os.path.join(ROOT, "SPEC")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)


def section(path, heading, stop_prefix="## "):
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith(heading):
            start = i
            break
    if start is None:
        print("no heading", heading, "in", path)
        return
    for i in range(start, len(lines)):
        if i > start and lines[i].startswith(stop_prefix):
            break
        sys.stdout.write("%4d| %s" % (i + 1, lines[i]))


def main():
    import wl_support as W

    wt = W.load_json(W.SCENARIO / "walkthrough.json")
    print("start:", json.dumps(wt.get("start")))
    print("checkpoints:", json.dumps(wt.get("checkpoints"))[:2000])
    print("token_rules:", json.dumps(wt.get("token_rules"))[:2000])

    section(os.path.join(SPEC, "SPEC-05-scenario.md"), "### 14.1")
    section(os.path.join(SPEC, "SPEC-05-scenario.md"), "### 14.2")

    print("--- cactus in tests ---")
    for name in sorted(os.listdir(TESTS)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(TESTS, name), encoding="utf-8") as fh:
            for i, ln in enumerate(fh):
                if "cactus" in ln.lower():
                    print("%s:%d: %s" % (name, i + 1, ln.rstrip()))


if __name__ == "__main__":
    main()
