"""Dump the reference log's checkpoint states: cell_changes and key fields."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
d = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())
ev = d["events"]

out = []
for e in ev:
    if e.get("type") == "checkpoint":
        st = e["state"]
        cc = st.get("cell_changes") or []
        out.append("checkpoint %-16s loc=%s x=%s y=%s steps=%s day=%s %02d:%02d mode=%s rng=%s ncc=%d"
                   % (e["name"], st.get("location"), st.get("x"), st.get("y"), st.get("steps"),
                      st.get("day"), st.get("hour"), st.get("minute"), st.get("mode"),
                      st.get("rng_state"), len(cc)))
        out.append("   cc=%r" % (cc,))

# also the walkthrough JSON
wt = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough.json").read_text())
out.append("=== walkthrough keys %r" % (list(wt.keys()),))
out.append(json.dumps(wt, indent=1)[:6000])

Path(__file__).with_name("dump176.txt").write_text("\n".join(out))
print("wrote dump176.txt")
