"""probe452: run the engine on the two failing scripts and dump the map cells.

Run: python3 tests/fixtures-generated/probe452.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402

SEED = 20261021


def main():
    d = tempfile.mkdtemp(prefix="probe452-")
    W.engine_ready()
    fn = W.api("scenario.compile")
    W._armed(fn, str(W.SCENARIO), d, allow_reference_log=True)
    print("compiled to", d)
    print("files:", sorted(os.listdir(d)))

    # dump the compiled map1
    for name in sorted(os.listdir(d)):
        if "map" in name.lower() and name.endswith(".json"):
            try:
                m = json.load(open(os.path.join(d, name), encoding="utf-8"))
            except Exception:
                continue
            if isinstance(m, dict) and "tiles" in m:
                print("== compiled", name, "w", m.get("width"), "h", m.get("height"))
                for y in (19, 20, 21):
                    print(" tiles y=%2d:" % y, " ".join("%2d" % v for v in m["tiles"][y]))
                for k in ("action_class", "action_value"):
                    if k in m:
                        for y in (19, 20, 21):
                            print(" %s y=%2d:" % (k, y), " ".join("%2d" % v for v in m[k][y]))
                print(" start:", json.dumps(m.get("start") or m.get("info"))[:400])

    for key, script in (("bump", ["LEFT"] * 13), ("look", ["L", "LEFT"])):
        dd = tempfile.mkdtemp(prefix="probe452-%s-" % key)
        import shutil
        shutil.copytree(d, dd, dirs_exist_ok=True)
        ev = W.call("headless.run", dd, json.dumps({"seed": SEED, "script": script + [{"checkpoint": "a"}]}))
        print("== %s ==" % key)
        for e in ev:
            print("  ", json.dumps(e)[:300])


if __name__ == "__main__":
    main()
