"""Print the oracle's compiled map1 actionClass/action rows 18..22 in full."""
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
d = Path(tempfile.mkdtemp(prefix="probe182-"))
W.engine_ready()
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(d), str(W.SCENARIO)],
                   capture_output=True, text=True)
data = json.loads(r.stdout)
cells = data["oracle"]["map1"]["cells"]
out.append("cells keys %r" % (list(cells.keys()),))
for k, v in cells.items():
    out.append("--- %s" % k)
    for y in range(18, 23):
        out.append("   y=%2d %r" % (y, v[y]))

Path(__file__).with_name("dump182.txt").write_text("\n".join(out))
print("wrote dump182.txt")
