"""Probe 247: oracle's decoded map1 cells vs the engine's scenario.load."""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
OUT = pathlib.Path(__file__).resolve().parent

from wlengine import scenario  # noqa: E402

tmp = pathlib.Path(tempfile.mkdtemp())
scenario.compile(str(ROOT / "SPEC" / "scenario"), str(tmp))

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(tmp),
                    str(ROOT / "SPEC" / "scenario")], capture_output=True, text=True)
data = json.loads(r.stdout)
m1 = data["oracle"]["map1"]
cells = m1["cells"]
out = []
out.append("oracle map1 cells keys: %s" % sorted(cells.keys()))
for k, v in cells.items():
    out.append("oracle cells[%s] row20[:8] = %s" % (k, v[20][:8]))
out.append("oracle map1 actions: %s" % json.dumps(m1["actions"])[:800])
out.append("oracle map1 info: %s" % json.dumps(m1["info"])[:400])

sc = scenario.load(str(tmp))
m = sc.map(1)
out.append("")
out.append("engine cells row20[:8]:")
for k, v in m["cells"].items():
    out.append("engine cells[%s] row20[:8] = %s" % (k, v[20][:8]))
out.append("engine actions: %s" % json.dumps(m["actions"])[:800])
out.append("engine info: %s" % json.dumps(m["info"])[:400])

# also compare all rows
for k in cells:
    if k in m["cells"]:
        diffs = []
        for y in range(32):
            if list(cells[k][y]) != list(m["cells"][k][y]):
                diffs.append((y, cells[k][y], m["cells"][k][y]))
        out.append("cells[%s] diffs: %d" % (k, len(diffs)))
        for d in diffs[:5]:
            out.append("   y=%d oracle=%s engine=%s" % d)

(OUT / "dump251.txt").write_text("\n".join(out))
print("ok")
