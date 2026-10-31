#!/usr/bin/env python3
"""Print the reference walkthrough event log (SPEC/scenario/walkthrough-reference-log.json).

Usage:
    python3 tests/fixtures-generated/refcheck.py                 # all events
    python3 tests/fixtures-generated/refcheck.py TYPE [TYPE...]  # only these types
    python3 tests/fixtures-generated/refcheck.py --range A B     # events [A, B)
    python3 tests/fixtures-generated/refcheck.py --json TYPE     # raw json of matches

This is a read-only debugging aid: it never writes anything and is not part of
the engine.  It exists so that a failing engine event can be compared against
the reference log without re-reading the whole SPEC.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REF = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")


def load():
    with open(REF, "r", encoding="utf-8") as fh:
        return json.load(fh)


def events(doc):
    if isinstance(doc, dict):
        for key in ("events", "log", "reference"):
            if key in doc:
                return doc[key]
        return doc
    return doc


def main(argv):
    doc = load()
    ev = events(doc)
    types = []
    lo, hi = 0, len(ev)
    as_json = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--range":
            lo, hi = int(argv[i + 1]), int(argv[i + 2])
            i += 3
            continue
        if a == "--json":
            as_json = True
            i += 1
            continue
        types.append(a)
        i += 1
    shown = 0
    for k, e in enumerate(ev):
        if not (lo <= k < hi):
            continue
        if types and e.get("type") not in types:
            continue
        if as_json:
            print(json.dumps(e, sort_keys=True))
        else:
            print("%5d %s" % (k, json.dumps(e, sort_keys=True)))
        shown += 1
    print("# %d/%d events shown" % (shown, len(ev)), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
