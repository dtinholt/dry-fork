"""probe449: run the engine for the two failing scripts and dump everything.

Also dump the reference log's events touching row 20 and the compiled map row 20.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wlengine.scenario as scenario  # noqa: E402
import wlengine.headless as headless  # noqa: E402

SCEN = ROOT / "SPEC" / "scenario"


def compile_data():
    d = tempfile.mkdtemp(prefix="probe449-")
    scenario.compile(str(SCEN), d)
    return d


def main():
    d = compile_data()
    print("compiled to", d)
    print("files:", sorted(os.listdir(d)))
    # dump the compiled map row 20
    sc = scenario.load(d)
    m = sc.map(1)
    print("map1 size", m["size"])
    print("image row20:", m["cells"]["image"][20])
    print("class row20:", m["cells"]["actionClass"][20])
    print("action row20:", m["cells"]["action"][20])
    print("image row11:", m["cells"]["image"][11])
    print("class row11:", m["cells"]["actionClass"][11])
    print("image row31:", m["cells"]["image"][31])
    print("class row31:", m["cells"]["actionClass"][31])

    for name, script in (("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
                         ("look", ["L", "LEFT", {"checkpoint": "a"}])):
        dd = tempfile.mkdtemp(prefix="probe449-run-")
        import shutil
        shutil.copytree(d, dd, dirs_exist_ok=True)
        ev = headless.run(dd, json.dumps({"seed": 20261021, "script": script}))
        print("=== %s ===" % name)
        for e in ev:
            print(json.dumps(e))

    ref = json.loads((SCEN / "walkthrough-reference-log.json").read_text())
    print("=== reference log events with y==20 or type look ===")
    for e in ref["events"]:
        if e.get("y") == 20 or e.get("type") == "look":
            print(json.dumps(e))
    print("=== reference log first 5 events ===")
    for e in ref["events"][:5]:
        print(json.dumps(e))


if __name__ == "__main__":
    main()
