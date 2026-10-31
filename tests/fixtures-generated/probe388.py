"""Probe: oracle map1 actionClass rows, and reference-log bump events."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TESTS = ROOT / "tests"
DD = TESTS / "fixtures-generated" / "dd3"

r = subprocess.run([sys.executable, str(TESTS / "oracle_tool.py"), "compiled", str(DD), str(ROOT / "SPEC" / "scenario")],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
m = d["oracle"]["map1"]
ac = m["cells"]["actionClass"]
img = m["cells"]["image"]
act = m["cells"]["action"]
for y in (20, 11):
    print("y", y)
    print("  class", ac[y])
    print("  image", img[y])
    print("  action", act[y])

ref = json.load(open(ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json"))["events"]
for e in ref:
    if e.get("type") in ("bump", "look", "move"):
        print(json.dumps(e, sort_keys=True))
