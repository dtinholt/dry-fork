"""probe450: compare SPEC-05 ASCII Saltwell rows with SPEC/scenario JSON, and
dump the engine's view of cells around (14..16, 19..21).

Run: python3 tests/fixtures-generated/probe450.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")
SCEN = os.path.join(SPEC, "scenario")


def main():
    print("== SPEC/scenario listing ==")
    for n in sorted(os.listdir(SCEN)):
        print("  ", n)

    # find a map json with tiles
    cand = None
    for n in sorted(os.listdir(SCEN)):
        if not n.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(SCEN, n), encoding="utf-8"))
        except Exception as e:
            print("  !", n, e)
            continue
        if isinstance(d, dict) and "tiles" in d:
            print("map json:", n, "keys:", sorted(d.keys()))
            if cand is None:
                cand = (n, d)
    if cand is None:
        print("no map json with tiles found")
        return
    name, d = cand
    tiles = d["tiles"]
    print("map", name, "rows", len(tiles), "cols", len(tiles[0]))
    for y in (0, 1, 19, 20, 21, 30, 31):
        row = tiles[y]
        print("tiles y=%2d:" % y, " ".join("%2d" % v for v in row))
    for key in ("action_class", "action_value", "action", "classes", "values"):
        if key in d:
            arr = d[key]
            print(key, "rows", len(arr), "cols", len(arr[0]))
            for y in (19, 20, 21):
                print("  %s y=%2d:" % (key, y), " ".join("%2d" % v for v in arr[y]))

    # parse the ASCII art from SPEC-05
    txt = open(os.path.join(SPEC, "SPEC-05-scenario.md"), encoding="utf-8").read().splitlines()
    start = None
    for i, l in enumerate(txt):
        if l.strip().startswith("0  ||||"):
            start = i
            break
    print("ascii start line", start)
    if start is not None:
        for k in range(0, 32):
            l = txt[start + k]
            body = l.split("|", 1)[1] if "|" in l else l
            # body includes the trailing '|' of the art
            body = body.rstrip()
            if body.endswith("|"):
                body = body[:-1]
            print("ascii y=%2d len=%2d %r" % (k, len(body), body))
        # column ruler
        print("ruler:", txt[start - 2])
        print("ruler:", txt[start - 1])


if __name__ == "__main__":
    main()
