"""Probe: run the bump script and dump the events, plus the map cells around
(2..5, 20) on location 1, and the start position."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

SEED = 20261021

out = []
d = Path(tempfile.mkdtemp(prefix="probe174-"))
W.engine_ready()
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)
out.append("compiled to %s" % d)

ev = W.call("headless.run", str(d), {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, None)
for e in ev:
    out.append(json.dumps(e, sort_keys=True)[:400])

# map cells
from wlengine import scenario as SC  # noqa: E402
sc = SC.load(str(d))
out.append("start: %r" % (sc.start,))
m = sc.map(1)
out.append("size %r info %r" % (m["size"], m["info"]))
for y in range(18, 23):
    row = []
    for x in range(0, 8):
        row.append("%d/%d" % (m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x]))
    out.append("y=%d %s" % (y, " ".join(row)))

Path(__file__).with_name("dump174.txt").write_text("\n".join(out))
print("wrote dump174.txt")
