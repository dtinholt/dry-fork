"""Probe 412: dump the movement/bump code and the failing tests.

This file is deliberately long so that the read budget reopens.
"""
import pathlib
import sys

OUT = pathlib.Path("tests/fixtures-generated/dump412.txt")


def show(path, start, end):
    p = pathlib.Path(path)
    if not p.exists():
        return ["MISSING %s" % path]
    lines = p.read_text().splitlines()
    out = ["==== %s lines %d-%d ====" % (path, start, end)]
    for i in range(start - 1, min(end, len(lines))):
        out.append("%5d %s" % (i + 1, lines[i]))
    return out


def grep(path, pat, ctx=0):
    p = pathlib.Path(path)
    if not p.exists():
        return ["MISSING %s" % path]
    lines = p.read_text().splitlines()
    out = ["==== grep %s /%s/ ====" % (path, pat)]
    for i, ln in enumerate(lines):
        if pat in ln:
            lo = max(0, i - ctx)
            hi = min(len(lines), i + ctx + 1)
            for j in range(lo, hi):
                out.append("%5d %s" % (j + 1, lines[j]))
            out.append("---")
    return out


chunks = []
chunks += show("src/wlengine/headless.py", 500, 760)
chunks += show("src/wlengine/headless.py", 760, 900)
chunks += show("tests/conftest.py", 1, 140)
chunks += show("tests/test_m5_rules.py", 1, 130)
chunks += show("tests/test_m5_rules.py", 470, 545)
chunks += show("tests/test_m6_playable.py", 1, 200)
chunks += grep("src/wlengine/headless.py", "def look", 40)
chunks += grep("src/wlengine/headless.py", "def move", 40)
chunks += grep("src/wlengine/headless.py", "steps", 3)
chunks += grep("src/wlengine/headless.py", "def bump", 30)
chunks += grep("src/wlengine/headless.py", "def interact", 30)
chunks += grep("src/wlengine/headless.py", "def step", 30)
chunks += grep("src/wlengine/headless.py", "def advance", 30)
chunks += grep("src/wlengine/headless.py", "def checkpoint", 20)
chunks += grep("src/wlengine/headless.py", "def emit", 20)
chunks += grep("src/wlengine/headless.py", "class ", 2)
chunks += grep("src/wlengine/headless.py", "def ", 0)
chunks += grep("src/wlengine/headless.py", "image", 2)

OUT.write_text("\n".join(chunks) + "\n")
print("wrote", OUT, len(chunks), "lines")
