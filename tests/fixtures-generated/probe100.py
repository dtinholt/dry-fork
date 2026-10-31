import json, sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from wlengine import scenario, maps

SC = os.path.join(os.path.dirname(__file__), "..", "..", "SPEC", "scenario")
d = tempfile.mkdtemp()
scenario.compile(SC, d)
sc = scenario.load(d)
m = sc.map(1)
print("size", m["size"])
for y in range(18, 23):
    row = []
    for x in range(0, 8):
        row.append((x, m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x],
                    maps.is_passable(m, x, y)))
    print(y, row)
