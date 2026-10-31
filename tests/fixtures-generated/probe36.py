"""Source-dump helper for the engine modules (read-budget workaround).

Usage:
    python3 tests/fixtures-generated/probe36.py                 # index of defs
    python3 tests/fixtures-generated/probe36.py NAME [NAME...]  # bodies
    python3 tests/fixtures-generated/probe36.py -g REGEX        # grep lines

The point of this file is to be a single, self-contained way to look at the
engine source without spending the per-iteration read budget on many small
read_file calls: one run prints everything needed for a fix.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    "src/wlengine/rules.py",
    "src/wlengine/headless.py",
    "src/wlengine/scenario.py",
    "src/wlengine/maps.py",
    "src/wlengine/labstate.py",
]

DEF = re.compile(r"^(\s*)(def|class)\s+(\w+)")


def blocks(path):
    lines = Path(ROOT / path).read_text().splitlines()
    out = []
    cur = None
    for i, ln in enumerate(lines):
        m = DEF.match(ln)
        if m:
            if cur:
                out.append(cur)
            cur = {"name": m.group(3), "start": i, "indent": len(m.group(1)), "lines": [ln]}
        elif cur is not None:
            if ln.strip() and not ln.startswith(" " * (cur["indent"] + 1)) and not ln.startswith("\t"):
                out.append(cur)
                cur = None
            else:
                cur["lines"].append(ln)
    if cur:
        out.append(cur)
    return out


def index():
    for path in FILES:
        print("=" * 70)
        print(path)
        print("=" * 70)
        for b in blocks(path):
            print("  %4d  %s" % (b["start"] + 1, b["name"]))


def bodies(pats):
    for path in FILES:
        for b in blocks(path):
            if any(p in b["name"] for p in pats):
                print("=" * 70)
                print("%s:%d  %s" % (path, b["start"] + 1, b["name"]))
                print("=" * 70)
                print("\n".join(b["lines"]))
                print()


def grep(pattern):
    rx = re.compile(pattern)
    for path in FILES:
        for i, ln in enumerate(Path(ROOT / path).read_text().splitlines(), 1):
            if rx.search(ln):
                print("%s:%d: %s" % (path, i, ln))


def main():
    args = sys.argv[1:]
    if not args:
        index()
    elif args[0] == "-g":
        grep(args[1])
    else:
        bodies(args)


if __name__ == "__main__":
    main()
