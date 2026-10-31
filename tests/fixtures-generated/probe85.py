"""Dump items.json, party.json, compiled party at CP3, and the reference log's
combat events. Writes dump81.txt."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump81.txt")

out = []


def add(s=""):
    out.append(str(s))


add("=== items.json ===")
add(json.dumps(json.load(open(os.path.join(ROOT, "SPEC/scenario/items.json"))), indent=1))
add("=== party.json ===")
add(json.dumps(json.load(open(os.path.join(ROOT, "SPEC/scenario/party.json"))), indent=1))
add("=== encounters.json ===")
add(json.dumps(json.load(open(os.path.join(ROOT, "SPEC/scenario/encounters.json"))), indent=1))

from wlengine import scenario, headless  # noqa: E402

d = tempfile.mkdtemp()
scenario.compile(os.path.join(ROOT, "SPEC", "scenario"), d)
sc = scenario.load(d)
add("=== compiled party ===")
for m in sc.premade_party():
    add(json.dumps(m))
add("=== item table (1..12) ===")
for i in range(1, 13):
    add("%d %s" % (i, json.dumps(sc.item(i))))
add("=== overworld mobs ===")
add(json.dumps(sc.map(0).get("mobs")))
add("=== overworld record at (30,41) ===")
from wlengine import maps  # noqa: E402

m0 = sc.map(0)
add(json.dumps(maps.record_at(m0, 30, 41)))
add("class/action %r" % (m0["cells"]["actionClass"][41][30],))
add("image %r" % (m0["cells"]["image"][41][30],))

add("=== reference log combat events (seq 200-300) ===")
log = json.load(open(os.path.join(ROOT, "SPEC/scenario/walkthrough-reference-log.json")))
evs = log["events"] if isinstance(log, dict) else log
for e in evs:
    if 200 <= e.get("seq", -1) <= 300:
        add(json.dumps(e)[:400])

add("=== reference log: all combat-ish events ===")
for e in evs:
    if e.get("type") in ("encounter_start", "check", "surprised", "round_orders", "round_start",
                         "attack", "jam", "click", "monster_dies", "unconscious", "death",
                         "group_closes", "combat_end", "xp", "promote", "money", "cell_change",
                         "advance", "reload", "unjammed", "flee", "no_target"):
        add(json.dumps(e)[:400])

open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote", OUT, len(out), "lines")
