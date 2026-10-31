"""probe434: dump the first events of the frozen walkthrough reference log and
the first tokens of the walkthrough script, to learn the coordinate convention.

Run: python3 tests/fixtures-generated/probe434.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"


def main():
    wt = json.loads((SCEN / "walkthrough.json").read_text(encoding="utf-8"))
    print("script first 40:", json.dumps(wt["script"][:40]))
    print("checkpoints:", json.dumps(wt["checkpoints"], indent=1)[:1500])
    ref = json.loads((SCEN / "walkthrough-reference-log.json").read_text(encoding="utf-8"))
    evs = ref["events"] if isinstance(ref, dict) else ref
    for e in evs[:70]:
        print(json.dumps(e)[:220])
    print("...")
    # all move events with their location
    moves = [e for e in evs if e.get("type") == "move"]
    print("moves:", len(moves))
    for e in moves[:40]:
        print("  ", json.dumps(e))


if __name__ == "__main__":
    main()
