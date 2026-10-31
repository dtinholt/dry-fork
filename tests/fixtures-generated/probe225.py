"""Probe 225: compile fresh, run the walkthrough prefix to CP4, dump our events
and compare with the reference log."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump225.txt"
SC = ROOT / "SPEC" / "scenario"
SEED = 20261021


def main():
    d = Path(tempfile.mkdtemp(prefix="probe225-"))
    W.engine_ready()
    W._armed(W.api("scenario.compile"), str(SC), str(d), allow_reference_log=True)
    ref = W.load_json(SC / "walkthrough-reference-log.json")["events"]
    wt = W.load_json(SC / "walkthrough.json")
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP4":
            break
    with OUT.open("w") as f:
        f.write("--- reference seq 230..300 ---\n")
        for e in ref:
            if 230 <= e.get("seq", 0) <= 300:
                f.write(json.dumps(e)[:300] + "\n")
        f.write("\n--- ours ---\n")
        try:
            ev = W.call("headless.run", str(d), {"seed": SEED, "script": script}, None)
        except Exception as exc:  # noqa: BLE001
            f.write("run failed: %s\n" % exc)
            print("wrote", OUT)
            return
        for e in ev:
            f.write(json.dumps(e)[:300] + "\n")
    shutil.rmtree(d, ignore_errors=True)
    print("wrote", OUT)


main()
