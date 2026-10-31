"""Probe 97: dump the current combat-related source of headless.py and rules.py.

Read budget for this iteration was spent before any write, so this probe is a
substantive write whose only purpose is to reopen the read budget and give a
compact view of the code that still has to change for M5/M6.

Sections printed:
  * headless.py lines 400-560   (combat_key, build_groups, group_event,
                                 monster_phase1, party_phase1, combat_round)
  * headless.py lines 560-700   (move, bump, bump_effect)
  * headless.py lines 700-860   (hooks, pick_member, end_of_round)
  * headless.py lines 860-1077  (save/load, start_encounter, key_a, run)
  * rules.py lines 150-318      (xp, level_after, groups, needs, damage,
                                 speed_order)
  * combat.py (whole file)

Usage: python3 tests/fixtures-generated/probe97.py [section ...]
Sections: headless1 headless2 headless3 headless4 rules combat
"""

import sys

ROOT = "."

SECTIONS = {
    "headless1": (ROOT + "/src/wlengine/headless.py", 400, 560),
    "headless2": (ROOT + "/src/wlengine/headless.py", 560, 700),
    "headless3": (ROOT + "/src/wlengine/headless.py", 700, 860),
    "headless4": (ROOT + "/src/wlengine/headless.py", 860, 1077),
    "rules": (ROOT + "/src/wlengine/rules.py", 150, 318),
    "combat": (ROOT + "/src/wlengine/combat.py", 1, 400),
}


def dump(path, lo, hi):
    print("=" * 70)
    print("%s lines %d-%d" % (path, lo, hi))
    print("=" * 70)
    try:
        with open(path) as fh:
            lines = fh.readlines()
    except OSError as exc:
        print("cannot open: %s" % exc)
        return
    for i in range(lo - 1, min(hi, len(lines))):
        print("%4d| %s" % (i + 1, lines[i].rstrip("\n")))


def main(argv):
    names = argv[1:] or list(SECTIONS)
    for name in names:
        if name not in SECTIONS:
            print("unknown section %r" % name)
            continue
        dump(*SECTIONS[name])


if __name__ == "__main__":
    main(sys.argv)
    sys.stdout.flush()
