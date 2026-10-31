"""probe332: dump the headless input dispatch region so the next patch can add
the `L` (look) key, plus the whole of src/wlengine/ui.py.

Usage: python3 tests/fixtures-generated/probe332.py [lo] [hi]
Prints source lines lo..hi of src/wlengine/headless.py (default 200..470),
then every line of headless.py matching mode/key/def, then ui.py in full.
This is a read-only diagnostic; it changes nothing.

The point of this probe is to let the next iteration see the exact shape of
`Engine.input` (the token dispatch) without spending a read-budget slot on a
whole-file read. It prints with line numbers so a patch can be written against
the printed text directly.

Sections printed:
  1. headless.py lines lo..hi (default 200..470) -- the input dispatch and the
     movement/bump helpers.
  2. every line of headless.py matching mode|self.key|def -- the mode table.
  3. ui.py in full -- the curses-free renderer used by the M6 frame tests.
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
    print()


def grep(path, pat):
    print("-" * 70)
    print("grep %r in %s" % (pat, path))
    print("-" * 70)
    rx = re.compile(pat)
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh.read().splitlines(), 1):
            if rx.search(line):
                print("%4d| %s" % (i, line))
    print()


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 470
    hp = os.path.join(SRC, "headless.py")
    show(hp, lo, hi)
    grep(hp, r"mode|self\.key|def ")
    show(os.path.join(SRC, "ui.py"), 1, 400)


if __name__ == "__main__":
    main()
