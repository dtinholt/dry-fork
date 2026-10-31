"""Probe 223: dump the parts of combat.py / headless.py that matter for the
M5 failures (weapon status byte, auto_orders, bump handling, cell_change tails,
promotion).  Read-only; prints to stdout.

Usage: python3 tests/fixtures-generated/probe223.py [file ...]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "wlengine"

PATTERNS = {
    "combat.py": [r"def weapon_ammo", r"def spend_ammo", r"def reload", r"def auto_orders",
                  r"jammed", r"loaded", r"0x80", r"0x7F", r"def jam", r"def unjam",
                  r"def resolve", r"def round", r"def fire", r"def _", r"status"],
    "headless.py": [r"def bump", r"def move", r"cell_change", r"action_class", r"def step",
                    r"steps", r"promote", r"def _tail", r"def _apply", r"def _cell",
                    r"def _run", r"def _do", r"def _handle"],
}


def show(path, patterns, ctx=6):
    text = (SRC / path).read_text().splitlines()
    hits = set()
    for i, line in enumerate(text):
        for p in patterns:
            if re.search(p, line):
                for j in range(max(0, i - ctx), min(len(text), i + ctx + 1)):
                    hits.add(j)
    print("=" * 70)
    print(path, "lines", len(text))
    print("=" * 70)
    last = -10
    for j in sorted(hits):
        if j != last + 1:
            print("   ...")
        print("%4d| %s" % (j + 1, text[j]))
        last = j


def whole(path):
    text = (SRC / path).read_text().splitlines()
    print("=" * 70)
    print(path, "lines", len(text), "(whole file)")
    print("=" * 70)
    for i, line in enumerate(text):
        print("%4d| %s" % (i + 1, line))


def main():
    args = sys.argv[1:]
    if not args:
        for name, pats in PATTERNS.items():
            show(name, pats)
    else:
        for name in args:
            if name.endswith(":all"):
                whole(name[:-4])
            else:
                show(name, PATTERNS.get(name, [r"."]))


if __name__ == "__main__":
    main()
