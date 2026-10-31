"""Probe: oracle images at (14,20) for all maps; map JSON conventions."""
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
for loc in range(4):
    m = d["oracle"]["map%d" % loc]
    img = m["cells"]["image"]
    ac = m["cells"]["actionClass"]
    print("map%d" % loc, "img(14,20)=", img[20][14], "img(15,20)=", img[20][15],
          "cls(14,20)=", ac[20][14], "cls(15,20)=", ac[20][15])
    print("   row20 img:", img[20])

for loc in range(4):
    j = json.load(open(ROOT / "SPEC" / "scenario" / ("map%d-%s.json" % (loc, ["overworld", "saltwell", "ninemile", "pumphouse"][loc]))))
    print("json map%d" % loc, "tiles(14,20)=", j["tiles"][20][14], "tiles(15,20)=", j["tiles"][20][15])
    print("   conventions:", json.dumps(j.get("conventions"))[:300])
    print("   info:", json.dumps(j.get("info"))[:300])
