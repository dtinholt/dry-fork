"""probe290: introspect the headless/scenario/ui API surface.

Prints:
  * module-level names of wlengine.headless, wlengine.scenario, wlengine.ui
  * the source of headless.run and headless.Engine.new_game (if present)
  * the signature of scenario.load and the attributes of the returned object
  * what a fresh new game looks like (events + state keys)
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from wlengine import headless, scenario, ui  # noqa: E402


def show(mod, name):
    print("=" * 70)
    print("MODULE", name)
    print("=" * 70)
    for n in sorted(dir(mod)):
        if n.startswith("__"):
            continue
        obj = getattr(mod, n)
        kind = type(obj).__name__
        if inspect.isfunction(obj) or inspect.isclass(obj):
            try:
                sig = str(inspect.signature(obj))
            except Exception:
                sig = "(?)"
            print("  %-28s %-10s %s" % (n, kind, sig))
        else:
            print("  %-28s %-10s %r" % (n, kind, obj))


show(headless, "wlengine.headless")
show(scenario, "wlengine.scenario")
show(ui, "wlengine.ui")

print("=" * 70)
print("SOURCE headless.run")
print("=" * 70)
try:
    print(inspect.getsource(headless.run))
except Exception as e:
    print("no run:", e)

print("=" * 70)
print("SOURCE Engine.new_game / start")
print("=" * 70)
for n in ("new_game", "start", "start_new_game", "reset"):
    fn = getattr(headless.Engine, n, None)
    if fn is not None:
        print("--- Engine.%s ---" % n)
        try:
            print(inspect.getsource(fn))
        except Exception as e:
            print("?", e)

print("=" * 70)
print("SOURCE scenario.load")
print("=" * 70)
try:
    print(inspect.getsource(scenario.load))
except Exception as e:
    print("no load:", e)

# Try to build a scenario from the compiled data dir if one is around.
cands = []
for root in (os.path.join(os.path.dirname(__file__), "..", ".."),):
    for dirpath, dirnames, filenames in os.walk(root):
        if "LABTABLES.BIN" in filenames:
            cands.append(dirpath)
print("=" * 70)
print("compiled dirs found:", cands[:5])
if cands:
    dd = cands[0]
    print("using", dd)
    try:
        sc = scenario.load(dd)
        print("scenario type:", type(sc))
        print("scenario attrs:", [a for a in dir(sc) if not a.startswith("_")])
        for a in ("maps", "map", "locations", "start", "party", "premade"):
            if hasattr(sc, a):
                print("  sc.%s = %r" % (a, getattr(sc, a)))
    except Exception as e:
        import traceback
        traceback.print_exc()
    try:
        ev, st = headless.run(dd, {"seed": 20261021}, 20261021)
        print("run events[:6]:", ev[:6])
        print("state keys:", sorted(st.keys()) if isinstance(st, dict) else type(st))
        print("state:", st)
    except Exception:
        import traceback
        traceback.print_exc()
