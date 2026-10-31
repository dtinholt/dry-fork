"""probe432: compile SPEC/scenario and run the two failing scripts, dumping
events and the compiled map cells around the interesting coordinates.

Run: python3 tests/fixtures-generated/probe432.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from wlengine import headless, scenario  # noqa: E402

SCEN = ROOT / "SPEC" / "scenario"
SEED = 20261021


def main():
    d = Path(tempfile.mkdtemp("compiled"))
    scenario.compile(str(SCEN), str(d))
    print("compiled into", d)
    print("files:", sorted(p.name for p in d.iterdir())[:40])

    # dump the compiled map for location 1
    for name in sorted(p.name for p in d.iterdir()):
        if "map" in name.lower() or name.endswith(".json"):
            print("---", name)
    mp = None
    for cand in ("map1.json", "map_1.json", "maps.json", "map1-saltwell.json"):
        p = d / cand
        if p.is_file():
            mp = json.loads(p.read_text())
            print("using", cand)
            break
    if mp is None:
        # try any json with 'tiles'
        for p in d.iterdir():
            if p.suffix == ".json":
                try:
                    j = json.loads(p.read_text())
                except Exception:
                    continue
                if isinstance(j, dict) and "tiles" in j:
                    mp = j
                    print("using", p.name)
                    break
    if mp is not None:
        print("map keys:", sorted(mp.keys()))
        t = mp.get("tiles")
        if t:
            for y in (11, 20):
                print("tiles[%d] = %s" % (y, t[y]))
        ac = mp.get("action_class")
        if ac:
            for y in (11, 20):
                print("aclass[%d] = %s" % (y, ac[y]))

    for key, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                        ("look", ["L", "LEFT", {"checkpoint": "a"}])):
        ev, _ = headless.run(str(d), {"seed": SEED, "script": script})
        print("\n=== %s ===" % key)
        for e in ev:
            print("  ", json.dumps(e))


if __name__ == "__main__":
    main()
