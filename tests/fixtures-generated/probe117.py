"""Dump the parts of headless.py we need to fix (M5).

Writes dump117.txt with the source of the relevant functions so the next
iteration can read it without spending the read budget on guesses.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "wlengine" / "headless.py"
OUT = Path(__file__).resolve().parent / "dump117.txt"

WANT = [
    "def bump_effect",
    "def victory",
    "def auto_orders",
    "def write_save_files",
    "def load_game",
    "def skill_attribute",
    "def attr_value",
    "def run_hook_at",
    "def apply_tail",
    "def do_check",
    "def check",
    "def hook",
    "def bump",
    "def move",
    "def step",
    "def save",
    "def load",
    "def spend_ammo",
    "def reload",
    "def ammo_boxes",
    "def loot",
    "def heal",
    "def pay",
]


def main():
    lines = SRC.read_text().splitlines()
    starts = []
    for i, ln in enumerate(lines):
        for w in WANT:
            if ln.strip().startswith(w):
                starts.append(i)
                break
    starts = sorted(set(starts))
    out = []
    for s in starts:
        # find the end: next line at the same or lower indent that starts a def/class
        indent = len(lines[s]) - len(lines[s].lstrip())
        e = s + 1
        while e < len(lines):
            ln = lines[e]
            if ln.strip() and (len(ln) - len(ln.lstrip())) <= indent and re.match(
                    r"\s*(def |class |@)", ln):
                break
            e += 1
        out.append("=" * 70)
        out.append("LINES %d-%d" % (s + 1, e))
        out.extend("%5d %s" % (k + 1, lines[k]) for k in range(s, e))
    OUT.write_text("\n".join(out) + "\n")
    print("wrote", OUT, len(out), "lines")


if __name__ == "__main__":
    main()
