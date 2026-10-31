"""Probe 226: run the raider fight for seeds 1..5 and print the consistency
issues plus the combat events."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402
import wl_combat_ref as CR  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump226.txt"
SC = ROOT / "SPEC" / "scenario"


def main():
    d = Path(tempfile.mkdtemp(prefix="probe226-"))
    W.engine_ready()
    W._armed(W.api("scenario.compile"), str(SC), str(d), allow_reference_log=True)
    wt = W.load_json(SC / "walkthrough.json")
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP4":
            break
    with OUT.open("w") as f:
        for seed in (1, 2, 3, 4, 5):
            f.write("=" * 70 + "\nseed %d\n" % seed)
            try:
                ev = W.call("headless.run", str(d), {"seed": seed, "script": script}, seed)
            except Exception as exc:  # noqa: BLE001
                f.write("run failed: %s\n" % exc)
                continue
            for c, m in CR.consistency(ev):
                f.write("ISSUE %s: %s\n" % (c, m))
            i = next((k for k, e in enumerate(ev) if e.get("type") == "encounter_start"), None)
            if i is None:
                continue
            for e in ev[i:]:
                if e.get("type") == "checkpoint":
                    break
                f.write(json.dumps(e)[:200] + "\n")
    shutil.rmtree(d, ignore_errors=True)
    print("wrote", OUT)


main()
