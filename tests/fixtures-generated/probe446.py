"""probe446: load the compiled map for location 1 and print row 20, plus the
rendered frame row for y=20, to see whether the compiled map matches the JSON."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402

d = tempfile.mkdtemp(prefix="probe446-")
W._armed(W.api("scenario.compile"), str(W.SCENARIO), d, allow_reference_log=True)

import wlengine.maps as M  # noqa: E402

print("load_map signature:", M.load_map.__doc__)
import inspect  # noqa: E402
print(inspect.signature(M.load_map))

# find the map file for location 1
print("files:", sorted(os.listdir(d)))
for name in sorted(os.listdir(d)):
    p = os.path.join(d, name)
    if os.path.isfile(p):
        print(name, os.path.getsize(p))

loc = json.load(open(os.path.join(d, "LOCATIONS.JSON"), encoding="utf-8"))
print("LOCATIONS.JSON:", json.dumps(loc)[:2000])
