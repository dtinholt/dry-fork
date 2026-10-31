"""Probe 11: dump the parts of the frozen tests and the engine that matter for
M5 combat. Prints source excerpts so the next iteration can read them without
spending the read budget on whole files.
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


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "headless"):
        show("src/wlengine/headless.py", r"^\s*(def |class )")
    if which in ("all", "m5"):
        show("tests/test_m5_rules.py", r"^\s*def test_")
    if which in ("all", "support"):
        show("tests/wl_support.py", r"^def ref_|^class RefRng|^    def ")
    if which in ("all", "combat"):
        show("src/wlengine/headless.py", r"combat|encounter|surprise|group|phase|round")
    if which in ("all", "rules"):
        show("src/wlengine/rules.py", r"^\s*(def |class )")
    if which == "m5body":
        show("tests/test_m5_rules.py", r"def test_", after=40)
    if which == "refbody":
        show("tests/wl_support.py", r"^def ref_", after=14)
    if which == "combatbody":
        show("src/wlengine/headless.py", r"def .*(combat|encounter|surprise|group|phase|round)",
             after=45)
    if which == "rulesbody":
        show("src/wlengine/rules.py", r"^\s*def ", after=20)
    if which == "m5all":
        p = PROJECT / "tests/test_m5_rules.py"
        print(p.read_text(encoding="utf-8"))
    if which == "combatall":
        p = PROJECT / "src/wlengine/headless.py"
        print(p.read_text(encoding="utf-8"))
    if which == "supportall":
        p = PROJECT / "tests/wl_support.py"
        print(p.read_text(encoding="utf-8"))
    if which == "rulesall":
        p = PROJECT / "src/wlengine/rules.py"
        print(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
