import pathlib, re, sys

def show(path, start, end):
    p = pathlib.Path(path)
    lines = p.read_text().splitlines()
    print("==== %s lines %d-%d ====" % (path, start, end))
    for i in range(start - 1, min(end, len(lines))):
        print("%5d %s" % (i + 1, lines[i]))

show("src/wlengine/headless.py", 520, 720)
print()
show("src/wlengine/headless.py", 720, 900)
print()
show("tests/conftest.py", 1, 120)
print()
show("tests/test_m5_rules.py", 1, 120)
print()
show("tests/test_m5_rules.py", 480, 540)
print()
show("tests/test_m6_playable.py", 1, 80)
