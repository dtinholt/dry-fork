"""probe447: dump the COMPILED map for location 1 (image + actionClass rows 11
and 20), the rendered frame row 6, and the look event, to see whether the
compiled arrays are shifted relative to SPEC/scenario/map1-saltwell.json."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wl_support as W  # noqa: E402

d = tempfile.mkdtemp(prefix="probe447-")
W._armed(W.api("scenario.compile"), str(W.SCENARIO), d, allow_reference_log=True)

import wlengine.maps as M  # noqa: E402
import wlengine.ui as U  # noqa: E402

print("ui module:", U.__file__)
print("ui names:", [n for n in dir(U) if not n.startswith("_")])

# how does the engine find the map for a location?
print("load_map doc:", M.load_map.__doc__)
import inspect  # noqa: E402
print("load_map sig:", inspect.signature(M.load_map))

loc = json.load(open(os.path.join(d, "LOCATIONS.JSON"), encoding="utf-8"))
print("LOCATIONS.JSON:", json.dumps(loc)[:1500])

# try loading map 1
for args in ((d, 1), (d, 0), (os.path.join(d, "GAME1"), 1)):
    try:
        m = M.load_map(*args)
        print("load_map%r ok; keys=%s" % (args, sorted(m.keys())))
        cells = m["cells"]
        print("cell keys:", sorted(cells.keys()))
        for y in (11, 20):
            print("y=%d image     %s" % (y, cells["image"][y]))
            print("y=%d actionCls %s" % (y, cells["actionClass"][y]))
        break
    except Exception as e:  # noqa: BLE001
        print("load_map%r failed: %s: %s" % (args, type(e).__name__, e))

fr = W.call("ui.render_frame", d)
print("frame row 6:", repr(fr[6]))
print("frame row 6 cols 0..38:", repr(fr[6][:39]))

ev = W.call("headless.run", d, {"seed": 19880101, "script": ["L", "LEFT", {"checkpoint": "a"}]})
for e in ev:
    if e.get("type") in ("look", "input"):
        print(json.dumps(e, sort_keys=True))
