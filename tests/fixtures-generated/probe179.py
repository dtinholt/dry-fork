"""Run the SPEC-05 walkthrough through our engine and diff every checkpoint
against the reference log."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

out = []
d = Path(tempfile.mkdtemp(prefix="probe179-"))
W.engine_ready()
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)

wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())["events"]

script = wt["script"]
ev = W.call("headless.run", str(d), {"seed": wt["seed"], "script": script}, None)
out.append("our events: %d, reference: %d" % (len(ev), len(ref)))

refck = {e["name"]: e["state"] for e in ref if e.get("type") == "checkpoint"}
ourck = {e["name"]: e["state"] for e in ev if e.get("type") == "checkpoint"}
out.append("ref checkpoints %r" % (sorted(refck),))
out.append("our checkpoints %r" % (sorted(ourck),))

for name in sorted(refck):
    if name not in ourck:
        out.append("=== %s: MISSING in ours" % name)
        continue
    a, b = ourck[name], refck[name]
    diffs = []
    for k in sorted(set(a) | set(b)):
        if k == "party":
            continue
        if a.get(k) != b.get(k):
            diffs.append("%s: ours=%r ref=%r" % (k, a.get(k), b.get(k)))
    out.append("=== %s: %d field diffs" % (name, len(diffs)))
    for x in diffs:
        out.append("    " + x[:600])
    # party diff
    pa, pb = a.get("party") or [], b.get("party") or []
    if len(pa) != len(pb):
        out.append("    party len ours=%d ref=%d" % (len(pa), len(pb)))
    for i in range(min(len(pa), len(pb))):
        for k in sorted(set(pa[i]) | set(pb[i])):
            if pa[i].get(k) != pb[i].get(k):
                out.append("    party[%d].%s ours=%r ref=%r" % (i, k, pa[i].get(k), pb[i].get(k)))

# first event-level divergence
n = min(len(ev), len(ref))
for i in range(n):
    a = {k: v for k, v in ev[i].items() if k != "state"}
    b = {k: v for k, v in ref[i].items() if k != "state"}
    if a != b:
        out.append("=== first event divergence at index %d" % i)
        out.append("    ours %s" % json.dumps(a, sort_keys=True)[:400])
        out.append("    ref  %s" % json.dumps(b, sort_keys=True)[:400])
        break
else:
    out.append("=== no event divergence in the first %d events" % n)

Path(__file__).with_name("dump179.txt").write_text("\n".join(out))
print("wrote dump179.txt")
