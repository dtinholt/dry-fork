"""Dump party.json, the CP3 checkpoint of the reference log, and the encounter
record at overworld (30,41).

Usage: python3 tests/fixtures-generated/probe58.py [party|cp3|cell|all]
"""
import json
import sys

SC = "SPEC/scenario"


def show_party():
    d = json.load(open(SC + "/party.json"))
    print(json.dumps(d, indent=1))


def show_cp(name):
    d = json.load(open(SC + "/walkthrough-reference-log.json"))
    for e in d["events"]:
        if e.get("type") == "checkpoint" and e.get("name") == name:
            print(json.dumps(e, indent=1))
            return
    print("no checkpoint", name)


def show_cell():
    d = json.load(open(SC + "/map0-overworld.json"))
    print("keys:", sorted(d.keys()))
    print("conventions:", d.get("conventions"))
    for key in ("action_cells", "cells", "encounters"):
        if key in d:
            print("--- %s ---" % key)
            print(json.dumps(d[key], indent=1)[:4000])


which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("all", "party"):
    show_party()
if which in ("all", "cp3"):
    show_cp("CP3")
if which in ("all", "cell"):
    show_cell()
