#!/usr/bin/env python3
"""Compare the engine's headless event log against the reference walkthrough log.

Usage:
    python3 tests/fixtures-generated/cmp.py --script bump --seed 20261021
    python3 tests/fixtures-generated/cmp.py --script full --from 200 --to 260

The reference log lives in SPEC/scenario/walkthrough-reference-log.json and is
frozen; the engine log is produced by running wlengine.headless over the
generated fixture directory tests/fixtures-generated/dd.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

REF = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")
DD = os.path.join(HERE, "dd")


def load_ref():
    with open(REF) as fh:
        return json.load(fh)


def engine_events(script, seed, data_dir=DD):
    from wlengine import headless
    return headless.run(data_dir, script=script, seed=seed)


def summarize(ev):
    t = ev.get("type")
    keys = sorted(k for k in ev if k != "type")
    bits = []
    for k in keys:
        v = ev[k]
        if isinstance(v, (list, dict)):
            v = json.dumps(v, sort_keys=True)
        bits.append("%s=%s" % (k, v))
    return "%s %s" % (t, " ".join(bits))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="full")
    ap.add_argument("--seed", type=int, default=20261021)
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=10 ** 9)
    ap.add_argument("--types", default=None)
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    ref = load_ref()
    ref_events = ref["events"] if isinstance(ref, dict) else ref
    if args.types:
        want = set(args.types.split(","))
        ref_events = [e for e in ref_events if e.get("type") in want]

    try:
        got = engine_events(args.script, args.seed)
    except Exception as exc:  # noqa: BLE001
        print("engine raised %s: %s" % (type(exc).__name__, exc))
        return 2

    lo, hi = args.lo, args.hi
    n = min(len(ref_events), len(got))
    shown = 0
    for i in range(n):
        if i < lo or i > hi:
            continue
        a, b = ref_events[i], got[i]
        if a == b:
            continue
        print("--- first difference at index %d" % i)
        print("ref: %s" % summarize(a))
        print("got: %s" % summarize(b))
        shown += 1
        if shown >= args.limit:
            break
    if shown == 0:
        print("no differences in [%d, %d] (ref %d events, engine %d events)"
              % (lo, hi, len(ref_events), len(got)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
