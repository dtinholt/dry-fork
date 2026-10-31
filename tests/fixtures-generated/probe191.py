"""Probe 191: run the bump script, the walkthrough to CP5-pre-save, and the fight."""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump191.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


SC = os.path.join(ROOT, "SPEC", "scenario")
from wlengine import scenario as scmod  # noqa: E402
from wlengine import headless as hl  # noqa: E402

d = tempfile.mkdtemp()
scmod.compile(SC, d)

# 1. bump script
ev = hl.run(d, {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, 20261021)
p("=" * 70)
p("BUMP SCRIPT EVENTS")
for e in ev:
    p(json.dumps(e, sort_keys=True)[:300])

# 2. walkthrough to CP5-pre-save
wt = json.load(open(os.path.join(SC, "walkthrough.json"), encoding="utf-8"))
script = wt["script"]
names = [c["name"] for c in wt["checkpoints"]]
# find the index of the CP5-pre-save checkpoint in the script
idx = None
for i, item in enumerate(script):
    if isinstance(item, dict) and item.get("checkpoint") == "CP5-pre-save":
        idx = i
        break
p("=" * 70)
p("CP5-pre-save script index", idx)
d2 = tempfile.mkdtemp()
scmod.compile(SC, d2)
ev2 = hl.run(d2, {"seed": 20261021, "script": script[:idx + 1]}, 20261021)
cps = {e.get("name"): e.get("state") for e in ev2 if e.get("type") == "checkpoint"}
st = cps.get("CP5-pre-save")
p("our CP5-pre-save cell_changes: %r" % (st.get("cell_changes") if st else None))
p("our CP5-pre-save steps: %r" % (st.get("steps") if st else None))
p("our CP5-pre-save rng: %r" % (st.get("rng_state") if st else None))
p("our CP5-pre-save party: %r" % json.dumps(st.get("party") if st else None, sort_keys=True))
ls = os.path.join(d2, "LABSTATE.BIN")
if os.path.isfile(ls):
    from wlengine import labstate as lsm
    p("LABSTATE: %r" % lsm.decode_labstate(open(ls, "rb").read()))
p("cell_change events in the run:")
for e in ev2:
    if e.get("type") == "cell_change":
        p("  " + json.dumps(e, sort_keys=True))

# 3. the fight: run the walkthrough to CP4 and print round_orders
idx4 = None
for i, item in enumerate(script):
    if isinstance(item, dict) and item.get("checkpoint") == "CP4":
        idx4 = i
        break
d3 = tempfile.mkdtemp()
scmod.compile(SC, d3)
ev3 = hl.run(d3, {"seed": 20261021, "script": script[:idx4 + 1]}, 20261021)
p("=" * 70)
p("FIGHT EVENTS (walkthrough to CP4)")
for e in ev3:
    if e.get("type") in ("encounter_start", "round_orders", "round_start", "attack", "jam", "click",
                         "monster_dies", "advance", "group_closes", "reload", "unjammed", "combat_end",
                         "xp", "promote", "money", "cell_change", "checkpoint"):
        p(json.dumps(e, sort_keys=True)[:400])

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
