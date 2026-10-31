"""Dump test_m5_rules.py head (helpers, runner fixture usage), conftest runner
fixture, and SPEC-04 combat sections. Writes dump79.txt."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump79.txt")

REGIONS = [
    ("tests/test_m5_rules.py", 1, 120, "m5 head"),
    ("tests/test_m5_rules.py", 380, 495, "m5 helpers/runner"),
    ("tests/conftest.py", 1, 260, "conftest"),
    ("tests/wl_support.py", 1, 95, "support head"),
    ("tests/wl_support.py", 200, 440, "support mid"),
    ("tests/wl_combat_ref.py", 1, 150, "combat_ref head"),
]


def region(path, start, end, label):
    lines = open(os.path.join(ROOT, path), encoding="utf-8").read().splitlines()
    buf = ["=" * 70, "%s  %s:%d-%d" % (label, path, start, end), "=" * 70]
    for i in range(start - 1, min(end, len(lines))):
        buf.append("%5d| %s" % (i + 1, lines[i]))
    return buf


def main():
    out = []
    for path, start, end, label in REGIONS:
        out += region(path, start, end, label)
    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT, len(out), "lines")


if __name__ == "__main__":
    main()
