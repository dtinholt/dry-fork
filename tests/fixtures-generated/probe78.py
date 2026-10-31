"""Dump the combat-relevant regions of the engine and tests so the next
iteration can implement combat without burning read budget.

Usage: python3 tests/fixtures-generated/probe78.py
Writes tests/fixtures-generated/dump78.txt.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump78.txt")

REGIONS = [
    ("src/wlengine/headless.py", 1, 70, "headless head"),
    ("src/wlengine/headless.py", 430, 640, "combat region"),
    ("src/wlengine/headless.py", 750, 1077, "encounter/save region"),
    ("src/wlengine/rules.py", 200, 318, "rules combat"),
    ("tests/test_m5_rules.py", 490, 730, "m5 combat tests"),
    ("tests/wl_combat_ref.py", 150, 200, "combat_ref consistency head"),
    ("tests/wl_combat_ref.py", 325, 346, "combat_ref tail"),
    ("tests/wl_support.py", 90, 200, "support needs"),
    ("tests/wl_support.py", 440, 531, "support groups/speed"),
    ("tests/conftest.py", 1, 130, "conftest"),
]

GREPS = [
    ("src/wlengine/headless.py", "def "),
    ("src/wlengine/headless.py", "combat"),
    ("src/wlengine/rules.py", "def "),
    ("tests/test_m5_rules.py", "def test_"),
]


def region(path, start, end, label):
    lines = open(os.path.join(ROOT, path), encoding="utf-8").read().splitlines()
    buf = ["=" * 70, "%s  %s:%d-%d" % (label, path, start, end), "=" * 70]
    for i in range(start - 1, min(end, len(lines))):
        buf.append("%5d| %s" % (i + 1, lines[i]))
    return buf


def grep(path, pat):
    lines = open(os.path.join(ROOT, path), encoding="utf-8").read().splitlines()
    buf = ["-" * 70, "grep %r in %s" % (pat, path), "-" * 70]
    for i, l in enumerate(lines):
        if pat in l:
            buf.append("%5d| %s" % (i + 1, l))
    return buf


def main():
    out = []
    for path, start, end, label in REGIONS:
        out += region(path, start, end, label)
    for path, pat in GREPS:
        out += grep(path, pat)
    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT, len(out), "lines")


if __name__ == "__main__":
    main()
