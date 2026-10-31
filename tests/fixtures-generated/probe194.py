"""Probe 194: reference events 280-300, combat.py phase2, headless move/after_move."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump194.txt")
buf = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


log = json.load(open(os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json"), encoding="utf-8"))
evs = log["events"]
p("=" * 70)
p("REFERENCE EVENTS 280-310")
for i in range(280, 312):
    p("%4d %s" % (i, json.dumps(evs[i], sort_keys=True)[:300]))

p("=" * 70)
p("REFERENCE EVENTS 455-475 (save/load)")
for i in range(455, 476):
    p("%4d %s" % (i, json.dumps(evs[i], sort_keys=True)[:300]))

src = os.path.join(ROOT, "src", "wlengine", "combat.py")
lines = open(src, encoding="latin-1").read().splitlines()
p("=" * 70)
p("combat.py 180-300")
for i in range(179, 300):
    p("%5d %s" % (i + 1, lines[i]))

src = os.path.join(ROOT, "src", "wlengine", "headless.py")
lines = open(src, encoding="latin-1").read().splitlines()
p("=" * 70)
p("headless.py 200-260 (input) and 500-600 (move/after_move)")
for i in list(range(199, 260)) + list(range(499, 600)):
    p("%5d %s" % (i + 1, lines[i]))

open(OUT, "w", encoding="latin-1").write("\n".join(buf))
print("wrote", OUT, len(buf))
