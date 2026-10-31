"""Dump the current source of the headless/rules/combat functions relevant to M5,
plus the reference combat module and the walkthrough script.

Run:  python3 tests/fixtures-generated/probe103.py
"""
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wlengine.headless as H  # noqa: E402
import wlengine.rules as R  # noqa: E402
import wlengine.combat as C  # noqa: E402

SCEN = ROOT / "SPEC" / "scenario"
OUT = ROOT / "tests" / "fixtures-generated" / "dump103.txt"
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


def show_module(mod):
    p("### %s module source" % mod.__name__)
    p(inspect.getsource(mod))
    p()


show_module(C)
show_module(R)
show_module(H)

p("### walkthrough.json")
wt = json.loads((SCEN / "walkthrough.json").read_text())
p(json.dumps(wt, indent=1))

OUT.write_text("\n".join(buf))
print("wrote", OUT, len(buf), "lines")
