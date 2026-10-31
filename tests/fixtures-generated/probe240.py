"""Probe 240: gather the data needed for the M5 fixes.

Writes:
  dump240.txt  - conftest runner fixture, headless bump handling, map row 20
  dump241.txt  - full src/wlengine/combat.py
  dump242.txt  - full tests/wl_combat_ref.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent


def dump(name, text):
    (OUT / name).write_text(text)
    print("wrote", name, len(text.splitlines()), "lines")


# ---- 1. conftest.py -------------------------------------------------------
conf = (ROOT / "tests" / "conftest.py").read_text()
dump("dump240.txt", "=== tests/conftest.py ===\n" + conf)

# ---- 2. headless.py: bump / move handling --------------------------------
hl = (ROOT / "src" / "wlengine" / "headless.py").read_text().splitlines()
keep = []
for i, line in enumerate(hl):
    if re.search(r"bump|def move|steps|class_11|action_class", line):
        keep.append(i)
sel = set()
for i in keep:
    for j in range(max(0, i - 3), min(len(hl), i + 4)):
        sel.add(j)
body = "\n".join("%4d %s" % (j + 1, hl[j]) for j in sorted(sel))
with open(OUT / "dump240.txt", "a") as fh:
    fh.write("\n\n=== src/wlengine/headless.py (bump/move/steps context) ===\n")
    fh.write(body)

# ---- 3. map1-saltwell.json row 20 ----------------------------------------
mp = ROOT / "tests" / "fixtures-generated" / "map1-saltwell.json"
with open(OUT / "dump240.txt", "a") as fh:
    fh.write("\n\n=== map1-saltwell.json ===\n")
    fh.write("exists: %s\n" % mp.exists())
    if mp.exists():
        d = json.loads(mp.read_text())
        fh.write("keys: %s\n" % sorted(d.keys()))
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], list):
                fh.write("%s row20[:10] = %s\n" % (k, v[20][:10]))
                fh.write("%s row20[10:20] = %s\n" % (k, v[20][10:20]))
            elif isinstance(v, list):
                fh.write("%s = %s\n" % (k, v[:20]))

# ---- 4. combat.py --------------------------------------------------------
dump("dump241.txt", (ROOT / "src" / "wlengine" / "combat.py").read_text())

# ---- 5. wl_combat_ref.py -------------------------------------------------
dump("dump242.txt", (ROOT / "tests" / "wl_combat_ref.py").read_text())

# ---- 6. test_m5_rules.py -------------------------------------------------
dump("dump243.txt", (ROOT / "tests" / "test_m5_rules.py").read_text())

# ---- 7. wl_support.py ----------------------------------------------------
dump("dump244.txt", (ROOT / "tests" / "wl_support.py").read_text())
