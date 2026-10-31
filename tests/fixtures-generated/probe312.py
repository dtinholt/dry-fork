"""Probe 312: map info keys, location name, tiles, border image; and the
reference log's repeat_until behaviour.

Run: python3 tests/fixtures-generated/probe312.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "src"))

from wlengine import headless, scenario  # noqa: E402

SCEN = os.path.join(PROJ, "SPEC", "scenario")


def main():
    dd = tempfile.mkdtemp(prefix="probe312-")
    scenario.compile(SCEN, dd)
    sc = headless._load_scenario(dd)
    m = sc.map(1)
    print("info:", json.dumps(m["info"], default=str)[:1200])
    print("cells keys:", list(m["cells"].keys()))
    print("tiles[20][13:17]:", m["cells"]["image"][20][13:17])
    print("actionClass[20][13:17]:", m["cells"]["actionClass"][20][13:17])
    print("map_string(1, ...) sample:")
    for i in range(1, 6):
        try:
            print("  ", i, repr(sc.map_string(1, i)))
        except Exception as e:
            print("  ", i, "err", e)
    # find Saltwell
    for i in range(1, 40):
        try:
            s = sc.map_string(1, i)
        except Exception:
            break
        if s and "Saltwell" in s:
            print("Saltwell at map string", i, repr(s))
    print("labstr[0][:6]:", sc.labstr[0][:6])
    # ui attr
    print("sc.ui:", json.dumps(sc.ui, default=str)[:500])

    # reference log: count A inputs and look at repeat macros
    ref = json.load(open(os.path.join(SCEN, "walkthrough-reference-log.json")))
    print("ref events:", len(ref))
    idxs = [i for i, e in enumerate(ref) if e.get("type") == "input" and e.get("key") == "A"]
    print("A inputs at:", idxs)
    # print events around first A run
    if idxs:
        lo = max(0, idxs[0] - 3)
        hi = min(len(ref), idxs[-1] + 3)
        for i in range(lo, min(lo + 12, len(ref))):
            print(i, json.dumps(ref[i])[:160])


main()
