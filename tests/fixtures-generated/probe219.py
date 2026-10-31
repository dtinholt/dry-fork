"""Probe 219: align the SPEC-05 Saltwell art rows with the scenario JSON rows."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump219.txt"
SC = ROOT / "SPEC" / "scenario"


def main():
    m = W.load_json(SC / "map1-saltwell.json")
    spec = (ROOT / "SPEC" / "SPEC-05-scenario.md").read_text().splitlines()
    # find the Saltwell art block: lines with "|" and a leading row number
    art = {}
    for ln in spec:
        s = ln.strip()
        if s.startswith("|") and s.endswith("|") and len(s) > 20:
            # format: "NN  |....|"
            parts = s.split(None, 1)
            if len(parts) == 2 and parts[0].isdigit():
                art[int(parts[0])] = parts[1]
    with OUT.open("w") as f:
        f.write("art rows: %s\n" % sorted(art)[:5])
        for y in sorted(art):
            row = art[y]
            f.write("y=%2d art  %s\n" % (y, row))
            f.write("      idx  %s\n" % "".join(str(i % 10) for i in range(len(row))))
            if y < len(m["tiles"]):
                f.write("      tile %s\n" % "".join("%d" % (t % 10) for t in m["tiles"][y]))
                f.write("      cls  %s\n" % "".join("%d" % (c % 10) for c in m["action_class"][y]))
                f.write("      act  %s\n" % "".join("%d" % (a % 10) for a in m["action_value"][y]))
        f.write("\nrow20 tiles=%s\n" % m["tiles"][20])
        f.write("row20 cls=%s\n" % m["action_class"][20])
        f.write("row20 act=%s\n" % m["action_value"][20])
    print("wrote", OUT)


main()
