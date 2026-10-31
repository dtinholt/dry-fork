import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
out = open(os.path.join(HERE, "dump111.txt"), "w")
for name in ("headless.py", "combat.py", "scenario.py"):
    p = os.path.join(ROOT, "src", "wlengine", name)
    lines = open(p).read().split("\n")
    out.write("=== %s (%d lines) ===\n" % (name, len(lines)))
    for i, s in enumerate(lines):
        out.write("%4d| %s\n" % (i + 1, s))
out.close()
