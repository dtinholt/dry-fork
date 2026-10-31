"""Probe 204: party items, item records, and the reference fight events."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump204.txt")
buf = []


def out(s=""):
    buf.append(str(s))


items = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "items.json")))
out("items.json type: %s" % type(items))
if isinstance(items, dict):
    out("keys: %s" % list(items))
    for k, v in items.items():
        out("%s: %s" % (k, json.dumps(v)[:2000]))
else:
    for i, v in enumerate(items):
        out("%d: %s" % (i, json.dumps(v)[:300]))

party = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "party.json")))
out("=== party.json ===")
out(json.dumps(party, indent=1)[:4000])

out("=== reference log: encounter + rounds ===")
ref = json.load(open(os.path.join(ROOT, "SPEC", "scenario",
                                  "walkthrough-reference-log.json")))
ev = ref["events"]
start = next(i for i, e in enumerate(ev) if e.get("type") == "encounter_start")
out("encounter_start at %d" % start)
for i in range(start - 4, min(len(ev), start + 90)):
    out("%d: %s" % (i, json.dumps(ev[i])[:500]))

out("=== reference CP4 state ===")
for i, e in enumerate(ev):
    if e.get("type") == "checkpoint" and e.get("name") in ("CP4", "CP3"):
        out("%s: %s" % (e.get("name"), json.dumps(e.get("state"))[:3000]))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
