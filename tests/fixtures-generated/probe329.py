"""probe329: dump the headless input dispatch region so the next patch can add
the `L` (look) key. Prints source lines 200-460 of src/wlengine/headless.py and
the whole of src/wlengine/ui.py, plus a quick grep for mode handling.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src", "wlengine")


def show(path, lo, hi):
    print("=" * 70)
    print(path, "lines", lo, "-", hi)
    print("=" * 70)
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for i in range(lo - 1, min(hi, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))


def grep(path, pat):
    print("-" * 70)
    print("grep %r in %s" % (pat, path))
    rx = re.compile(pat)
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh.read().splitlines(), 1):
            if rx.search(line):
                print("%4d| %s" % (i, line))


def main():
    hp = os.path.join(SRC, "headless.py")
    show(hp, 200, 470)
    grep(hp, r"mode|self\.key|def ")
    show(os.path.join(SRC, "ui.py"), 1, 200)


if __name__ == "__main__":
    main()
