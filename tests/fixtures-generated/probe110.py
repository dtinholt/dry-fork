import sys, os, json, traceback
_OUT = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dump110.txt"), "w")
_print = print


def print(*a, **k):
    k.setdefault("file", _OUT)
    _print(*a, **k)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))

p = os.path.join(ROOT, "src", "wlengine", "headless.py")
lines = open(p).read().split("\n")
print("TOTAL headless", len(lines))
for a, b in [(1, 60), (440, 545), (680, 845), (940, len(lines))]:
    print("=== headless lines %d-%d ===" % (a, b))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))

for name in ("rules.py", "combat.py", "labstate.py"):
    p2 = os.path.join(ROOT, "src", "wlengine", name)
    l2 = open(p2).read().split("\n")
    print("=== %s (%d lines) ===" % (name, len(l2)))
    for i, s in enumerate(l2):
        print("%4d| %s" % (i + 1, s))

# ---- diagnostics -----------------------------------------------------------
import wl_support as W
import wl_combat_ref as CR

SCEN = W.SCENARIO
walkthrough = W.load_json(SCEN / "walkthrough.json")


def prefix(upto):
    out = []
    for item in walkthrough["script"]:
        out.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == upto:
            return out
    raise AssertionError("no checkpoint " + upto)


import tempfile
import shutil

_COMPILED = None


def compiled_dir():
    global _COMPILED
    if _COMPILED is None:
        d = tempfile.mkdtemp()
        W._armed(W.api("scenario.compile"), str(W.SCENARIO), d, allow_reference_log=True)
        _COMPILED = d
    return _COMPILED


def run(name, script, seed=20261021):
    d = tempfile.mkdtemp()
    shutil.copytree(compiled_dir(), d, dirs_exist_ok=True)
    try:
        ev = W.call("headless.run", d, {"seed": seed, "script": script}, seed)
    except Exception:
        traceback.print_exc()
        return []
    return ev


def show(ev, types=None):
    for e in ev:
        if types and e.get("type") not in types:
            continue
        print(json.dumps(e, default=str)[:300])


print("### bump")
ev = run("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}])
show(ev, ("input", "bump", "checkpoint", "map_change", "message", "paragraph"))

print("### storehouse (CP6)")
ev = run("cp6", prefix("CP6"))
show(ev, ("check", "unlock", "cell_change", "xp", "message", "paragraph", "bump"))

print("### healer (CP7)")
ev = run("cp7", prefix("CP7"))
show(ev, ("prompt", "money", "heal_all", "bump", "checkpoint"))

print("### key (CP9)")
ev = run("cp9", prefix("CP9"))
show(ev, ("bump", "message", "key_used", "unlock", "cell_change", "checkpoint"))

print("### victory loot")
ev = run("cp4", prefix("CP4"), seed=20261021)
show(ev, ("combat_end", "cell_change", "money", "loot", "xp"))
