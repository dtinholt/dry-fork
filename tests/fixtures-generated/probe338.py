"""Probe 338: dump headless.py key dispatch + Saltwell map + reference log facts.

Writes tests/fixtures-generated/dump338.txt with every line of headless.py that
looks like key dispatch / movement / bump / look handling, plus map and
reference-log facts for the M5 bump test and the M6 look test.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "wlengine" / "headless.py"
lines = SRC.read_text().splitlines()

out = []
out.append("=== headless.py (%d lines) ===" % len(lines))
pat = re.compile(r"LEFT|RIGHT|UP|DOWN|\bkey\b|move|bump|look|def |class |elif|if ")
for i, l in enumerate(lines):
    if pat.search(l):
        out.append("%5d %s" % (i + 1, l))

out.append("")
out.append("=== maps.py key lines ===")
mlines = (ROOT / "src" / "wlengine" / "maps.py").read_text().splitlines()
for i, l in enumerate(mlines):
    if re.search(r"def |tiles|action_class|passab|walk|image", l):
        out.append("%5d %s" % (i + 1, l))

out.append("")
out.append("=== scenario.py key lines ===")
slines = (ROOT / "src" / "wlengine" / "scenario.py").read_text().splitlines()
for i, l in enumerate(slines):
    if re.search(r"def |tiles|action_class|passab|walk|image|look", l):
        out.append("%5d %s" % (i + 1, l))

(ROOT / "tests" / "fixtures-generated" / "dump338.txt").write_text("\n".join(out))
print("wrote dump338.txt with %d lines" % len(out))

scen = ROOT / "SPEC" / "scenario"
m1 = json.loads((scen / "map1-saltwell.json").read_text())
print("map1 keys:", sorted(m1.keys()))
tiles = m1["tiles"]
ac = m1["action_class"]
print("tiles[20][0:8] =", tiles[20][0:8])
print("ac[20][0:8]    =", ac[20][0:8])
print("tiles[2][18:24] =", tiles[2][18:24])
print("tiles[3][18:24] =", tiles[3][18:24])
print("ac[2][18:24]    =", ac[2][18:24])
print("ac[3][18:24]    =", ac[3][18:24])
print("tiles[20][14:18] =", tiles[20][14:18])
print("ac[20][14:18]    =", ac[20][14:18])

wt = json.loads((scen / "walkthrough.json").read_text())
print("walkthrough keys:", sorted(wt.keys()))
print("walkthrough script[:8]:", wt.get("script", [])[:8])

cands = sorted((ROOT / "SPEC").glob("*reference*"))
print("reference candidates:", [str(c) for c in cands])
if cands:
    ref = json.loads(cands[0].read_text())
    evs = ref["events"] if isinstance(ref, dict) else ref
    print("ref events:", len(evs))
    bumps = [e for e in evs if e.get("type") == "bump"]
    print("reference bumps:", bumps[:6])
    looks = [e for e in evs if e.get("type") == "look"]
    print("reference looks:", looks[:6])
    inputs = [e for e in evs if e.get("type") == "input"]
    print("reference inputs[:20]:", inputs[:20])
