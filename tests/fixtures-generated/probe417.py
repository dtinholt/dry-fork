"""Probe 417: decode the compiled GAME1 with the oracle and compare tiles."""
import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path("src").resolve()))
sys.path.insert(0, str(pathlib.Path("tests").resolve()))

import wlengine.scenario as S  # noqa: E402

SCEN = pathlib.Path("SPEC/scenario")
OUT = pathlib.Path("tests/fixtures-generated/dump417.txt")
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


dd = pathlib.Path(tempfile.mkdtemp(prefix="probe417-"))
S.compile(str(SCEN), str(dd))
p("compiled dir", dd)

r = subprocess.run([sys.executable, "tests/oracle_tool.py", "compiled", str(dd), str(SCEN)],
                   capture_output=True, text=True)
p("rc", r.returncode)
if r.returncode != 0:
    p(r.stdout[:2000], r.stderr[:2000])
else:
    d = json.loads(r.stdout)
    p("errors:", json.dumps(d.get("errors")))
    o = d["oracle"]
    p("oracle keys:", sorted(o.keys()))
    m1 = o.get("map1")
    if m1:
        p("map1 keys:", sorted(m1.keys()))
        for k in sorted(m1.keys()):
            v = m1[k]
            if isinstance(v, list) and v and isinstance(v[0], list):
                p("  %s rows=%d cols=%d" % (k, len(v), len(v[0])))
            else:
                p("  %s = %s" % (k, str(v)[:200]))
        for k in ("tiles", "tileMap", "image", "images"):
            if k in m1:
                p("  %s y=20: %s" % (k, m1[k][20]))
                p("  %s y=14: %s" % (k, m1[k][14]))
    p("expected keys:", sorted(d["expected"].keys()))

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
