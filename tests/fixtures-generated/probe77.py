"""Dump the combat-relevant regions of headless.py, rules.py, test_m5_rules.py
and wl_combat_ref.py so the next iteration can implement combat without burning
read budget. Run: python3 tests/fixtures-generated/probe77.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump77.txt")


def region(path, start, end, label):
    lines = open(os.path.join(ROOT, path), encoding="utf-8").read().splitlines()
    buf = ["=" * 70, "%s  %s:%d-%d" % (label, path, start, end), "=" * 70]
    for i in range(start - 1, min(end, len(lines))):
        buf.append("%5d| %s" % (i + 1, lines[i]))
    return buf


def grep(path, pat):
    lines = open(os.path.join(ROOT, path), encoding="utf-8").read().splitlines()
    buf = ["-" * 70, "grep %r in %s" % (pat, path), "-" * 70]
    for i, l in enumerate(lines):
        if pat in l:
            buf.append("%5d| %s" % (i + 1, l))
    return buf


out = []
out += region("src/wlengine/headless.py", 1, 70, "headless head")
out += grep("src/wlengine/headless.py", "def ")
out += region("src/wlengine/headless.py", 430, 640, "combat region")
out += region("src/wlengine/headless.py", 750, 1077, "encounter/save region")
out += region("src/wlengine/rules.py", 200, 318, "rules combat")
out += region("tests/test_m5_rules.py", 490, 730, "m5 combat tests")
out += region("tests/wl_combat_ref.py", 150, 200, "combat_ref consistency head")
out += region("tests/wl_combat_ref.py", 325, 346, "combat_ref tail")
out += region("tests/wl_support.py", 90, 200, "support needs")
out += region("tests/wl_support.py", 440, 531, "support groups/speed")
out += region("tests/conftest.py", 1, 120, "conftest")

open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote", OUT, len(out), "lines")
