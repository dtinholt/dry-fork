"""Dump the source of the combat-relevant parts of the engine.

Usage: python3 tests/fixtures-generated/probe35.py [pattern ...]
Prints every function/class definition line in src/wlengine/rules.py and
src/wlengine/headless.py, plus the full body of any function whose name
matches one of the given patterns.

With no arguments it prints the definition index of every module under src/.
With one or more arguments it prints the full body of the matching blocks.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = ["src/wlengine/rules.py", "src/wlengine/headless.py", "src/wlengine/scenario.py",
         "src/wlengine/maps.py"]

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


def main():
    pats = sys.argv[1:]
    for path in FILES:
        print("=" * 70)
        print(path)
        print("=" * 70)
        for b in blocks(path):
            if not pats:
                print("  %s" % b["name"])
            elif any(p in b["name"] for p in pats):
                print("\n".join(b["lines"]))
                print()


def grep(pattern):
    """Print every line of every module that contains pattern."""
    rx = re.compile(pattern)
    for path in FILES:
        for i, ln in enumerate(Path(ROOT / path).read_text().splitlines(), 1):
            if rx.search(ln):
                print("%s:%d: %s" % (path, i, ln))


if __name__ == "__main__":
    main()
