#!/usr/bin/env python3
"""Diagnostic harness for the M5/M6 headless engine.

Usage:
    python3 tests/fixtures-generated/analyze.py <fixture-dir> [--seed N] [--script NAME]

Runs the walkthrough script (or a named short script) through
wlengine.headless.run and prints the resulting event log in a compact form so
that failures can be inspected without re-reading the frozen tests.

Options:
    --seed N        override the seed
    --script NAME   one of: opening, bump, rest, pump, cp2, cp3, cp4, cp6,
                    cp7, cp9, full
    --from NAME     start printing at the first checkpoint with this name
    --to NAME       stop printing at the first checkpoint with this name
    --types T,T     only print events whose type is in this list
    --limit N       print at most N events (default 400)
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

from wlengine import headless  # noqa: E402

SCEN = os.path.join(ROOT, "SPEC", "scenario")


def load_walkthrough():
    with open(os.path.join(SCEN, "walkthrough.json")) as fh:
        return json.load(fh)


def prefix(walkthrough, upto):
    out = []
    for item in walkthrough["script"]:
        out.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == upto:
            return out
    raise SystemExit("no checkpoint %s" % upto)


def opening_script(walkthrough):
    out = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            return out + ["A"]
        out.append(item)
    raise SystemExit("no repeat_until macro")


def build_script(name, walkthrough):
    if name == "full":
        return walkthrough["script"]
    if name == "opening":
        return opening_script(walkthrough)
    if name == "bump":
        return ["LEFT"] * 13 + [{"checkpoint": "a"}]
    if name == "rest":
        return ["R", {"checkpoint": "a"}]
    if name == "pump":
        return ["UP"] * 9 + [{"checkpoint": "a"}]
    if name.startswith("cp"):
        return prefix(walkthrough, name.upper())
    raise SystemExit("unknown script %r" % name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fixture")
    ap.add_argument("--seed", type=int, default=20261021)
    ap.add_argument("--script", default="full")
    ap.add_argument("--from", dest="frm", default=None)
    ap.add_argument("--to", dest="to", default=None)
    ap.add_argument("--types", default=None)
    ap.add_argument("--limit", type=int, default=400)
    args = ap.parse_args()

    walkthrough = load_walkthrough()
    script = build_script(args.script, walkthrough)
    types = set(args.types.split(",")) if args.types else None

    ev = headless.run(args.fixture, {"seed": args.seed, "script": script}, args.seed)

    started = args.frm is None
    printed = 0
    for e in ev:
        if e.get("type") == "checkpoint":
            if args.frm and e.get("name") == args.frm:
                started = True
            if args.to and e.get("name") == args.to:
                print("== checkpoint %s ==" % e.get("name"))
                st = e.get("state") or {}
                for k in sorted(st):
                    print("   %s = %r" % (k, st[k]))
                break
        if not started:
            continue
        if types and e.get("type") not in types:
            continue
        printed += 1
        if printed > args.limit:
            print("... (limit reached)")
            break
        print(json.dumps(e, sort_keys=True))


if __name__ == "__main__":
    main()
