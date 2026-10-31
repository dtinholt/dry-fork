"""Dump the Scenario object's attributes and item/shop tables.

Usage: python3 tests/fixtures-generated/probe62.py [attrs|items|shops|all]
"""
import json
import os
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "tests")

from wlengine import scenario  # noqa: E402

OUT = "tests/fixtures-generated/dd9"


def build():
    if not os.path.isdir(OUT):
        scenario.compile("SPEC/scenario", OUT)
    return scenario.load(OUT)


which = sys.argv[1] if len(sys.argv) > 1 else "all"
sc = build()
if which in ("all", "attrs"):
    for name in sorted(dir(sc)):
        if name.startswith("_"):
            continue
        v = getattr(sc, name)
        if callable(v):
            print("method", name)
        else:
            print("attr", name, "=", repr(v)[:200])
if which in ("all", "items"):
    fn = getattr(sc, "item_table", None)
    tbl = fn() if fn else None
    print("item_table:", json.dumps(tbl, indent=1)[:3000] if tbl else tbl)
if which in ("all", "shops"):
    print("shops:", json.dumps(sc.shops, indent=1)[:3000])
