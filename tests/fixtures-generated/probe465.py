"""probe465: reference-log context around the bumps, to learn the reference
implementation's map coordinates.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ev = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]

for seq in (127, 603, 1018, 562):
    print("=== around seq %d ===" % seq)
    for e in ev:
        if seq - 6 <= e["seq"] <= seq + 3:
            print(" ", e)
    print()

print("=== all moves with y==20 ===")
for e in ev:
    if e.get("type") == "move" and e.get("y") == 20:
        print(e)
print("=== all moves with y==21 ===")
for e in ev:
    if e.get("type") == "move" and e.get("y") == 21:
        print(e)
print("=== all moves with y==11 ===")
for e in ev:
    if e.get("type") == "move" and e.get("y") == 11:
        print(e)
print("=== all moves with y==17 ===")
for e in ev:
    if e.get("type") == "move" and e.get("y") == 17:
        print(e)
