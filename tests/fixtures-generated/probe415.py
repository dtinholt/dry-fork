"""Probe 415: compare map1-saltwell.json cells with the compiled map cells."""
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path("src").resolve()))
sys.path.insert(0, str(pathlib.Path("tests").resolve()))

import wlengine.scenario as S  # noqa: E402

SCEN = pathlib.Path("SPEC/scenario")
OUT = pathlib.Path("tests/fixtures-generated/dump415.txt")
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
ac = m1["action_class"]
av = m1["action_value"]
tl = m1["tiles"]
p("action_class rows 18..22:")
for y in range(18, 23):
    p(" y=%2d" % y, ac[y])
p("action_value rows 18..22:")
for y in range(18, 23):
    p(" y=%2d" % y, av[y])
p("tiles rows 18..22:")
for y in range(18, 23):
    p(" y=%2d" % y, tl[y])
p("action_cells:", json.dumps(m1["action_cells"], indent=1))

dd = pathlib.Path(tempfile.mkdtemp(prefix="probe415-"))
S.compile(str(SCEN), str(dd))
p("compiled dir", dd)
files = sorted(x.name for x in dd.iterdir())
p("files:", files)
# find the compiled map file
for f in files:
    if "map" in f.lower() or f.endswith(".json"):
        p("---", f)
        try:
            d = json.loads((dd / f).read_text())
        except Exception as e:
            p("  not json:", e)
            continue
        if isinstance(d, dict) and "cells" in d:
            c = d["cells"]
            p("  keys", sorted(c.keys()))
            for y in range(18, 23):
                p("  y=%2d class" % y, c["actionClass"][y])
            for y in range(18, 23):
                p("  y=%2d image" % y, c["image"][y])
        elif isinstance(d, dict):
            p("  keys", sorted(d.keys())[:20])

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
