"""Probe 13: run the engine's "opening" script and dump the event log.

Usage:
    python3 tests/fixtures-generated/probe13.py [seed]

Prints the event log of the raider encounter opening (the script the M5 tests
use) so we can compare against tests/wl_combat_ref.opening(seed).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "tests"))

import wl_support as W  # noqa: E402


def opening_script(walkthrough):
    out = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            return out + ["A"]
        out.append(item)
    raise AssertionError("no repeat_until")


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261021
    data_dir = PROJECT / "tests/fixtures-generated/dd3"
    walkthrough = W.load_json(W.SCENARIO / "walkthrough.json")
    script = opening_script(walkthrough)
    print("script:", script)
    from wlengine import headless
    ev = headless.run(str(data_dir), {"seed": seed, "script": script}, seed)
    for e in ev:
        print(json.dumps(e, default=str)[:400])
    print("---- reference ----")
    import wl_combat_ref as CR
    ref = CR.opening(seed)
    print(json.dumps(ref, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
