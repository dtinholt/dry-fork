"""Probe 166: dump events for the failing M5 tests (standalone).

Run: python3 tests/fixtures-generated/probe166.py
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
SRC = os.path.join(ROOT, "src")
SPEC = os.path.join(ROOT, "SPEC")
for p in (SRC, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)

OUT = HERE


def dump(name, ev):
    lines = []
    for i, e in enumerate(ev):
        lines.append("%4d %s" % (i, json.dumps(e, default=str, sort_keys=True)))
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return lines


def compile_data():
    import wlengine.scenario as sc
    d = tempfile.mkdtemp(prefix="probe166-")
    sc.compile(os.path.join(SPEC, "scenario"), d)
    return d


def main():
    import wlengine.headless as H
    import test_m5_rules as T
    import inspect

    with open(os.path.join(OUT, "dump167src.txt"), "w") as fh:
        fh.write(inspect.getsource(T.test_raider_fight_rules))

    dd = compile_data()
    print("compiled to", dd)

    # --- bump -----------------------------------------------------------
    ev = H.run(dd, {"seed": T.SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    lines = dump("dump166.txt", ev)
    print("=== bump tail ===")
    print("\n".join(lines[-30:]))


if __name__ == "__main__":
    main()
