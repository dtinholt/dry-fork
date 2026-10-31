"""probe451: exact column positions in the SPEC-05 Saltwell ASCII art vs the
frozen SPEC/scenario/map1-saltwell.json arrays, plus the SPEC/reference tree.

Run: python3 tests/fixtures-generated/probe451.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")
SCEN = os.path.join(SPEC, "scenario")


def art_rows():
    txt = open(os.path.join(SPEC, "SPEC-05-scenario.md"), encoding="utf-8").read().splitlines()
    start = None
    for i, l in enumerate(txt):
        if l.strip().startswith("0  ||||"):
            start = i
            break
    rows = []
    for k in range(32):
        l = txt[start + k]
        # strip the leading "  NN  " label (5 chars)
        body = l[5:]
        rows.append(body)
    return rows


def main():
    rows = art_rows()
    print("== ASCII art rows (raw, len, index of first/last non-'|') ==")
    for y, r in enumerate(rows):
        print("y=%2d len=%2d %r" % (y, len(r), r))
    print()
    print("== interesting cells ==")
    for y in (11, 12, 20, 29, 30, 31):
        r = rows[y]
        for ch in ("P", "Y", ";"):
            idxs = [i for i, c in enumerate(r) if c == ch]
            print("y=%2d char %r at art indices %s" % (y, ch, idxs))
    print()
    print("== SPEC/reference tree ==")
    ref = os.path.join(SPEC, "reference")
    for dirpath, dirnames, filenames in os.walk(ref):
        rel = os.path.relpath(dirpath, ref)
        print(" dir", rel, "->", sorted(filenames)[:20])
    print()
    print("== map1-saltwell.json ==")
    d = json.load(open(os.path.join(SCEN, "map1-saltwell.json"), encoding="utf-8"))
    print("width", d["width"], "height", d["height"], "location", d["location"])
    tiles = d["tiles"]
    ac = d["action_class"]
    av = d["action_value"]
    for y in (0, 1, 11, 12, 19, 20, 21, 29, 30, 31):
        print("tiles y=%2d:" % y, " ".join("%2d" % v for v in tiles[y]))
    for y in (11, 12, 20, 29, 30, 31):
        print("aclass y=%2d:" % y, " ".join("%2d" % v for v in ac[y]))
        print("avalue y=%2d:" % y, " ".join("%2d" % v for v in av[y]))
    print("action_cells:", json.dumps(d["action_cells"])[:2000])
    print("info:", json.dumps(d["info"])[:800])
    print("conventions:", json.dumps(d["conventions"])[:800])


if __name__ == "__main__":
    main()
