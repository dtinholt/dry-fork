"""probe233: compare map1-saltwell.json tiles/class with the SPEC-05 art."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
d = json.loads((ROOT / "SPEC/scenario/map1-saltwell.json").read_text())
OUT = []
for y in range(32):
    OUT.append("y=%2d tiles=%s" % (y, d["tiles"][y]))
    OUT.append("     class=%s" % (d["action_class"][y],))
    OUT.append("     value=%s" % (d["action_value"][y],))
OUT.append("action_cells=%s" % json.dumps(d["action_cells"], indent=1))
OUT.append("records=%s" % json.dumps(d["records"], indent=1))
OUT.append("info=%s" % json.dumps(d["info"], indent=1))
(ROOT / "tests/fixtures-generated/dump233.txt").write_text("\n".join(OUT))
print("ok")
