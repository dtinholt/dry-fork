"""Probe 197: gather everything needed for the three M5 failures.

Run:  python3 tests/fixtures-generated/probe197.py
"""
import inspect
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump197.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


import wl_support as W  # noqa: E402
import wlengine.headless as H  # noqa: E402
from wlengine import scenario as scmod  # noqa: E402

p("=== ref_labstate source ===")
p(inspect.getsource(W.ref_labstate))
p("=== headless names ===")
for nm in dir(H):
    if "snap" in nm.lower() or "labstate" in nm.lower() or "cell_change" in nm.lower():
        p("  " + nm)
for nm in ("snapshot", "sorted_cell_changes", "write_save_files", "save_game"):
    fn = getattr(H.Engine, nm, None)
    if fn is not None:
        p("=== Engine.%s ===" % nm)
        try:
            p(inspect.getsource(fn))
        except Exception as e:  # noqa: BLE001
            p("  (no source: %s)" % e)

# --- the walkthrough script and the CP5-pre-save checkpoint -------------------
SC = os.path.join(ROOT, "SPEC", "scenario")
wt = json.load(open(os.path.join(SC, "walkthrough.json"), encoding="utf-8"))
script = wt["script"]
idx = next(i for i, it in enumerate(script) if isinstance(it, dict) and it.get("checkpoint") == "CP5-pre-save")
p("=== walkthrough script up to CP5-pre-save ===")
p(json.dumps(script[:idx + 1]))

d = tempfile.mkdtemp()
scmod.compile(SC, d)
ev = H.run(d, {"seed": 5, "script": script[:idx + 1]}, 5)
st = next(e["state"] for e in ev if e.get("type") == "checkpoint" and e.get("name") == "CP5-pre-save")
p("=== CP5-pre-save cell_changes ===")
p(json.dumps(st.get("cell_changes")))
p("=== cell_change events ===")
for e in ev:
    if e.get("type") == "cell_change":
        p(json.dumps(e, sort_keys=True))
p("=== all checkpoint names ===")
p(json.dumps([e.get("name") for e in ev if e.get("type") == "checkpoint"]))

# --- the bump scenario -------------------------------------------------------
ev2 = H.run(d, {"seed": 5, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, 5)
p("=== bump events ===")
for e in ev2:
    p(json.dumps(e, sort_keys=True)[:300])
p("=== bump checkpoint a ===")
p(json.dumps(next(e["state"] for e in ev2 if e.get("type") == "checkpoint"), sort_keys=True))

# --- the raider fight orders -------------------------------------------------
idx4 = next(i for i, it in enumerate(script) if isinstance(it, dict) and it.get("checkpoint") == "CP4")
ev3 = H.run(d, {"seed": 3, "script": script[:idx4 + 1]}, 3)
p("=== raider fight seed 3 events ===")
for e in ev3:
    if e.get("type") in ("encounter_start", "round_orders", "round_start", "attack", "jam", "click",
                         "monster_dies", "advance", "group_closes", "reload", "unjammed", "combat_end",
                         "xp", "promote", "money", "cell_change", "check", "paragraph", "checkpoint"):
        p(json.dumps(e, sort_keys=True)[:400])

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
