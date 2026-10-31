"""Probe: dump the Saltwell cells near the cactus, the walkthrough script, and
the reference log window for the raider fight."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "dump87.txt"
SCEN = ROOT / "SPEC" / "scenario"


def main():
    out = []
    wt = json.loads((SCEN / "walkthrough.json").read_text())
    out.append("==== walkthrough script ====")
    for i, item in enumerate(wt["script"]):
        out.append("%3d %r" % (i, item))
    out.append("")
    out.append("==== walkthrough keys ====")
    out.append(repr(sorted(wt.keys())))
    for k in wt:
        if k != "script":
            out.append("%s = %r" % (k, wt[k]))
    out.append("")

    # reference log
    ref = json.loads((SCEN / "walkthrough-reference-log.json").read_text())
    out.append("==== reference log type ==== %s" % type(ref).__name__)
    if isinstance(ref, dict):
        out.append(repr(sorted(ref.keys())))
        ev = ref.get("events") or ref.get("log") or []
    else:
        ev = ref
    out.append("==== reference log events (%d) ====" % len(ev))
    for i, e in enumerate(ev):
        out.append("%4d %s" % (i, json.dumps(e)))
    OUT.write_text("\n".join(out) + "\n")
    print("wrote", OUT, len(out), "lines")


if __name__ == "__main__":
    main()
