"""Probe: dump combat-related source from headless.py and the M5 test tail.

Usage: python3 tests/fixtures-generated/probe2.py [what]
  what = headless (default) | test | ref | spec | all
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def dump(path, pattern, ctx=0, start=None, end=None):
    lines = Path(path).read_text().splitlines()
    if start is not None:
        lo = max(0, start - 1)
        hi = min(len(lines), end or len(lines))
        for j in range(lo, hi):
            print("%5d %s" % (j + 1, lines[j]))
        return
    rx = re.compile(pattern)
    hits = [i for i, l in enumerate(lines) if rx.search(l)]
    shown = set()
    for i in hits:
        for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
            shown.add(j)
    prev = None
    for j in sorted(shown):
        if prev is not None and j != prev + 1:
            print("   ...")
        print("%5d %s" % (j + 1, lines[j]))
        prev = j


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "headless"
    if what == "headless":
        dump(ROOT / "src/wlengine/headless.py",
             r"def |encounter|surprise|round|group|combat|monster|band|jam|reload|unjam|advance|closes",
             ctx=1)
    elif what == "test":
        dump(ROOT / "tests/test_m5_rules.py", r"def test_|encounter|surprise|round|combat", ctx=2)
    elif what == "ref":
        dump(ROOT / "tests/wl_combat_ref.py", r"def |encounter|surprise|round|group", ctx=1)
    elif what == "spec":
        dump(ROOT / "SPEC/SPEC-04-rules.md", r"^#|LR-3[0-9]|LR-4[0-9]", ctx=0)
    elif what == "conftest":
        dump(ROOT / "tests/conftest.py", r".", ctx=0)
    elif what == "support":
        dump(ROOT / "tests/wl_support.py", r"def |class ", ctx=1)
    elif what == "rules":
        dump(ROOT / "src/wlengine/rules.py", r"def |class ", ctx=1)
    elif what == "scenario":
        dump(ROOT / "src/wlengine/scenario.py", r"def |class ", ctx=1)
    else:
        print("unknown:", what)


if __name__ == "__main__":
    main()
