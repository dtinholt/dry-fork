"""Probe 213: ask the oracle what it sees in the compiled map1 row 20."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump213.txt")
buf = []


def out(s=""):
    buf.append(str(s))


import wlengine.scenario as sc  # noqa: E402

d = tempfile.mkdtemp(prefix="probe213")
sc.compile(os.path.join(ROOT, "SPEC", "scenario"), d)

r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "oracle_tool.py"),
                    "compiled", d, os.path.join(ROOT, "SPEC", "scenario")],
                   capture_output=True, text=True)
out("rc %s" % r.returncode)
out("stderr %s" % r.stderr[-2000:])
try:
    data = json.loads(r.stdout)
except ValueError:
    out("stdout not json: %s" % r.stdout[:2000])
    data = {}

out("top keys: %s" % sorted(data.keys()))
out("oracle keys: %s" % sorted(data.get("oracle", {}).keys()))
out("errors: %s" % json.dumps(data.get("errors"))[:2000])

maps = data.get("oracle", {}).get("maps") or data.get("oracle", {}).get("map")
if maps:
    out("maps type %s" % type(maps))
    if isinstance(maps, dict):
        out("map keys %s" % sorted(maps.keys())[:10])
        m1 = maps.get("1") or maps.get(1)
    else:
        m1 = maps[1] if len(maps) > 1 else maps[0]
    if m1:
        out("m1 keys %s" % sorted(m1.keys()))
        for key in ("actionClass", "action_class", "cells"):
            if key in m1:
                out("%s: %s" % (key, json.dumps(m1[key])[:600]))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
