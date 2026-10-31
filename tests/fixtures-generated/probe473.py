"""Probe 473: dump map1 (Saltwell) tiles/actions around row 20 and compare with
the SPEC-05 ASCII map, to decide whether the engine or the compiler is at fault
for M5 test_bump_is_not_a_step (cactus expected at (2,20)) and M6 test_look
(look west from (15,20) expects image 28 at (14,20)).

Also dumps the compiled map (if a compiled data dir exists) so we can see what
the engine actually reads, and prints the SPEC-05 ASCII rows for Saltwell.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(ROOT, "SPEC", "scenario")


def load(name):
    with open(os.path.join(SCEN, name), encoding="utf-8") as fh:
        return json.load(fh)


def dump_ascii():
    spec = os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md")
    with open(spec, encoding="utf-8") as fh:
        text = fh.read()
    idx = text.find("### 5.2 Saltwell")
    if idx < 0:
        print("no Saltwell section found")
        return
    chunk = text[idx:idx + 6000]
    lines = [l for l in chunk.splitlines() if l.startswith("|") and "---" not in l]
    print("--- SPEC-05 Saltwell ASCII rows (first 40) ---")
    for i, l in enumerate(lines[:40]):
        print("%2d %s" % (i, l))


def main():
    d = load("map1-saltwell.json")
    print("keys:", sorted(d.keys()))
    for k, v in d.items():
        if isinstance(v, list):
            print("  %-16s list len=%d first=%r" % (k, len(v), v[0] if v else None))
        else:
            print("  %-16s %r" % (k, v))

    tiles = d.get("tiles")
    if tiles:
        print("tiles rows=%d cols=%d" % (len(tiles), len(tiles[0])))
        for y in range(17, 24):
            print("tiles y=%2d x0..19  %s" % (y, tiles[y][:20]))
            print("tiles y=%2d x10..29 %s" % (y, tiles[y][10:30]))

    for key in ("action_class", "action_value", "action", "actions"):
        v = d.get(key)
        if isinstance(v, list) and v and isinstance(v[0], list):
            print("%s rows=%d cols=%d" % (key, len(v), len(v[0])))
            for y in range(17, 24):
                print("%s y=%2d x0..19 %s" % (key, y, v[y][:20]))

    dump_ascii()

    # Try to find a compiled data dir to inspect what the engine reads.
    for cand in ("build", "data", "out", "compiled"):
        p = os.path.join(ROOT, cand)
        if os.path.isdir(p):
            print("candidate dir:", p, os.listdir(p)[:20])


if __name__ == "__main__":
    main()
