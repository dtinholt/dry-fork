import pathlib, re, sys

def show(path, start, end):
    p = pathlib.Path(path)
    lines = p.read_text().splitlines()
    print("==== %s lines %d-%d ====" % (path, start, end))
    for i in range(start - 1, min(end, len(lines))):
        print("%5d %s" % (i + 1, lines[i]))

show("src/wlengine/headless.py", 540, 720)
print()
show("tests/conftest.py", 1, 80)
