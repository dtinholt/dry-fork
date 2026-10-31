"""Probe 241: inspect SPEC/scenario/map1-saltwell.json row 20 and the
walkthrough script for the bump test."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent

d = json.loads((ROOT / "SPEC" / "scenario" / "map1-saltwell.json").read_text())
lines = []
lines.append("keys: %s" % sorted(d.keys()))
for k, v in d.items():
    if isinstance(v, list) and v and isinstance(v[0], list):
        lines.append("%s row20[:8] = %s" % (k, v[20][:8]))
    elif isinstance(v, list):
        lines.append("%s = %s" % (k, v[:8]))
    else:
        lines.append("%s = %r" % (k, v))

wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
lines.append("")
lines.append("walkthrough keys: %s" % sorted(wt.keys()))
lines.append(json.dumps(wt, indent=1)[:6000])

(OUT / "dump245.txt").write_text("\n".join(lines))
print("ok")
