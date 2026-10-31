"""Probe 189: dump reference-log checkpoints CP3..CP6 and the walkthrough script."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump189.txt")
buf = []

log = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json"), encoding="utf-8"))
evs = log["events"]
cps = {e.get("name"): e.get("state") for e in evs if e.get("type") == "checkpoint"}
buf.append("checkpoint names: %r" % list(cps))
for name in ("CP3", "CP4", "CP5-pre-save", "CP5", "CP6"):
    st = cps.get(name)
    buf.append("=" * 70)
    buf.append("CP %s" % name)
    buf.append(json.dumps(st, indent=1, sort_keys=True))

# the events around the fight and the save
buf.append("=" * 70)
buf.append("EVENTS (type, key fields)")
for i, e in enumerate(evs):
    t = e.get("type")
    if t == "checkpoint":
        buf.append("%4d checkpoint %s" % (i, e.get("name")))
    elif t in ("cell_change", "money", "xp", "promote", "save", "load", "combat_end", "encounter_start",
               "round_orders", "round_start", "attack", "jam", "click", "monster_dies", "advance",
               "group_closes", "unconscious", "death", "reload", "unjammed", "bump", "move", "input",
               "paragraph", "message", "win", "check", "unlock", "prompt", "buy", "equip", "recruit"):
        buf.append("%4d %s" % (i, json.dumps(e, sort_keys=True)))
    else:
        buf.append("%4d %s %s" % (i, t, json.dumps({k: v for k, v in e.items() if k not in ("seq", "type")}, sort_keys=True)[:200]))

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
