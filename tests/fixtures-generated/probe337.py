"""Probe 337: dump headless.py key dispatch + Saltwell map around the cactus.

Writes tests/fixtures-generated/dump337.txt with every line of headless.py that
looks like key dispatch / movement / bump / look handling, plus a few map and
reference-log facts for the M5 bump test.
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
(ROOT / "tests" / "fixtures-generated" / "dump337.txt").write_text("\n".join(out))
print("wrote dump337.txt with %d lines" % len(out))

scen = ROOT / "SPEC" / "scenario"
m1 = json.loads((scen / "map1-saltwell.json").read_text())
tiles = m1["tiles"]
ac = m1["action_class"]
print("tiles[20][0:8] =", tiles[20][0:8])
print("ac[20][0:8]    =", ac[20][0:8])
print("tiles[2][18:24] =", tiles[2][18:24])
print("tiles[3][18:24] =", tiles[3][18:24])
print("ac[2][18:24]    =", ac[2][18:24])
print("ac[3][18:24]    =", ac[3][18:24])

wt = json.loads((scen / "walkthrough.json").read_text())
print("walkthrough keys:", sorted(wt.keys()))
print("walkthrough script[:6]:", wt.get("script", [])[:6])

ref = json.loads((ROOT / "SPEC" / "reference-log.json").read_text()) if (ROOT / "SPEC" / "reference-log.json").is_file() else None
if ref is None:
    cands = list((ROOT / "SPEC").glob("*reference*"))
    print("reference candidates:", [str(c) for c in cands])
    if cands:
        ref = json.loads(cands[0].read_text())
if ref is not None:
    evs = ref["events"] if isinstance(ref, dict) else ref
    bumps = [e for e in evs if e.get("type") == "bump"]
    print("reference bumps:", bumps[:6])
    looks = [e for e in evs if e.get("type") == "look"]
    print("reference looks:", looks[:6])
