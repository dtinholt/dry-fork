#!/usr/bin/env python3
"""Reference-log inspector for the Dry Fork walkthrough.

Usage:
    python3 tests/fixtures-generated/refdiff.py ref [CPNAME] [--after N]
        Print the reference log events, optionally only those after the
        checkpoint CPNAME, with a running index.

    python3 tests/fixtures-generated/refdiff.py diff ENGINE_LOG.json [CPNAME]
        Align the reference log and an engine log by index and print the
        first N differences (default 40).

    python3 tests/fixtures-generated/refdiff.py types
        Print a histogram of event types in the reference log.

The reference log lives at SPEC/scenario/walkthrough-reference-log.json and
is frozen; the engine log is whatever the headless driver wrote.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "SPEC" / "scenario" / "walkthrough-reference-log.json"


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def events(doc):
    if isinstance(doc, dict):
        for key in ("events", "log", "script"):
            if key in doc and isinstance(doc[key], list):
                return doc[key]
        raise SystemExit("no event list in %r" % (list(doc)[:8],))
    return doc


def strip(e):
    if isinstance(e, dict):
        return {k: v for k, v in e.items() if k != "seq"}
    return e


def show(ev, start=0, limit=None, width=200):
    n = 0
    for i, e in enumerate(ev):
        if i < start:
            continue
        print("%5d %s" % (i, json.dumps(strip(e), sort_keys=True)[:width]))
        n += 1
        if limit is not None and n >= limit:
            break


def checkpoint_index(ev, name):
    for i, e in enumerate(ev):
        if isinstance(e, dict) and e.get("type") == "checkpoint" and e.get("name") == name:
            return i
    raise SystemExit("no checkpoint %r" % name)


def diff(ref, eng, limit=40):
    shown = 0
    for i in range(max(len(ref), len(eng))):
        a = strip(ref[i]) if i < len(ref) else "<missing>"
        b = strip(eng[i]) if i < len(eng) else "<missing>"
        if a != b:
            print("--- index %d" % i)
            print("  ref: %s" % json.dumps(a, sort_keys=True)[:400])
            print("  eng: %s" % json.dumps(b, sort_keys=True)[:400])
            shown += 1
            if shown >= limit:
                break
    if shown == 0:
        print("identical (%d events)" % len(ref))


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    ref = events(load(REF))
    if cmd == "ref":
        start = 0
        limit = None
        rest = argv[1:]
        if rest and not rest[0].startswith("-"):
            start = checkpoint_index(ref, rest[0])
            rest = rest[1:]
        if "--after" in rest:
            start += int(rest[rest.index("--after") + 1])
        if "--limit" in rest:
            limit = int(rest[rest.index("--limit") + 1])
        show(ref, start, limit)
        return 0
    if cmd == "types":
        hist = {}
        for e in ref:
            t = e.get("type") if isinstance(e, dict) else "?"
            hist[t] = hist.get(t, 0) + 1
        for t, c in sorted(hist.items(), key=lambda kv: -kv[1]):
            print("%6d %s" % (c, t))
        return 0
    if cmd == "diff":
        eng = events(load(argv[1]))
        if len(argv) > 2:
            eng = eng[checkpoint_index(eng, argv[2]):]
            ref = ref[checkpoint_index(ref, argv[2]):]
        diff(ref, eng)
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
