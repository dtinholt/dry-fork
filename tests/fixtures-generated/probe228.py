"""Probe 228: map1 row 20 (tiles + action classes) and the reference log bumps."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "dump228.txt"
SC = ROOT / "SPEC" / "scenario"

with OUT.open("w") as f:
    m = json.loads((SC / "map1-saltwell.json").read_text())
    f.write("keys=%s\n" % list(m.keys()))
    for k in ("tiles", "action_class", "action", "image"):
        if k in m:
            f.write("%s row20=%s\n" % (k, m[k][20]))
    cells = m.get("cells")
    if isinstance(cells, dict):
        f.write("cells keys=%s\n" % list(cells.keys()))
        for k in ("tile", "actionClass", "action", "image"):
            if k in cells:
                f.write("cells.%s row20=%s\n" % (k, cells[k][20]))
    ref = json.loads((SC / "walkthrough-reference-log.json").read_text())["events"]
    f.write("\n--- reference bumps ---\n")
    for e in ref:
        if e.get("type") == "bump":
            f.write(json.dumps(e) + "\n")
print("wrote", OUT)
