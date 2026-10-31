"""Probe 135: dump headless.py regions and the bump scenario to a file.

Writes tests/fixtures-generated/dump135.txt with:
  * headless.py 490-800   movement, bump, bump_effect, bump_blocked, bump_lock
  * headless.py 880-1080  save/load helpers (write_save_files, load_game, key_o/key_y)
  * the event stream of the M5 "bump" scenario (13 LEFT from the Dry Fork start)
  * the event stream of the M5 "cp6" scenario (storehouse lock)
  * the event stream of the M5 "cp9" scenario (vault gate key lock)
"""
import sys
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))

SRC = os.path.join(HERE, "..", "..", "src", "wlengine", "headless.py")
OUT = os.path.join(HERE, "dump135.txt")

out = open(OUT, "w")


def w(line=""):
    out.write(line + "\n")


def dump(start, end):
    lines = open(SRC).read().split("\n")
    w("=== headless.py %d-%d ===" % (start, end))
    for i in range(start - 1, min(end, len(lines))):
        w("%4d %s" % (i + 1, lines[i]))
    w()


def run_scenario(name, opts):
    w("=== scenario %s ===" % name)
    try:
        import wl_support as W
        runner = W.Runner()
        ev, dd = runner.run(name, opts)
        for e in ev:
            w(json.dumps(e, sort_keys=True))
    except Exception:
        import traceback
        w(traceback.format_exc())
    w()


def main():
    dump(490, 800)
    dump(880, 1080)
    run_scenario("bump", {"seed": 20261021,
                          "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    out.close()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
