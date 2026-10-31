"""Dump the sources needed to implement combat (rules.py, headless.py head,
conftest.py, wl_support.py head, wl_combat_ref.py tail) into dump70.txt so it
can be read in chunks.  Also dumps the reference log combat window and the
scenario monster/weapon tables.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump70.txt")


def read(path, start=None, end=None):
    try:
        lines = open(path, encoding="latin-1").read().split("\n")
    except OSError as e:
        return ["<<missing %s: %s>>" % (path, e)]
    if start is not None:
        lines = lines[start - 1:end]
    return ["%4d %s" % (i + 1, l) for i, l in enumerate(lines)]


def main():
    chunks = []
    chunks.append("=" * 30 + " rules.py")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "rules.py")))
    chunks.append("=" * 30 + " headless.py 1-400")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "headless.py"), 1, 400))
    chunks.append("=" * 30 + " conftest.py")
    chunks.extend(read(os.path.join(ROOT, "tests", "conftest.py")))
    chunks.append("=" * 30 + " wl_support.py 1-260")
    chunks.extend(read(os.path.join(ROOT, "tests", "wl_support.py"), 1, 260))
    chunks.append("=" * 30 + " wl_support.py 260-560")
    chunks.extend(read(os.path.join(ROOT, "tests", "wl_support.py"), 260, 560))
    chunks.append("=" * 30 + " wl_combat_ref.py 150-400")
    chunks.extend(read(os.path.join(ROOT, "tests", "wl_combat_ref.py"), 150, 400))
    chunks.append("=" * 30 + " test_m5_rules.py 460-700")
    chunks.extend(read(os.path.join(ROOT, "tests", "test_m5_rules.py"), 460, 700))
    chunks.append("=" * 30 + " test_m5_rules.py 700-1000")
    chunks.extend(read(os.path.join(ROOT, "tests", "test_m5_rules.py"), 700, 1000))
    chunks.append("=" * 30 + " test_m5_rules.py 1000-1300")
    chunks.extend(read(os.path.join(ROOT, "tests", "test_m5_rules.py"), 1000, 1300))
    chunks.append("=" * 30 + " test_m5_rules.py 1300-1600")
    chunks.extend(read(os.path.join(ROOT, "tests", "test_m5_rules.py"), 1300, 1600))
    chunks.append("=" * 30 + " labstate.py")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "labstate.py")))
    chunks.append("=" * 30 + " headless.py 700-900")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "headless.py"), 700, 900))
    chunks.append("=" * 30 + " scenario.py 1-120")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "scenario.py"), 1, 120))
    chunks.append("=" * 30 + " scenario.py 120-400")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "scenario.py"), 120, 400))
    chunks.append("=" * 30 + " scenario.py 400-700")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "scenario.py"), 400, 700))
    chunks.append("=" * 30 + " scenario.py 700-900")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "scenario.py"), 700, 900))
    chunks.append("=" * 30 + " maps.py")
    chunks.extend(read(os.path.join(ROOT, "src", "wlengine", "maps.py")))
    with open(OUT, "w", encoding="latin-1") as fh:
        fh.write("\n".join(chunks) + "\n")
    print("wrote", OUT, len(chunks), "lines")


if __name__ == "__main__":
    main()
