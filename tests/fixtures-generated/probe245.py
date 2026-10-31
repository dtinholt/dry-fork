"""Probe 245: exact bytes of the SPEC-05 Saltwell art, scenario start, the
reference log around y=20, and the bump test source."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent

out = []

txt = (ROOT / "SPEC" / "SPEC-05-scenario.md").read_text().splitlines()
for i, ln in enumerate(txt):
    if re.match(r"^\s+20\s+\|", ln):
        for j in range(i - 2, i + 3):
            out.append("art[%d] = %r" % (j, txt[j]))
        break

sc = json.loads((ROOT / "SPEC" / "scenario" / "scenario.json").read_text())
out.append("")
out.append("scenario.json: %s" % json.dumps(sc)[:1500])

out.append("")
out.append("test_m5_rules.py 505-525:")
tl = (ROOT / "tests" / "test_m5_rules.py").read_text().splitlines()
for j in range(504, 525):
    out.append("%4d %r" % (j + 1, tl[j]))

out.append("")
out.append("test_m5_rules.py SEED / imports:")
for j, ln in enumerate(tl[:40]):
    out.append("%4d %s" % (j + 1, ln))

ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())
ev = ref["events"]
out.append("")
out.append("reflog events with y==20:")
for e in ev:
    if e.get("y") == 20:
        out.append(json.dumps(e))
out.append("")
out.append("reflog first 30 events:")
for e in ev[:30]:
    out.append(json.dumps(e))
out.append("")
out.append("reflog bumps:")
for e in ev:
    if e.get("type") == "bump":
        out.append(json.dumps(e))

(OUT / "dump249.txt").write_text("\n".join(out))
print("ok")
