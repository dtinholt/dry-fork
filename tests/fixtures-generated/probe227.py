"""Probe 227: dump the whole reference combat window (encounter_start..combat_end+20)
from SPEC/scenario/walkthrough-reference-log.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "dump227.txt"
SC = ROOT / "SPEC" / "scenario"

ref = json.loads((SC / "walkthrough-reference-log.json").read_text())["events"]
i = next(k for k, e in enumerate(ref) if e.get("type") == "encounter_start")
j = next(k for k in range(i, len(ref)) if ref[k].get("type") == "combat_end")
with OUT.open("w") as f:
    for e in ref[i:j + 25]:
        f.write(json.dumps(e)[:260] + "\n")
print("wrote", OUT)
