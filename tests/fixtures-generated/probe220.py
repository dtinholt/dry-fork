"""Probe 220: reference-log events on row 20, and the walkthrough script tokens."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump220.txt"
SC = ROOT / "SPEC" / "scenario"


def main():
    ref = W.load_json(SC / "walkthrough-reference-log.json")["events"]
    wt = W.load_json(SC / "walkthrough.json")
    with OUT.open("w") as f:
        f.write("--- ref events with y==20 ---\n")
        for e in ref:
            if e.get("y") == 20 or (e.get("type") == "checkpoint" and (e.get("state") or {}).get("y") == 20):
                f.write(json.dumps(e)[:400] + "\n")
        f.write("\n--- ref events seq 0..40 ---\n")
        for e in ref[:40]:
            f.write(json.dumps(e)[:300] + "\n")
        f.write("\n--- walkthrough script tokens 0..60 ---\n")
        for i, t in enumerate(wt["script"][:60]):
            f.write("%3d %s\n" % (i, json.dumps(t)))
        f.write("\n--- token_rules ---\n")
        f.write(json.dumps(wt.get("token_rules"))[:2000] + "\n")
        f.write("\n--- start ---\n")
        f.write(json.dumps(wt.get("start"))[:500] + "\n")
    print("wrote", OUT)


main()
