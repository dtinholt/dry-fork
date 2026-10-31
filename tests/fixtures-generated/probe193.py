"""Probe 193: compiled map1 cells, fight for seed 3, test_m5 fight section."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump193.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


SC = os.path.join(ROOT, "SPEC", "scenario")
from wlengine import scenario as scmod  # noqa: E402
from wlengine import headless as hl  # noqa: E402
from wlengine import maps as mapsmod  # noqa: E402

d = tempfile.mkdtemp()
scmod.compile(SC, d)
m = mapsmod.load_map(d, 1)
p("compiled map keys: %r" % list(m))
p("size %r" % m.get("size"))
cells = m["cells"]
p("cells keys: %r" % list(cells))
for y in (19, 20, 21):
    for k in cells:
        p("cells[%s][%d] = %r" % (k, y, cells[k][y]))
p("info: %r" % json.dumps(m.get("info"), sort_keys=True))
p("records: %r" % json.dumps(m.get("records"), sort_keys=True)[:1500])

# fight for seed 3
wt = json.load(open(os.path.join(SC, "walkthrough.json"), encoding="utf-8"))
script = wt["script"]
idx4 = next(i for i, it in enumerate(script) if isinstance(it, dict) and it.get("checkpoint") == "CP4")
for seed in (3, 20261021):
    d2 = tempfile.mkdtemp()
    scmod.compile(SC, d2)
    ev = hl.run(d2, {"seed": seed, "script": script[:idx4 + 1]}, seed)
    p("=" * 70)
    p("FIGHT seed %d" % seed)
    for e in ev:
        if e.get("type") in ("encounter_start", "round_orders", "round_start", "attack", "jam", "click",
                             "monster_dies", "advance", "group_closes", "reload", "unjammed", "combat_end",
                             "xp", "promote", "money", "cell_change", "check", "paragraph"):
            p(json.dumps(e, sort_keys=True)[:300])

# test_m5 fight section
txt = open(os.path.join(ROOT, "tests", "test_m5_rules.py"), encoding="latin-1").read()
i = txt.find("FIGHT_SEEDS")
p("=" * 70)
p("test_m5_rules.py from FIGHT_SEEDS")
p(txt[max(0, i - 3000):i + 3000])

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
