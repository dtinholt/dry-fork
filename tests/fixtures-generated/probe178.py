"""Focused: tile/class diffs between compiled and JSON maps; reference log
segments around the cot bump and the pump bump."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

out = []
d = Path(tempfile.mkdtemp(prefix="probe178-"))
W.engine_ready()
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)

from wlengine import scenario as SC  # noqa: E402
sc = SC.load(str(d))

names = ["overworld", "saltwell", "ninemile", "pumphouse"]
for loc in range(4):
    m = sc.map(loc)
    ac = m["cells"]["actionClass"]
    av = m["cells"]["action"]
    tiles = m["cells"]["image"]
    j = json.loads((ROOT / "SPEC" / "scenario" / ("map%d-%s.json" % (loc, names[loc]))).read_text())
    jac, jt, jav = j["action_class"], j["tiles"], j["action_value"]
    n = m["size"]
    td = [(x, y, tiles[y][x], jt[y][x]) for y in range(n) for x in range(n) if tiles[y][x] != jt[y][x]]
    cd = [(x, y, ac[y][x], jac[y][x]) for y in range(n) for x in range(n) if ac[y][x] != jac[y][x]]
    ad = [(x, y, av[y][x], jav[y][x]) for y in range(n) for x in range(n) if av[y][x] != jav[y][x]]
    out.append("loc %d: tile diffs %d %r" % (loc, len(td), td[:12]))
    out.append("loc %d: class diffs %d %r" % (loc, len(cd), cd[:12]))
    out.append("loc %d: action diffs %d %r" % (loc, len(ad), ad[:12]))
    # class 11 cells in compiled vs json
    c11 = sorted((x, y) for y in range(n) for x in range(n) if ac[y][x] == 11)
    j11 = sorted((x, y) for y in range(n) for x in range(n) if jac[y][x] == 11)
    out.append("loc %d: class11 only-compiled %r only-json %r" % (loc, sorted(set(c11) - set(j11))[:20], sorted(set(j11) - set(c11))[:20]))

ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]
for lo, hi in [(596, 612), (1010, 1022), (120, 135), (555, 570)]:
    out.append("=== reference log %d..%d ===" % (lo, hi))
    for i in range(lo, min(hi + 1, len(ref))):
        out.append("%4d %s" % (i, json.dumps(ref[i], sort_keys=True)[:260]))

Path(__file__).with_name("dump178.txt").write_text("\n".join(out))
print("wrote dump178.txt")
