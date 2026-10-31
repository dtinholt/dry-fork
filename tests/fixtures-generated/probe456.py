"""probe456: precise index:value dump of the frozen map1 rows 11 and 20, the
ASCII art rows, and the engine's runtime map (read back from the compiled
GAME1 through the engine's own maps API).

Run: python3 tests/fixtures-generated/probe456.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SCEN = os.path.join(ROOT, "SPEC", "scenario")


def main():
    m = json.load(open(os.path.join(SCEN, "map1-saltwell.json"), encoding="utf-8"))
    for y in (11, 20):
        print("JSON tiles y=%d:" % y)
        print("   ", " ".join("%d:%d" % (x, v) for x, v in enumerate(m["tiles"][y])))
        print("   class:", " ".join("%d:%d" % (x, v) for x, v in enumerate(m["action_class"][y])))
    txt = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md"), encoding="utf-8").read().splitlines()
    start = next(i for i, l in enumerate(txt) if l.strip().startswith("0  ||||"))
    for y in (11, 20):
        body = txt[start + y][5:]
        print("ASCII y=%d:" % y, " ".join("%d:%s" % (x, c) for x, c in enumerate(body)))

    # engine runtime map
    import wl_support as W
    d = tempfile.mkdtemp(prefix="probe456-")
    W.engine_ready()
    fn = W.api("scenario.compile")
    W._armed(fn, str(W.SCENARIO), d, allow_reference_log=True)
    print("compiled:", sorted(os.listdir(d)))
    # try the engine's maps API
    import wlengine.maps as M
    print("maps module attrs:", [a for a in dir(M) if not a.startswith("_")])
    import wlengine.headless as H
    print("headless attrs:", [a for a in dir(H) if not a.startswith("_")][:60])


if __name__ == "__main__":
    main()
