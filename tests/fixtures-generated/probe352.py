"""probe352: locate the compiled scenario dir(s) and dump the cells around
(2..6, 20) for location 1 in both readings, plus action classes.

Run:  python3 tests/fixtures-generated/probe352.py
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

print("ROOT", ROOT)

cands = []
for pat in ("**/maps.json", "**/scenario.json", "**/LABTABLES.BIN", "**/GAME1"):
    for p in glob.glob(os.path.join(ROOT, pat), recursive=True):
        cands.append(p)
for p in sorted(set(cands)):
    print("cand", os.path.relpath(p, ROOT))

# try to find a directory that looks like a compiled scenario
dirs = set()
for p in cands:
    dirs.add(os.path.dirname(p))
print("dirs", sorted(os.path.relpath(d, ROOT) for d in dirs))

try:
    import wlengine.headless as H
except Exception as e:
    print("import headless failed", e)
    H = None

if H is not None:
    for d in sorted(dirs):
        try:
            sc = H._load_scenario(d)
        except Exception as e:
            print("load", os.path.relpath(d, ROOT), "failed", type(e).__name__, e)
            continue
        print("=== loaded", os.path.relpath(d, ROOT))
        try:
            locs = sc.locations() if hasattr(sc, "locations") else None
        except Exception:
            locs = None
        print("locations", locs)
        for loc in (0, 1, 2, 3):
            try:
                m = sc.map(loc)
            except Exception as e:
                print("map", loc, "failed", type(e).__name__, e)
                continue
            cells = m["cells"]
            print("map", loc, "size", m.get("size"), "keys", sorted(cells.keys()))
            ac = cells.get("actionClass")
            act = cells.get("action")
            img = cells.get("image")
            tiles = cells.get("tile")
            for y in (19, 20, 21):
                row = []
                for x in range(0, 8):
                    try:
                        a = ac[y][x]
                    except Exception:
                        a = None
                    try:
                        b = act[y][x]
                    except Exception:
                        b = None
                    try:
                        t = tiles[y][x]
                    except Exception:
                        t = None
                    try:
                        im = img[y][x]
                    except Exception:
                        im = None
                    row.append((x, a, b, t, im))
                print("  y=%d" % y, row)
            # transposed reading
            print("  transposed (tiles[x][y]) for x=2..5,y=20:")
            for x in range(2, 6):
                try:
                    print("    x=%d tile=%s ac=%s act=%s img=%s" % (
                        x, tiles[x][20], ac[x][20], act[x][20], img[x][20]))
                except Exception as e:
                    print("    x=%d failed %s" % (x, e))
