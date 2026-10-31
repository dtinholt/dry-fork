"""Local helper: run the engine over a compiled data dir and diff the event log
against SPEC/scenario/walkthrough-reference-log.json.

Usage:
  python3 tests/fixtures-generated/difftool.py [data_dir] [--full] [--from N]
                                              [--grep TYPE] [--limit N]
  python3 tests/fixtures-generated/difftool.py --dump [data_dir]   # print got log

Options:
  --full        print every mismatch (default: first 25)
  --from N      start the comparison at event index N
  --limit N     stop after N mismatches
  --grep TYPE   only report mismatches whose ref or got event type contains TYPE
  --dump        print the engine's event log instead of diffing
  --ref         print the reference event log
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wlengine.headless as H  # noqa: E402


def load_ref():
    p = os.path.join(ROOT, "SPEC", "scenario", "walkthrough-reference-log.json")
    return json.load(open(p))["events"]


def load_script():
    p = os.path.join(ROOT, "SPEC", "scenario", "walkthrough.json")
    return json.load(open(p))


def expand(wt):
    """Expand the walkthrough script into a flat token list with checkpoints."""
    out = []
    for item in wt["script"]:
        if isinstance(item, dict):
            if "checkpoint" in item:
                out.append(item)
            elif "repeat_until" in item:
                out.append(item)
        else:
            out.append(item)
    return out


def strip(ev):
    if ev is None:
        return None
    return {k: v for k, v in ev.items() if k != "seq"}


def run_engine(dd):
    wt = load_script()
    script = expand(wt)
    return H.run(dd, {"seed": wt["seed"], "script": script}, wt["seed"])


def main():
    argv = sys.argv[1:]
    opts = {}
    args = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            name = a[2:]
            if name in ("from", "limit", "grep"):
                i += 1
                opts[name] = argv[i]
            else:
                opts[name] = True
        else:
            args.append(a)
        i += 1
    dd = args[0] if args else os.path.join(HERE, "dd")
    ref = load_ref()
    events = run_engine(dd)
    if opts.get("ref"):
        for i, ev in enumerate(ref):
            print("%4d %s" % (i, json.dumps(strip(ev))[:400]))
        return
    if opts.get("dump"):
        for i, ev in enumerate(events):
            print("%4d %s" % (i, json.dumps(strip(ev))[:400]))
        print("total got=%d ref=%d" % (len(events), len(ref)))
        return
    start = int(opts.get("from", 0))
    limit = int(opts.get("limit", 25))
    grep = opts.get("grep")
    n = max(len(ref), len(events))
    bad = 0
    shown = 0
    for i in range(start, n):
        a = strip(ref[i] if i < len(ref) else None)
        b = strip(events[i] if i < len(events) else None)
        if a == b:
            continue
        bad += 1
        if grep:
            ta = (a or {}).get("type", "")
            tb = (b or {}).get("type", "")
            if grep not in ta and grep not in tb:
                continue
        shown += 1
        if shown <= limit or opts.get("full"):
            print("--- event %d" % i)
            print("ref: %s" % json.dumps(a)[:600])
            print("got: %s" % json.dumps(b)[:600])
    print("total events ref=%d got=%d mismatches=%d" % (len(ref), len(events), bad))


if __name__ == "__main__":
    main()
