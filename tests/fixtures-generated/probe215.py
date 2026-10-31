"""Probe 215: the cactus row, the engine run, and the oracle's expected row."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump215.txt")
buf = []


def out(s=""):
    buf.append(str(s))


# 1. SPEC art row 20
ls = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")).read().split("\n")
for i, l in enumerate(ls):
    if l.startswith(" 20  |"):
        art = l[5:]
        out("SPEC art row20: %r" % art)
        out("indices: %s" % "".join(str(j % 10) for j in range(len(art))))
        out("chars:   %s" % art)

# 2. JSON row 20
m = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
out("JSON action_class[20]: %s" % m["action_class"][20])
out("JSON tiles[20]:        %s" % m["tiles"][20])

# 3. engine compile
import wlengine.scenario as sc  # noqa: E402

d = tempfile.mkdtemp(prefix="probe215")
sc.compile(os.path.join(ROOT, "SPEC", "scenario"), d)
s = sc.load(d)
mm = s.map(1)
out("engine actionClass[20]: %s" % mm["cells"]["actionClass"][20])
out("engine image[20]:       %s" % mm["cells"]["image"][20])

# 4. oracle expected
r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"),
                    "compiled", d, os.path.join(ROOT, "SPEC", "scenario")],
                   capture_output=True, text=True)
data = json.loads(r.stdout)
out("oracle actionClass[20]: %s" % data["oracle"]["map1"]["cells"]["actionClass"][20])

# 5. run the headless engine
import shutil  # noqa: E402
import wlengine.headless as hl  # noqa: E402

dd = tempfile.mkdtemp(prefix="probe215run")
shutil.copytree(d, dd, dirs_exist_ok=True)
ev = hl.run(dd, {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
for e in ev:
    out(json.dumps(e))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
