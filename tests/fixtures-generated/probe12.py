"""Probe 12: dump the frozen M5 test bodies and the engine's combat code.

This is a scratch analysis tool. It prints source excerpts so that later
iterations can inspect the exact expected event shapes without spending the
read budget on whole files. Usage:

    python3 tests/fixtures-generated/probe12.py <what>

where <what> is one of:
    m5        - the test function names in tests/test_m5_rules.py
    m5body    - every test function with 40 lines of body
    ref       - the ref_* helpers in tests/wl_support.py with 14 lines of body
    refall    - the whole of tests/wl_support.py
    combat    - the combat/encounter functions in src/wlengine/headless.py
    combatall - the whole of src/wlengine/headless.py
    rules     - the functions in src/wlengine/rules.py
    rulesall  - the whole of src/wlengine/rules.py
    scenario  - the functions in src/wlengine/scenario.py
    grep <pat> [path] - grep a pattern in a file (default: headless.py)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]


def show(path: str, pattern: str, before: int = 0, after: int = 0, limit: int = 400):
    p = PROJECT / path
    lines = p.read_text(encoding="utf-8").splitlines()
    rx = re.compile(pattern)
    hits = [i for i, l in enumerate(lines) if rx.search(l)]
    print("=" * 70)
    print("%s  (%d lines)  pattern=%r  hits=%d" % (path, len(lines), pattern, len(hits)))
    print("=" * 70)
    shown = set()
    for i in hits[:limit]:
        lo = max(0, i - before)
        hi = min(len(lines), i + after + 1)
        for k in range(lo, hi):
            if k in shown:
                continue
            shown.add(k)
            print("%5d| %s" % (k + 1, lines[k]))
        print("-" * 40)


def dump(path: str):
    p = PROJECT / path
    print("=" * 70)
    print("%s (%d lines)" % (path, len(p.read_text(encoding="utf-8").splitlines())))
    print("=" * 70)
    print(p.read_text(encoding="utf-8"))


def main():
    args = sys.argv[1:]
    which = args[0] if args else "all"
    if which == "m5":
        show("tests/test_m5_rules.py", r"^\s*def test_")
    elif which == "m5body":
        show("tests/test_m5_rules.py", r"^\s*def test_", after=40)
    elif which == "m5all":
        dump("tests/test_m5_rules.py")
    elif which == "ref":
        show("tests/wl_support.py", r"^def ref_|^class RefRng", after=14)
    elif which == "refall":
        dump("tests/wl_support.py")
    elif which == "combat":
        show("src/wlengine/headless.py", r"^\s*(def |class )")
    elif which == "combatbody":
        show("src/wlengine/headless.py",
             r"def .*(combat|encounter|surprise|group|phase|round|attack|jam|reload)",
             after=45)
    elif which == "combatall":
        dump("src/wlengine/headless.py")
    elif which == "rules":
        show("src/wlengine/rules.py", r"^\s*(def |class )")
    elif which == "rulesbody":
        show("src/wlengine/rules.py", r"^\s*def ", after=20)
    elif which == "rulesall":
        dump("src/wlengine/rules.py")
    elif which == "scenario":
        show("src/wlengine/scenario.py", r"^\s*(def |class )")
    elif which == "grep":
        pat = args[1]
        path = args[2] if len(args) > 2 else "src/wlengine/headless.py"
        show(path, pat, after=6)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
