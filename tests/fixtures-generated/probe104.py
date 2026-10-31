"""Probe: dump the reference combat module + reference log, and run the engine
on the M5 scenarios to see the actual events.

Run:  python3 tests/fixtures-generated/probe104.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

SCEN = ROOT / "SPEC" / "scenario"
OUT = ROOT / "tests" / "fixtures-generated" / "dump104.txt"
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


p("### wl_combat_ref.py")
p((ROOT / "tests" / "wl_combat_ref.py").read_text())
p()
p("### walkthrough-reference-log.json (first 20000 chars)")
p((SCEN / "walkthrough-reference-log.json").read_text()[:20000])
p()

import wlengine.headless as H  # noqa: E402

WT = json.loads((SCEN / "walkthrough.json").read_text())


def prefix(upto):
    out = []
    for item in WT["script"]:
        out.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == upto:
            return out
    raise AssertionError(upto)


def run(name, script, seed, data_dir=None):
    p("=== run %s seed %s" % (name, seed))
    try:
        ev = H.run(data_dir or str(SCEN), {"seed": seed, "script": script}, seed)
    except Exception as e:  # noqa: BLE001
        p("EXC %r" % (e,))
        return []
    for e in ev:
        p(json.dumps(e))
    p()
    return ev


# 1. bump test
run("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}], 20261021)

# 2. fight seeds
for s in [1, 2, 3]:
    run("fight%d" % s, prefix("CP4"), s)

# 3. storehouse
run("cp6", prefix("CP6"), 20261021)

# 4. healer
run("cp7", prefix("CP7"), 20261021)

# 5. key lock
run("cp9", prefix("CP9"), 20261021)

OUT.write_text("\n".join(buf))
print("wrote", OUT, len(buf), "lines")
