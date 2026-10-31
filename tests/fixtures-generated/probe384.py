"""Probe: reproduce test_bump_is_not_a_step (M5) and test_look (M6).

Finds a compiled data dir, runs headless.run with the failing scripts and
prints the events, plus the map cells around the relevant coordinates.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "src"))

import wlengine.headless as H  # noqa: E402


def find_data():
    cands = []
    for base in (HERE, ROOT / "tests", ROOT):
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_dir() and (p / "GAME1").is_file():
                cands.append(p)
    return cands


def main():
    cands = find_data()
    print("candidate data dirs:")
    for c in cands[:20]:
        print("  ", c)
    if not cands:
        print("none found")
        return
    dd = cands[0]
    print("using", dd)
    print("files:", sorted(os.listdir(dd))[:40])

    for name, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                         ("look", ["L", "LEFT", {"checkpoint": "a"}])):
        print("=" * 60)
        print("run", name)
        try:
            ev = H.run(str(dd), {"seed": 1, "script": script})
        except Exception as e:  # noqa: BLE001
            print("ERROR", type(e).__name__, e)
            continue
        if isinstance(ev, tuple):
            ev = ev[0]
        for e in ev:
            print(json.dumps(e, sort_keys=True))

    # dump the map cells around (15, 20) on location 1
    print("=" * 60)
    print("map cells")
    try:
        import wlengine.maps as M
        import wlengine.scenario as S
        sc = S.Scenario(str(dd))
        mp = sc.map(1)
        for y in range(18, 23):
            row = []
            for x in range(0, 20):
                c = mp.cell(x, y)
                row.append("%d/%d/%d" % (c.image, c.action_class, c.action))
            print(y, " ".join(row))
    except Exception as e:  # noqa: BLE001
        print("map dump failed", type(e).__name__, e)


if __name__ == "__main__":
    main()
