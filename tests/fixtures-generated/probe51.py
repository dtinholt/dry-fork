"""Run the engine's opening script and dump only the combat events + party."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from wlengine import scenario, headless  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")
wt = json.load(open(os.path.join(SCEN, "walkthrough.json")))
script = []
for item in wt["script"]:
    if isinstance(item, dict) and "repeat_until" in item:
        script.append("A")
        break
    script.append(item)

d = tempfile.mkdtemp()
scenario.compile(SCEN, d)

ev = headless.run(d, {"seed": 20261021, "script": script}, 20261021)
started = False
for e in ev:
    if e.get("type") == "encounter_start":
        started = True
    if started:
        print(json.dumps(e))

eng = headless.Engine(d, seed=20261021, options={})
eng.new_game(20261021)
for m in eng.party:
    print("MEMBER", m["slot"], m["name"], m["attrs"], m["skills"], m["items"],
          "ac", m["ac"], "hp", m["hp"], m["max_hp"], "wslot", m["weapon_slot"])
print("skill_table", eng.sc.skill_table[:6])
print("mobs", eng.sc.map(0)["mobs"][:3])
print("item recs", eng.sc.shops[0]["items"][:6])
