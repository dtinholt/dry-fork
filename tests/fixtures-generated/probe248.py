"""Probe 248: reference log context around each bump, to learn the bump
coordinate convention (target cell vs. party cell)."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent

ref = json.loads((ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json").read_text())
ev = ref["events"]
out = []
for i, e in enumerate(ev):
    if e.get("type") == "bump":
        out.append("--- bump at index %d: %s" % (i, json.dumps(e)))
        for j in range(max(0, i - 6), min(len(ev), i + 6)):
            out.append("   %4d %s" % (j, json.dumps(ev[j])[:220]))
        out.append("")

# also the CP1 checkpoint state
for e in ev:
    if e.get("type") == "checkpoint":
        out.append("checkpoint %s: %s" % (e.get("name"), json.dumps(e["state"])[:400]))

(OUT / "dump252.txt").write_text("\n".join(out))
print("ok")
