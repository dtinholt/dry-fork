"""Probe the compiled Saltwell map around the cactus and run the bump script."""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from wlengine import scenario, headless  # noqa: E402

d = tempfile.mkdtemp()
scenario.compile(os.path.join(ROOT, "SPEC", "scenario"), d)
sc = scenario.load(d)
m = sc.map(1)
print("size", m["size"])
for y in (19, 20, 21):
    print("y=%d tiles" % y, m["cells"]["image"][y][:8], "ac", m["cells"]["actionClass"][y][:8])
print("start", sc.start)
ev = headless.run(d, {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
for e in ev[-6:]:
    print(json.dumps(e)[:300])
