"""Probe 214: oracle map1 action classes row 20 and the M5 bump test's runner."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump214.txt")
buf = []


def out(s=""):
    buf.append(str(s))


import wlengine.scenario as sc  # noqa: E402

d = tempfile.mkdtemp(prefix="probe214")
sc.compile(os.path.join(ROOT, "SPEC", "scenario"), d)
r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"),
                    "compiled", d, os.path.join(ROOT, "SPEC", "scenario")],
                   capture_output=True, text=True)
data = json.loads(r.stdout)
m1 = data["oracle"]["map1"]
out("map1 keys %s" % sorted(m1.keys()))
out(json.dumps(m1)[:3000])

out("=== conftest runner ===")
src = open(os.path.join(ROOT, "tests", "conftest.py")).read().split("\n")
for i, l in enumerate(src):
    if "def runner" in l or "def _saved" in l:
        for j in range(i, min(len(src), i + 30)):
            out("conftest:%d: %s" % (j + 1, src[j]))
        out("---")

out("=== test_m5_rules _saved / _fight / prefix ===")
src = open(os.path.join(ROOT, "tests", "test_m5_rules.py")).read().split("\n")
for i, l in enumerate(src):
    if l.startswith("def _saved") or l.startswith("def _fight") or l.startswith("def prefix") or l.startswith("def _payload"):
        for j in range(i, min(len(src), i + 25)):
            out("m5:%d: %s" % (j + 1, src[j]))
        out("---")

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
