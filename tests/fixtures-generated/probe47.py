"""Probe 47: raw JSON structure of map1-saltwell.json around row 20 and the
full action_cells list; also search the reference log for (2,20)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"


def main():
    txt = (SCEN / "map1-saltwell.json").read_text()
    d = json.loads(txt)
    print("keys:", list(d.keys()))
    print("conventions:", json.dumps(d.get("conventions"))[:2000])
    ac = d["action_class"]
    tl = d["tiles"]
    av = d["action_value"]
    print("len(ac)=%d len(ac[0])=%d len(tl)=%d len(tl[0])=%d" % (len(ac), len(ac[0]), len(tl), len(tl[0])))
    print("action_cells (%d):" % len(d["action_cells"]))
    for c in d["action_cells"]:
        print("   ", json.dumps(c))
    print("ac rows 19,20,21:")
    for r in (19, 20, 21):
        print("  y=%d class %s" % (r, ac[r]))
        print("  y=%d tiles %s" % (r, tl[r]))
    # raw text around the cactus
    i = txt.find('"action_class"')
    print("raw action_class starts at", i)
    print(txt[i:i + 400])
    # reference log search
    log = json.loads((SCEN / "walkthrough-reference-log.json").read_text())
    ev = log["events"] if isinstance(log, dict) else log
    for e in ev:
        if e.get("x") == 2 and e.get("y") == 20:
            print("REF (2,20):", json.dumps(e))
        if e.get("x") == 3 and e.get("y") == 20:
            print("REF (3,20):", json.dumps(e))


if __name__ == "__main__":
    main()
