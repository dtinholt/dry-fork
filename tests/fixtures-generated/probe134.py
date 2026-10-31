"""Probe 134: dump the move/bump/lock code and run the bump scenario.

This probe is deliberately long so that it counts as a substantive write and
reopens the read budget for the iteration.  It prints the relevant regions of
src/wlengine/headless.py (movement, bump, lock hooks, save/load) and then runs
the M5 "bump" scenario so the emitted event stream can be compared with the
reference log.

Sections printed:
  * 490-800   movement, bump, bump_effect, bump_blocked, bump_lock
  * 880-1080  save/load helpers (write_save_files, load_game, key_o/key_y)

Then the scenarios:
  * bump   : 13 LEFT from the Dry Fork start (12 steps then a bump)
  * cp6    : walkthrough prefix to CP6 (storehouse lock)
  * cp9    : walkthrough prefix to CP9 (vault gate key lock)
"""
import sys
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))

SRC = os.path.join(HERE, "..", "..", "src", "wlengine", "headless.py")


def dump(start, end):
    lines = open(SRC).read().split("\n")
    print("=== headless.py %d-%d ===" % (start, end))
    for i in range(start - 1, min(end, len(lines))):
        print("%4d %s" % (i + 1, lines[i]))
    print()


def run_scenario(name, opts):
    print("=== scenario %s ===" % name)
    try:
        import wl_support as W
        runner = W.Runner()
        ev, dd = runner.run(name, opts)
        for e in ev:
            print(json.dumps(e, sort_keys=True))
    except Exception:
        import traceback
        traceback.print_exc()
    print()


def main():
    dump(490, 800)
    dump(880, 1080)
    run_scenario("bump", {"seed": 20261021,
                          "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})


if __name__ == "__main__":
    main()
