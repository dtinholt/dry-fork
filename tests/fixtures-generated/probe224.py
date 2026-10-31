"""Probe 224: dump the reference combat window (seq 240..300) and ours for the
same walkthrough prefix, seed 20261021."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump224.txt"
SC = ROOT / "SPEC" / "scenario"
DD = Path(__file__).resolve().parent / "dd"
SEED = 20261021


def main():
    ref = W.load_json(SC / "walkthrough-reference-log.json")["events"]
    wt = W.load_json(SC / "walkthrough.json")
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP4":
            break
    with OUT.open("w") as f:
        f.write("--- reference seq 240..300 ---\n")
        for e in ref:
            if 240 <= e.get("seq", 0) <= 300:
                f.write(json.dumps(e)[:300] + "\n")
        f.write("\n--- ours ---\n")
        try:
            ev = W.call("headless.run", str(DD), {"seed": SEED, "script": script}, None)
        except Exception as exc:  # noqa: BLE001
            f.write("run failed: %s\n" % exc)
            print("wrote", OUT)
            return
        for e in ev:
            f.write(json.dumps(e)[:300] + "\n")
    print("wrote", OUT)


main()
