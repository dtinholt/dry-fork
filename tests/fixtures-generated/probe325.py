"""Probe 325: dump the source regions of headless.py we need to edit.

Prints:
  * run_repeat / _until_met (the repeat_until driver),
  * run() (the module-level entry point),
  * the Engine.__init__ signature and the first_frame-relevant state,
  * the scenario helpers used to build a fresh game,
  * the scenario module's public API (so ui.py can build a frame state).

This is a read-only probe: it never writes anything outside stdout.
"""

import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, SRC)

from wlengine import headless  # noqa: E402
from wlengine import scenario  # noqa: E402

path = os.path.join(SRC, "wlengine", "headless.py")
lines = open(path, encoding="utf-8").read().splitlines()


def show(a, b):
    print("---- headless.py lines %d..%d ----" % (a, b))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d %s" % (i + 1, lines[i]))


show(1180, len(lines))
print()
print("---- Engine.__init__ ----")
show(54, 100)
print()
print("---- run_script / input / dispatch ----")
show(200, 250)
print()
print("---- has first_frame_state? ----", hasattr(headless, "first_frame_state"))
print("---- headless module attrs ----", [n for n in dir(headless) if not n.startswith("_")])
print()
print("---- Engine methods ----")
print([n for n in dir(headless.Engine) if not n.startswith("__")])
print()
print("---- scenario module attrs ----")
print([n for n in dir(scenario) if not n.startswith("_")])
print()
print("---- scenario classes ----")
for name in dir(scenario):
    obj = getattr(scenario, name)
    if inspect.isclass(obj) and obj.__module__ == scenario.__name__:
        print(name, [n for n in dir(obj) if not n.startswith("__")])
print()
print("---- scenario source: class defs and defs ----")
spath = os.path.join(SRC, "wlengine", "scenario.py")
slines = open(spath, encoding="utf-8").read().splitlines()
for i, l in enumerate(slines):
    if l.startswith("class ") or l.startswith("def ") or l.strip().startswith("def "):
        print("%4d %s" % (i + 1, l))
