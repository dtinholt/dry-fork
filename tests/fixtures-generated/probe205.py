"""Probe 205: full code of combat.py head, headless.py head, premade_party,
map1 row 20, and our engine's fight events for seed 3."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump205.txt")
buf = []


def out(s=""):
    buf.append(str(s))


def lines(path, a, b):
    full = os.path.join(ROOT, path)
    ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
    out("=== %s lines %d..%d ===" % (path, a, b))
    for i in range(a - 1, min(b, len(ls))):
        out("%d: %s" % (i + 1, ls[i]))


lines("src/wlengine/combat.py", 1, 130)
lines("src/wlengine/headless.py", 42, 170)

# premade_party
full = os.path.join(ROOT, "src/wlengine/scenario.py")
ls = open(full, encoding="utf-8", errors="replace").read().split("\n")
for i, l in enumerate(ls):
    if "premade_party" in l or "def _party_from_json" in l:
        out("=== scenario.py %d ===" % (i + 1))
        out("\n".join("%d: %s" % (j + 1, ls[j]) for j in range(i, min(len(ls), i + 45))))
        break

m1 = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "map1-saltwell.json")))
out("=== map1 keys: %s" % list(m1))
out("tiles row 20: %s" % m1["tiles"][20])
out("action_class row 20: %s" % m1["action_class"][20])
out("action_value row 20: %s" % m1["action_value"][20])
out("tiles row 19: %s" % m1["tiles"][19])
out("action_class row 19: %s" % m1["action_class"][19])
out("records: %s" % json.dumps(m1.get("records"))[:1500])
out("start: %s" % json.dumps(m1.get("start")))

# our engine fight events for seed 3
from wlengine import headless  # noqa: E402

dd = os.path.join(ROOT, "tests", "fixtures-generated", "dd")
wt = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough.json")))
out("=== walkthrough keys: %s" % list(wt))


def prefix(wt, name):
    steps = wt.get("steps") or wt.get("script") or []
    out_ = []
    for s in steps:
        if isinstance(s, dict) and s.get("checkpoint") == name:
            break
        out_.append(s)
    return out_


try:
    ev, dd2 = headless.run("cp4", {"seed": 3, "script": prefix(wt, "CP4")}, 3, data_dir=dd)
    out("=== our events seed 3 (fight window) ===")
    start = next(i for i, e in enumerate(ev) if e.get("type") == "encounter_start")
    for i in range(start - 2, min(len(ev), start + 60)):
        out("%d: %s" % (i, json.dumps(ev[i])[:400]))
except Exception as exc:  # noqa: BLE001
    import traceback
    out("RUN FAILED: %s" % exc)
    out(traceback.format_exc())

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
