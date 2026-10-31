"""Dump the oracle's map1 view: cells around (2..4,20) and the action records."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

out = []
d = Path(tempfile.mkdtemp(prefix="probe181-"))
W.engine_ready()
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(d), str(W.SCENARIO)],
                   capture_output=True, text=True)
data = json.loads(r.stdout)
m1 = data["oracle"]["map1"]
out.append("map1 keys %r" % (list(m1.keys()),))
for k, v in m1.items():
    if isinstance(v, list) and v and isinstance(v[0], list):
        out.append("%s: %dx%d" % (k, len(v), len(v[0])))
        for y in range(18, 23):
            out.append("   y=%2d %r" % (y, v[y][:8]))
    else:
        out.append("%s = %s" % (k, json.dumps(v)[:400]))

Path(__file__).with_name("dump181.txt").write_text("\n".join(out))
print("wrote dump181.txt")
