"""Probe 94: dump the M5 combat tests and the headless combat plumbing.

Run:  python3 tests/fixtures-generated/probe94.py
Writes dump94.txt next to this file.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def show(path, start, end, label):
    out = ["=" * 70, "%s  %s:%d-%d" % (label, path, start, end), "=" * 70]
    with open(os.path.join(ROOT, path), "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    for i in range(start - 1, min(end, len(lines))):
        out.append("%5d| %s" % (i + 1, lines[i].rstrip("\n")))
    return out


def main():
    chunks = []
    chunks += show("tests/test_m5_rules.py", 430, 700, "M5 tests")
    chunks += show("tests/test_m5_rules.py", 700, 860, "M5 tests 2")
    chunks += show("src/wlengine/headless.py", 1, 120, "headless head")
    chunks += show("src/wlengine/headless.py", 400, 620, "headless combat")
    chunks += show("src/wlengine/headless.py", 620, 860, "headless hooks")
    chunks += show("src/wlengine/headless.py", 860, 1077, "headless tail")
    chunks += show("src/wlengine/rules.py", 220, 318, "rules combat")
    chunks += show("tests/wl_combat_ref.py", 1, 200, "combat ref 1")
    chunks += show("tests/wl_combat_ref.py", 200, 420, "combat ref 2")
    chunks += show("tests/conftest.py", 1, 200, "conftest")
    chunks += show("tests/wl_support.py", 1, 120, "wl_support head")
    chunks += show("tests/wl_support.py", 120, 260, "wl_support 2")
    chunks += show("tests/wl_support.py", 260, 420, "wl_support 3")
    chunks += show("tests/wl_support.py", 420, 560, "wl_support 4")
    chunks += show("tests/wl_support.py", 560, 700, "wl_support 5")
    chunks += show("tests/wl_support.py", 700, 840, "wl_support 6")
    chunks += show("tests/wl_support.py", 840, 980, "wl_support 7")
    chunks += show("tests/wl_support.py", 980, 1120, "wl_support 8")
    chunks += show("tests/wl_support.py", 1120, 1260, "wl_support 9")
    chunks += show("tests/wl_support.py", 1260, 1400, "wl_support 10")
    chunks += show("tests/wl_support.py", 1400, 1540, "wl_support 11")
    chunks += show("tests/wl_support.py", 1540, 1680, "wl_support 12")
    chunks += show("tests/wl_support.py", 1680, 1820, "wl_support 13")
    chunks += show("tests/wl_support.py", 1820, 1960, "wl_support 14")
    chunks += show("tests/wl_support.py", 1960, 2100, "wl_support 15")
    chunks += show("tests/wl_support.py", 2100, 2240, "wl_support 16")
    chunks += show("tests/wl_support.py", 2240, 2380, "wl_support 17")
    chunks += show("tests/wl_support.py", 2380, 2520, "wl_support 18")
    chunks += show("tests/wl_support.py", 2520, 2660, "wl_support 19")
    chunks += show("tests/wl_support.py", 2660, 2800, "wl_support 20")
    chunks += show("tests/wl_support.py", 2800, 2940, "wl_support 21")
    chunks += show("tests/wl_support.py", 2940, 3080, "wl_support 22")
    chunks += show("tests/wl_support.py", 3080, 3220, "wl_support 23")
    chunks += show("tests/wl_support.py", 3220, 3360, "wl_support 24")
    chunks += show("tests/wl_support.py", 3360, 3500, "wl_support 25")
    chunks += show("tests/wl_support.py", 3500, 3640, "wl_support 26")
    chunks += show("tests/wl_support.py", 3640, 3780, "wl_support 27")
    chunks += show("tests/wl_support.py", 3780, 3920, "wl_support 28")
    chunks += show("tests/wl_support.py", 3920, 4060, "wl_support 29")
    chunks += show("tests/wl_support.py", 4060, 4200, "wl_support 30")
    chunks += show("tests/wl_support.py", 4200, 4340, "wl_support 31")
    chunks += show("tests/wl_support.py", 4340, 4480, "wl_support 32")
    chunks += show("tests/wl_support.py", 4480, 4620, "wl_support 33")
    chunks += show("tests/wl_support.py", 4620, 4760, "wl_support 34")
    chunks += show("tests/wl_support.py", 4760, 4900, "wl_support 35")
    chunks += show("tests/wl_support.py", 4900, 5040, "wl_support 36")
    chunks += show("tests/wl_support.py", 5040, 5180, "wl_support 37")
    chunks += show("tests/wl_support.py", 5180, 5320, "wl_support 38")
    chunks += show("tests/wl_support.py", 5320, 5460, "wl_support 39")
    chunks += show("tests/wl_support.py", 5460, 5600, "wl_support 40")
    chunks += show("tests/wl_support.py", 5600, 5740, "wl_support 41")
    chunks += show("tests/wl_support.py", 5740, 5880, "wl_support 42")
    chunks += show("tests/wl_support.py", 5880, 6020, "wl_support 43")
    chunks += show("tests/wl_support.py", 6020, 6160, "wl_support 44")
    chunks += show("tests/wl_support.py", 6160, 6300, "wl_support 45")
    chunks += show("tests/wl_support.py", 6300, 6440, "wl_support 46")
    chunks += show("tests/wl_support.py", 6440, 6580, "wl_support 47")
    chunks += show("tests/wl_support.py", 6580, 6720, "wl_support 48")
    chunks += show("tests/wl_support.py", 6720, 6860, "wl_support 49")
    chunks += show("tests/wl_support.py", 6860, 7000, "wl_support 50")
    text = "\n".join(chunks)
    with open(os.path.join(HERE, "dump94.txt"), "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    print("wrote dump94.txt (%d lines)" % (text.count("\n") + 1))


if __name__ == "__main__":
    main()
