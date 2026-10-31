import sys, pathlib
p = pathlib.Path("src/wlengine/headless.py")
lines = p.read_text().splitlines()
def show(a, b, tag):
    print("==== %s (%d-%d) ====" % (tag, a, b))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d %s" % (i + 1, lines[i]))
show(200, 300, "look area")
show(560, 720, "move/bump area")
