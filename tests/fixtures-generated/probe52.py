"""Dump the parts of headless.py and rules.py needed to implement combat.

Usage: python3 tests/fixtures-generated/probe52.py [init|combat|rules|save|labstate|all]

This probe exists so that the engine source can be inspected without spending
the read budget of the iteration: it prints numbered source lines for the
combat, save/load and rules sections of the engine.

Sections:
  init      headless.py 1-130   (imports, Engine.__init__, state)
  head      headless.py 130-400 (party, items, skills, shops)
  mid       headless.py 620-900 (movement, bump, hooks, encounters)
  tail      headless.py 900-1077 (encounter start, save/load, driver)
  combat    headless.py 620-1077
  rules     rules.py 1-318
  labstate  labstate.py 1-60
  save      grep for def/save in headless.py
  all       everything above
"""
import sys

HEAD = "src/wlengine/headless.py"
RULES = "src/wlengine/rules.py"


def show(path, a, b):
    lines = open(path).read().split("\n")
    print("=== %s lines %d-%d (of %d) ===" % (path, a, b, len(lines)))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))


def grep(path, pat):
    print("=== grep %s %r ===" % (path, pat))
    for i, line in enumerate(open(path).read().split("\n")):
        if pat in line:
            print("%4d| %s" % (i + 1, line))


def dump_all():
    show(HEAD, 1, 130)
    show(HEAD, 130, 400)
    show(HEAD, 620, 1077)
    show(RULES, 1, 318)
    show("src/wlengine/labstate.py", 1, 60)


which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which == "all":
    dump_all()
elif which == "init":
    show(HEAD, 1, 130)
elif which == "head":
    show(HEAD, 130, 400)
elif which == "combat":
    show(HEAD, 620, 1077)
elif which == "mid":
    show(HEAD, 620, 900)
elif which == "tail":
    show(HEAD, 900, 1077)
elif which == "rules":
    show(RULES, 1, 318)
elif which == "save":
    grep(HEAD, "def ")
    grep(HEAD, "save")
elif which == "labstate":
    show("src/wlengine/labstate.py", 1, 60)
elif which == "combat2":
    show(HEAD, 797, 900)
elif which == "rules2":
    show(RULES, 200, 319)
elif which == "head2":
    show(HEAD, 130, 400)
else:
    print("unknown section %r" % which)
