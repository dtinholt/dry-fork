"""probe235: compile the scenario, dump compiled map1 row 20, run the bump script."""
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

OUT = []
import wlengine.scenario as sc  # noqa: E402
import wlengine.headless as hl  # noqa: E402

d = pathlib.Path(tempfile.mkdtemp())
sc.compile(str(ROOT / "SPEC/scenario"), str(d))
OUT.append("compiled files: %s" % sorted(p.name for p in d.iterdir()))

g = (d / "GAME1").read_bytes()
OUT.append("GAME1 size %d" % len(g))

ev = hl.run(str(d), json.loads(json.dumps({"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})), None)
for e in ev:
    OUT.append(json.dumps(e)[:400])

import wlengine.maps as maps  # noqa: E402
try:
    m = maps.read_map(str(d / "GAME1"), 1)
    OUT.append("map keys: %s" % sorted(m.keys()))
    for k in ("tiles", "action_class", "action_value", "action"):
        if k in m:
            OUT.append("%s row20: %s" % (k, m[k][20]))
            OUT.append("%s row17: %s" % (k, m[k][17]))
except Exception as e:  # noqa: BLE001
    OUT.append("read_map failed: %s: %s" % (type(e).__name__, e))

(ROOT / "tests/fixtures-generated/dump235.txt").write_text("\n".join(OUT))
print("ok")
