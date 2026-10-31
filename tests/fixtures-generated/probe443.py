"""probe443: compile the scenario, run the look/bump scripts, and dump the
compiled map rows 19..21 to see where the road and the cactus really are."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402

SEED = 19880101
d = tempfile.mkdtemp(prefix="probe443-")
fn = W.api("scenario.compile")
W._armed(fn, str(W.SCENARIO), d, allow_reference_log=True)
print("compiled to", d)
print("files:", sorted(os.listdir(d)))

# ---- compiled map ----------------------------------------------------------
import wlengine.maps as M  # noqa: E402

print("maps module:", M.__file__)
print([n for n in dir(M) if not n.startswith("_")])

# try to find the map loader
for name in ("load_map", "read_map", "Map", "load"):
    print(name, getattr(M, name, None))

# ---- headless runs ---------------------------------------------------------
for key, script in (("look", ["L", "LEFT", {"checkpoint": "a"}]),
                    ("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}])):
    ev = W.call("headless.run", d, {"seed": SEED, "script": script})
    print("=== %s ===" % key)
    for e in ev:
        print(json.dumps(e, sort_keys=True))
