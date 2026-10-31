"""Ask the reference oracle what the compiled map 1 cells are around (2..4,20),
and what the M3 tests assert about map cells."""
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
d = Path(tempfile.mkdtemp(prefix="probe180-"))
W.engine_ready()
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(d), str(W.SCENARIO)],
                   capture_output=True, text=True)
out.append("rc=%d stderr=%s" % (r.returncode, r.stderr[-500:]))
data = json.loads(r.stdout)
out.append("top keys %r" % (list(data.keys()),))
out.append("oracle keys %r" % (list(data.get("oracle", {}).keys()),))
out.append("errors %r" % (data.get("errors"),))

maps = data.get("oracle", {}).get("maps")
if maps is not None:
    out.append("maps type %s" % type(maps).__name__)
    if isinstance(maps, dict):
        out.append("maps keys %r" % (list(maps.keys()),))
        m1 = maps.get("1") or maps.get(1)
    else:
        m1 = maps[1] if len(maps) > 1 else maps[0]
    out.append("m1 keys %r" % (list(m1.keys()) if isinstance(m1, dict) else type(m1),))
    out.append(json.dumps(m1, indent=1)[:3000])

Path(__file__).with_name("dump180.txt").write_text("\n".join(out))
print("wrote dump180.txt")
