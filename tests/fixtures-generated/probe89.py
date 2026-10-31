"""Dump the sources needed to finish M5 combat (iter 62).

Writes tests/fixtures-generated/dump89.txt with:
  - src/wlengine/rules.py (full)
  - tests/wl_support.py (full)
  - src/wlengine/combat.py (full)
  - src/wlengine/headless.py lines 440-1077
  - tests/test_m5_rules.py (full)
  - tests/conftest.py (full)
  - tests/wl_combat_ref.py (full)
  - src/wlengine/scenario.py (full)
  - src/wlengine/labstate.py (full)
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

FILES = [
    ("src/wlengine/rules.py", None, None),
    ("tests/wl_support.py", None, None),
    ("src/wlengine/combat.py", None, None),
    ("src/wlengine/headless.py", 440, 1077),
    ("tests/test_m5_rules.py", None, None),
    ("tests/conftest.py", None, None),
    ("tests/wl_combat_ref.py", None, None),
    ("src/wlengine/scenario.py", None, None),
    ("src/wlengine/labstate.py", None, None),
]


def read(path, start=None, end=None):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    if start is not None:
        lines = lines[start - 1:end]
    return lines


def section(out, title, lines):
    out.append("==== %s (%d lines) ====" % (title, len(lines)))
    for i, ln in enumerate(lines, 1):
        out.append("%5d %s" % (i, ln))
    out.append("")


def main():
    out = []
    for path, start, end in FILES:
        title = path if start is None else "%s %d-%d" % (path, start, end)
        section(out, title, read(path, start, end))
    with open(os.path.join(HERE, "dump89.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote dump89.txt: %d lines" % len(out))


if __name__ == "__main__":
    main()
