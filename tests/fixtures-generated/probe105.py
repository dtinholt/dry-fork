"""Probe: compile the scenario, then run the engine on the M5 scenarios and dump
the events.

Run:  python3 tests/fixtures-generated/probe105.py
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

SCEN = ROOT / "SPEC" / "scenario"
OUT = ROOT / "tests" / "fixtures-generated" / "dump105.txt"
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


import wlengine.headless as H  # noqa: E402
import wlengine.scenario as S  # noqa: E402

WT = json.loads((SCEN / "walkthrough.json").read_text())

tmp = Path(tempfile.mkdtemp(prefix="wlprobe"))
S.compile(str(SCEN), str(tmp))
p("compiled to %s" % tmp)
p("files: %s" % sorted(x.name for x in tmp.iterdir()))


def prefix(upto):
    out = []
    for item in WT["script"]:
        out.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == upto:
            return out
    raise AssertionError(upto)


def run(name, script, seed, data_dir=None):
    p("=== run %s seed %s" % (name, seed))
    dd = data_dir or tmp
    try:
        ev = H.run(str(dd), {"seed": seed, "script": script}, seed)
    except Exception as e:  # noqa: BLE001
        import traceback
        p("EXC %r" % (e,))
        p(traceback.format_exc())
        return []
    for e in ev:
        p(json.dumps(e))
    p()
    return ev


run("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}], 20261021)

for s in [1, 2, 3]:
    run("fight%d" % s, prefix("CP4"), s)

run("cp6", prefix("CP6"), 20261021)
run("cp7", prefix("CP7"), 20261021)
run("cp9", prefix("CP9"), 20261021)

OUT.write_text("\n".join(buf))
print("wrote", OUT, len(buf), "lines")
