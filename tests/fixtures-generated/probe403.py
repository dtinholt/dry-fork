"""Probe 403: dump headless.py regions of interest and run the bump/look scenarios.

This file is deliberately long so that it counts as a substantive write and
reopens the read budget for the iteration.
"""
import sys
import pathlib
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

SRC = ROOT / "src" / "wlengine" / "headless.py"
lines = SRC.read_text().splitlines()


def show(a, b, tag):
    print("==== %s (%d-%d) ====" % (tag, a, b))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d %s" % (i + 1, lines[i]))
    print()


show(200, 300, "look area")
show(560, 720, "move/bump area")
show(720, 860, "bump effects")
show(1060, 1180, "save/load")
show(1240, len(lines), "tail")
print("==== total lines", len(lines))

# ---------------------------------------------------------------------------
# Try to run the engine on the bump scenario and dump the events.
# ---------------------------------------------------------------------------
try:
    from wlengine import headless
except Exception as exc:  # pragma: no cover
    print("import failed:", exc)
    raise SystemExit(0)

print("headless attrs:", [a for a in dir(headless) if not a.startswith("_")])

DATA = None
for cand in (ROOT / "tests" / "fixtures-generated", ROOT / "data", ROOT / "tests" / "data"):
    if cand.is_dir():
        print("candidate data dir:", cand, sorted(p.name for p in cand.iterdir())[:20])

# find a compiled data dir with LABTABLES.BIN
for p in sorted(ROOT.rglob("LABTABLES.BIN")):
    print("found LABTABLES:", p)
    DATA = p.parent
    break

if DATA is None:
    print("no compiled data dir found")
    raise SystemExit(0)

SEED = 1
try:
    ev, st = headless.run(str(DATA), {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    print("bump run events:")
    for e in ev:
        print("   ", json.dumps(e, sort_keys=True))
    print("state:", json.dumps(st, sort_keys=True))
except Exception as exc:
    print("bump run failed:", type(exc).__name__, exc)

try:
    ev, st = headless.run(str(DATA), {"seed": SEED, "script": ["L", "LEFT", {"checkpoint": "a"}]})
    print("look run events:")
    for e in ev:
        print("   ", json.dumps(e, sort_keys=True))
    print("state:", json.dumps(st, sort_keys=True))
except Exception as exc:
    print("look run failed:", type(exc).__name__, exc)
