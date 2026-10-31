import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path("src").resolve()))
p = pathlib.Path("src/wlengine/headless.py")
lines = p.read_text().splitlines()
def show(a, b, tag):
    print("==== %s (%d-%d) ====" % (tag, a, b))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d %s" % (i + 1, lines[i]))
show(200, 300, "look area")
show(560, 720, "move/bump area")
show(720, 860, "bump effects")
print("==== total lines", len(lines))

# Now run the engine on the bump scenario and dump events.
from wlengine import headless
import wlengine
print("headless attrs:", [a for a in dir(headless) if not a.startswith("_")])
