"""probe232: dump the pieces needed for the M5 fixes (bump, orders, labstate)."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
T = ROOT / "tests"
SPEC = ROOT / "SPEC"
OUT = []


def show(title, text, maxlines=None):
    OUT.append("=" * 25 + " " + title)
    ls = text.splitlines()
    if maxlines:
        ls = ls[:maxlines]
    OUT.extend(ls)


ref = T / "wl_combat_ref.py"
txt = ref.read_text()
show("wl_combat_ref.py lines 240-346", "\n".join(txt.splitlines()[239:]), None)

cf = T / "conftest.py"
txt = cf.read_text()
show("conftest.py", txt, 300)

for cand in (SPEC / "scenario", SPEC):
    if cand.is_dir():
        OUT.append("SCENARIO DIR %s: %s" % (cand, sorted(x.name for x in cand.iterdir())[:60]))

mj = None
for p in ROOT.rglob("map1-saltwell.json"):
    mj = p
    break
OUT.append("map1-saltwell.json at %s" % mj)
if mj:
    d = json.loads(mj.read_text())
    OUT.append("keys: %s" % sorted(d.keys()))
    for key in ("tiles", "action_class", "action", "image"):
        if key in d:
            OUT.append("%s row20: %s" % (key, d[key][20][:8]))

for p in SPEC.rglob("SPEC-05*.md"):
    txt = p.read_text()
    for i, line in enumerate(txt.splitlines()):
        if "cactus" in line.lower():
            OUT.append("SPEC-05 line %d: %s" % (i + 1, line))
    idx = txt.find("5.2 Saltwell")
    if idx >= 0:
        show("SPEC-05 5.2 Saltwell", txt[idx:idx + 3500])

pathlib.Path(__file__).with_name("dump232.txt").write_text("\n".join(OUT))
print("wrote dump232.txt", len(OUT), "lines")
