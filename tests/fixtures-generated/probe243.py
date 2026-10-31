"""Probe 243: compare SPEC/scenario/map1-saltwell.json rows with the SPEC-05
art, and dump the compiled map cells for the same rows."""
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
OUT = pathlib.Path(__file__).resolve().parent

from wlengine import scenario  # noqa: E402

d = json.loads((ROOT / "SPEC" / "scenario" / "map1-saltwell.json").read_text())
lines = []
for y in (0, 6, 11, 12, 20, 21, 29, 31):
    lines.append("y=%2d tiles      = %s" % (y, d["tiles"][y]))
    lines.append("y=%2d action_cls = %s" % (y, d["action_class"][y]))
    lines.append("y=%2d action_val = %s" % (y, d["action_value"][y]))

tmp = pathlib.Path(tempfile.mkdtemp())
scenario.compile(str(ROOT / "SPEC" / "scenario"), str(tmp))
sc = scenario.load(str(tmp))
m = sc.map(1)
lines.append("")
lines.append("compiled cells type: %s" % type(m["cells"]))
cells = m["cells"]
if isinstance(cells, list) and cells and isinstance(cells[0], list):
    for y in (0, 6, 11, 12, 20, 21, 29, 31):
        lines.append("compiled y=%2d = %s" % (y, cells[y]))
elif isinstance(cells, dict):
    lines.append("cells keys: %s" % list(cells.keys())[:5])
    lines.append(json.dumps(cells)[:2000])
lines.append("")
lines.append("actions: %s" % json.dumps(m["actions"])[:2000])

(OUT / "dump247.txt").write_text("\n".join(lines))
print("ok")
