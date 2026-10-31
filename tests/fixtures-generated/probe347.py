"""Probe: what does the frozen reference log say about positions, bumps and cells?"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "..", "SPEC", "scenario")

ref = json.load(open(os.path.join(SPEC, "walkthrough-reference-log.json")))
ev = ref["events"]
print("note:", ref["note"])
print("n events", len(ev))
types = {}
for e in ev:
    types[e["type"]] = types.get(e["type"], 0) + 1
print("types:", types)

for e in ev:
    if e["type"] in ("bump", "look", "talk", "transition", "cell_change", "checkpoint", "win", "shop", "prompt"):
        print(json.dumps(e)[:300])

print("---- checkpoints")
for e in ev:
    if e["type"] == "checkpoint":
        st = e["state"]
        print(e["name"], "loc", st.get("location"), "x", st.get("x"), "y", st.get("y"),
              "steps", st.get("steps"), "mode", st.get("mode"))
