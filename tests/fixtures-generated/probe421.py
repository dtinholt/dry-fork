"""Probe: introspect the scenario compiler API and dump Saltwell map cells.

Run: python3 tests/fixtures-generated/probe421.py
"""
import os
import sys
import json
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

print("ROOT:", ROOT)
print("root listing:", sorted(os.listdir(ROOT)))

for name in ("scenario", "maps", "headless", "containers"):
    try:
        mod = __import__("wlengine." + name, fromlist=["x"])
        print("== wlengine.%s public names:" % name)
        print("   ", sorted(n for n in dir(mod) if not n.startswith("_")))
    except Exception:
        traceback.print_exc()

# scenario source dir?
for cand in ("scenario", "scenario-src", "data", "SPEC"):
    p = os.path.join(ROOT, cand)
    if os.path.isdir(p):
        print("dir %s: %s" % (cand, sorted(os.listdir(p))[:40]))

# try to find a compiled data dir from earlier runs
for base in (os.path.join(ROOT, "tests", "fixtures-generated"), "/tmp"):
    if os.path.isdir(base):
        for entry in sorted(os.listdir(base))[:60]:
            full = os.path.join(base, entry)
            if os.path.isdir(full):
                try:
                    sub = sorted(os.listdir(full))
                except Exception:
                    continue
                if any(s.startswith("GAME") or s.endswith(".BIN") for s in sub):
                    print("candidate data dir:", full, sub[:20])

try:
    import wlengine.scenario as S
    print("scenario module file:", getattr(S, "__file__", None))
    for n in sorted(dir(S)):
        if n.startswith("_"):
            continue
        obj = getattr(S, n)
        print("  %s: %s" % (n, type(obj).__name__))
except Exception:
    traceback.print_exc()

# ---- look at the tests' helper module to learn how to build a runner ----
for cand in ("tests/support.py", "tests/conftest.py", "tests/wl.py", "tests/helpers.py"):
    p = os.path.join(ROOT, cand)
    if os.path.isfile(p):
        print("=== %s ===" % cand)
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            print(fh.read()[:6000])

# ---- dump the Saltwell map cells if we can compile ----
try:
    import wlengine.scenario as S
    print("scenario attrs:", [n for n in dir(S) if "compile" in n.lower() or "build" in n.lower()])
except Exception:
    pass

# ---- inspect the M5 test file header for the runner fixture ----
p = os.path.join(ROOT, "tests", "test_m5_rules.py")
if os.path.isfile(p):
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    print("=== test_m5_rules.py first 4000 chars ===")
    print(text[:4000])
