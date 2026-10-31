"""Probe 242: compile the scenario, dump compiled map1 row 20, and run the
bump script to see the actual events."""
import json
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
OUT = pathlib.Path(__file__).resolve().parent

from wlengine import scenario, headless, maps  # noqa: E402

tmp = pathlib.Path(tempfile.mkdtemp())
scenario.compile(str(ROOT / "SPEC" / "scenario"), str(tmp))

lines = []
sc = scenario.load(str(tmp))
m = sc.map(1)
lines.append("map keys: %s" % sorted(m.keys()))
lines.append("map repr: %s" % json.dumps({k: v for k, v in m.items() if not isinstance(v, (list, dict))})[:500])
for k, v in m.items():
    if isinstance(v, list) and v and isinstance(v[0], list):
        lines.append("%s row20[:8] = %s" % (k, v[20][:8]))
    elif isinstance(v, list):
        lines.append("%s = %s" % (k, v[:8]))
lines.append("passable(3,20)=%s passable(2,20)=%s" % (maps.is_passable(m, 3, 20), maps.is_passable(m, 2, 20)))
lines.append("record_at(3,20)=%r" % (maps.record_at(m, 3, 20),))
lines.append("record_at(2,20)=%r" % (maps.record_at(m, 2, 20),))

ev = headless.run(str(tmp), {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
lines.append("")
lines.append("events:")
for e in ev:
    lines.append(json.dumps(e)[:300])

(OUT / "dump246.txt").write_text("\n".join(lines))
print("ok", tmp)
