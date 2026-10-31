"""Probe 414: reproduce the M5 bump failure and the M6 look failure."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path("src").resolve()))
sys.path.insert(0, str(pathlib.Path("tests").resolve()))

import wlengine.headless as H  # noqa: E402
import wlengine.scenario as S  # noqa: E402

SCEN = pathlib.Path("SPEC/scenario")
OUT = pathlib.Path("tests/fixtures-generated/dump414.txt")
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


# compile the scenario into a temp dir
import tempfile
dd = pathlib.Path(tempfile.mkdtemp(prefix="probe414-"))
try:
    S.compile(str(SCEN), str(dd))
except TypeError:
    S.compile(str(dd), str(SCEN))
p("compiled to", dd)

ev = H.run(str(dd), {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, 20261021)
for e in ev:
    p(json.dumps(e, sort_keys=True))

p("---- look ----")
ev2 = H.run(str(dd), {"seed": 20261021, "script": ["L", "LEFT", {"checkpoint": "a"}]}, 20261021)
for e in ev2:
    p(json.dumps(e, sort_keys=True))

p("---- map1 json cells around (14,20) ----")
m1 = json.loads((SCEN / "map1-saltwell.json").read_text())
p("keys:", sorted(m1.keys()))
p(json.dumps({k: v for k, v in m1.items() if k not in ("cells", "tiles", "image")}, indent=1)[:4000])
for k in ("cells", "image", "tiles", "tilemap"):
    if k in m1:
        p("has", k, type(m1[k]))

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
