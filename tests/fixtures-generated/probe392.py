"""Probe: reproduce the M5 bump_is_not_a_step failure and dump the move/bump
code paths of wlengine.headless so we can see where the extra step comes from.

Run: python3 tests/fixtures-generated/probe392.py
"""
import inspect
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wlengine.headless as H  # noqa: E402


def show_source(obj, name):
    fn = getattr(obj, name, None)
    if fn is None:
        print("!! no attribute", name)
        return
    try:
        src = inspect.getsource(fn)
    except Exception as e:  # noqa: BLE001
        print("!! cannot get source of", name, e)
        return
    print("=" * 70)
    print("### %s" % name)
    print("=" * 70)
    print(src)


def dump_sources():
    print("headless module file:", H.__file__)
    for name in ("move", "try_move", "step", "bump", "bump_effect", "bump_blocked",
                 "advance_clock", "look", "interact", "handle_key", "run_script"):
        show_source(H, name)
    for cls_name in dir(H):
        cls = getattr(H, cls_name)
        if inspect.isclass(cls) and cls.__module__ == H.__name__:
            print("class", cls_name, "methods:",
                  [m for m in dir(cls) if not m.startswith("_")])
            for m in ("move", "try_move", "step", "bump", "bump_effect", "bump_blocked",
                      "advance_clock", "look", "interact", "handle_key"):
                if hasattr(cls, m):
                    show_source(cls, m)


def reproduce():
    """Run the failing scenario directly and print the event stream."""
    try:
        import wl_support as W
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return
    print("wl_support:", W.__file__)
    print("scenario dir:", getattr(W, "SCENARIO", None))
    seed = None
    for cand in ("SEED", "SEED0"):
        if hasattr(W, cand):
            seed = getattr(W, cand)
            break
    print("seed:", seed)
    # find the runner fixture helper
    for name in dir(W):
        if "runner" in name.lower():
            print("wl_support has", name)
    try:
        from wlengine.headless import Headless
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return
    print("Headless:", Headless)
    try:
        h = Headless()
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return
    print("Headless instance methods:", [m for m in dir(h) if not m.startswith("_")])
    try:
        ev = h.run("bump", {"seed": seed, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return
    if isinstance(ev, tuple):
        ev = ev[0]
    for e in ev:
        print(json.dumps(e, default=str))


def main():
    dump_sources()
    reproduce()


if __name__ == "__main__":
    main()
