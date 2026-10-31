"""Command line entry point (SPEC-06 sections 5 and 7).

Usage:
    wl --headless --data DIR --script FILE [--seed N] --log OUT.jsonl
    wl --data DIR --render-frame

Exit codes (SPEC-06 5.1): 0 the script ran to its end; 2 a `repeat_until`
exceeded its `max`; 3 a data error; 4 a malformed script.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import headless, ui
from .errors import FormatError, RepeatLimitError, ScriptError


def build_parser():
    p = argparse.ArgumentParser(prog="wl", add_help=True)
    p.add_argument("--headless", action="store_true", help="run a script headless")
    p.add_argument("--data", default=None, help="directory of compiled data files")
    p.add_argument("--script", default=None, help="script file (JSON)")
    p.add_argument("--seed", type=int, default=None, help="override the script seed")
    p.add_argument("--log", default=None, help="write the JSON Lines event log here")
    p.add_argument("--render-frame", dest="render_frame", action="store_true",
                   help="render the first frame and exit")
    return p


def _events(result):
    if isinstance(result, tuple):
        return result[0]
    return result


def run_headless(args):
    if not args.data:
        print("--headless needs --data", file=sys.stderr)
        return 3
    if not args.script:
        print("--headless needs --script", file=sys.stderr)
        return 3
    try:
        with open(args.script, "r", encoding="utf-8") as fh:
            script = json.load(fh)
    except (OSError, ValueError) as exc:
        print("cannot read script: %s" % exc, file=sys.stderr)
        return 4
    if not isinstance(script, dict):
        print("script must be a JSON object", file=sys.stderr)
        return 4
    seed = args.seed if args.seed is not None else script.get("seed")
    options = dict(script)
    options["seed"] = seed
    try:
        events = _events(headless.run(args.data, options, seed))
    except RepeatLimitError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ScriptError as exc:
        print(str(exc), file=sys.stderr)
        return 4
    except FormatError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    lines = [json.dumps(e, separators=(", ", ": ")) for e in events]
    text = "\n".join(lines)
    if text:
        text += "\n"
    if args.log:
        try:
            with open(args.log, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as exc:
            print("cannot write log: %s" % exc, file=sys.stderr)
            return 3
    else:
        sys.stdout.write(text)
    return 0


def run_render_frame(args):
    if not args.data:
        print("--render-frame needs --data", file=sys.stderr)
        return 3
    try:
        frame = ui.render_frame(args.data)
    except FormatError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    sys.stdout.write("\n".join(frame) + "\n")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.render_frame:
        return run_render_frame(args)
    if args.headless:
        return run_headless(args)
    print("nothing to do: pass --headless or --render-frame", file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main())
