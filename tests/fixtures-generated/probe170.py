"""Probe 170: bump scenario events + Saltwell cells around (2..6, 20).

Also dumps the raider fight orders for seed 3 and the save/load payload, so
one run gives us the three M5 failures at once.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import wlengine.headless as H  # noqa: E402
import wlengine.maps as M  # noqa: E402
import wlengine.containers as C  # noqa: E402

SRC = os.path.join(ROOT, "tests", "fixtures-generated", "dd")
if not os.path.isdir(SRC):
    SRC = os.path.join(ROOT, "tests", "fixtures-generated", "dd117")

SEED = 20261021


def fresh():
    d = tempfile.mkdtemp(prefix="probe170-")
    shutil.copytree(SRC, d, dirs_exist_ok=True)
    return d


def dump_events(tag, ev):
    print("=== events (%s) ===" % tag)
    for e in ev:
        print(json.dumps(e, sort_keys=True))


def main():
    dd = fresh()
    ev = H.run(dd, {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    dump_events("bump", ev)

    m = M.load_map(SRC, 1)
    print("=== Saltwell cells y=20, x=0..8 ===")
    for x in range(0, 9):
        cls = m["cells"]["actionClass"][20][x]
        act = m["cells"]["action"][20][x]
        img = m["cells"]["image"][20][x]
        print("x=%d class=%d action=%d image=%d passable=%s" % (x, cls, act, img, M.is_passable(m, x, 20)))
    print("=== Saltwell cells y=19..21, x=2..5 ===")
    for y in range(19, 22):
        row = []
        for x in range(2, 6):
            row.append((m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x]))
        print("y=%d %s" % (y, row))

    # ---- raider fight orders, seed 3 --------------------------------
    print("=== raider fight seed 3 ===")
    try:
        dd2 = fresh()
        ev2 = H.run(dd2, {"seed": 3, "script": ["F", {"checkpoint": "a"}]})
        dump_events("fight3", ev2)
    except Exception as exc:  # noqa: BLE001
        print("fight run failed: %r" % (exc,))

    # ---- save / load -------------------------------------------------
    print("=== save/load ===")
    try:
        dd3 = fresh()
        ev3 = H.run(dd3, {"seed": SEED, "script": ["S", {"checkpoint": "a"}]})
        dump_events("save", ev3)
        t = C.read_tables(os.path.join(dd3, "LABTABLES.BIN"))
        g = open(os.path.join(dd3, "GAME1"), "rb").read()
        off = t["savegameOffsets"][0]
        payload = C.rxor_decode_whole(g, 0x800, off + 4)
        print("payload len", len(payload))
        print("payload head", payload[:64].hex())
        ls = open(os.path.join(dd3, "LABSTATE.BIN"), "rb").read()
        print("labstate len", len(ls), ls[:64].hex())
    except Exception as exc:  # noqa: BLE001
        print("save run failed: %r" % (exc,))


main()
