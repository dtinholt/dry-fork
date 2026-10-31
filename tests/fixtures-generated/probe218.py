"""Probe 218: run the bump script on the compiled dd data dir and dump events."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump218.txt"
DD = Path(__file__).resolve().parent / "dd"
SEED = 20261021


def main():
    with OUT.open("w") as f:
        ev = W.call("headless.run", str(DD), {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}, None)
        for e in ev:
            f.write(json.dumps(e) + "\n")
    print("wrote", OUT)


main()
