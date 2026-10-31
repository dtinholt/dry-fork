"""Compare the compiled maps with the SPEC/scenario JSON: class-11 cells and
tiles, per location. Also dump the reference log around the cot bump."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

out = []
d = Path(tempfile.mkdtemp(prefix="probe177-"))
W.engine_ready()
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)

from wlengine import scenario as SC  # noqa: E402
sc = SC.load(str(d))

for loc in range(4):
    m = sc.map(loc)
    ac = m["cells"]["actionClass"]
    av = m["cells"]["action"]
    tiles = m["cells"]["image"]
    pos11 = sorted((x, y) for y in range(m["size"]) for x in range(m["size"]) if ac[y][x] == 11)
    out.append("loc %d size %d class11 %r" % (loc, m["size"], pos11))
    out.append("   tiles at those: %r" % ([(x, y, tiles[y][x]) for x, y in pos11],))
    out.append("   actions: %r" % ([(x, y, av[y][x]) for x, y in pos11],))

    j = json.loads((ROOT / "SPEC" / "scenario" / ("map%d-%s.json" % (loc, ["overworld", "saltwell", "ninemile", "pumphouse"][loc]))).read_text())
    jac = j["action_class"]
    jt = j["tiles"]
    jpos = sorted((x, y) for y in range(len(jac)) for x in range(len(jac[y])) if jac[y][x] == 11)
    out.append("   JSON class11 %r" % (jpos,))
    out.append("   JSON tiles there %r" % ([(x, y, jt[y][x]) for x, y in jpos],))
    # diff of tiles
    diffs = [(x, y, tiles[y][x], jt[y][x]) for y in range(m["size"]) for x in range(m["size"]) if tiles[y][x] != jt[y][x]]
    out.append("   tile diffs (compiled, json): %r" % (diffs[:20],))
    diffs = [(x, y, ac[y][x], jac[y][x]) for y in range(m["size"]) for x in range(m["size"]) if ac[y][x] != jac[y][x]]
    out.append("   class diffs: %r" % (diffs[:20],))

ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]
out.append("=== reference log 590..630 ===")
for i, e in enumerate(ref):
    if 590 <= i <= 632:
        out.append("%4d %s" % (i, json.dumps(e, sort_keys=True)[:220]))
out.append("=== reference log 995..1022 ===")
for i, e in enumerate(ref):
    if 995 <= i <= 1021:
        out.append("%4d %s" % (i, json.dumps(e, sort_keys=True)[:220]))

Path(__file__).with_name("dump177.txt").write_text("\n".join(out))
print("wrote dump177.txt")
