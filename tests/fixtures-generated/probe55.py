"""Dump walkthrough.json script and the CP3/CP4 checkpoint party states.

Usage: python3 tests/fixtures-generated/probe55.py [script|cp3|cp4|items|all]
"""
import json
import sys

WT = "SPEC/scenario/walkthrough.json"


def show_script():
    d = json.load(open(WT))
    for i, item in enumerate(d["script"]):
        print("%3d| %r" % (i, item))


def show_cp(name):
    for line in open("tests/fixtures-generated/reflog.txt"):
        if '"checkpoint"' in line and '"%s"' % name in line:
            e = json.loads(line)
            print(json.dumps(e, indent=1)[:6000])
            return
    print("no checkpoint", name)


def show_items():
    d = json.load(open("SPEC/scenario/items.json"))
    for it in d["items"]:
        print(it)


which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("all", "script"):
    show_script()
if which in ("all", "cp3"):
    show_cp("CP3")
if which in ("all", "cp4"):
    show_cp("CP4")
if which in ("all", "items"):
    show_items()
