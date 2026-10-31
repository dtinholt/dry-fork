"""Probe 422: dump Saltwell (location 1) cells around row 20 and the look image."""
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import wlengine.scenario as S
import wlengine.maps as M

dd = os.path.join(ROOT, "tests", "fixtures-generated", "dd")
sc = S.load(dd)
m = sc.map(1)
print("size", m["size"])
print("info", m["info"])
cells = m["cells"]
print("cell keys", sorted(cells.keys()))
for y in range(18, 23):
    row = []
    for x in range(0, 8):
        row.append((x, cells["actionClass"][y][x], cells["action"][y][x], cells["image"][y][x]))
    print("y=%d" % y, row)
print("--- records ---")
for y in range(18, 23):
    for x in range(0, 8):
        r = M.record_at(m, x, y)
        if r is not None:
            print("rec", x, y, {k: v for k, v in r.items() if k != "messages"})
print("--- passable ---")
for y in range(18, 23):
    print("y=%d" % y, [M.is_passable(m, x, y) for x in range(0, 8)])
print("--- image_at ---")
for y in range(18, 23):
    print("y=%d" % y, [M.image_at(m, x, y) for x in range(0, 8)])
