"""Probe 217: gather the three M5 failures' raw data."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump217.txt"
SC = ROOT / "SPEC" / "scenario"


def main():
    with OUT.open("w") as f:
        m = W.load_json(SC / "map1-saltwell.json")
        for y in (19, 20, 21):
            f.write("row %d tiles      %s\n" % (y, m["tiles"][y][:8]))
            f.write("row %d actionClass %s\n" % (y, m["action_class"][y][:8]))
            f.write("row %d actionValue %s\n" % (y, m["action_value"][y][:8]))
        f.write("width=%s height=%s\n" % (m["width"], m["height"]))
        f.write("action_cells=%s\n" % json.dumps(m["action_cells"])[:3000])
        f.write("records=%s\n" % json.dumps(m["records"])[:3000])
        f.write("\n")

        wt = W.load_json(SC / "walkthrough.json")
        f.write("walkthrough keys=%s\n" % list(wt.keys()))
        f.write("script len=%d\n" % len(wt["script"]))
        f.write("checkpoints=%s\n" % json.dumps(wt.get("checkpoints"))[:3000])
        f.write("\n")

        ref = SC / "walkthrough-reference-log.json"
        f.write("ref exists=%s\n" % ref.is_file())
        if ref.is_file():
            data = W.load_json(ref)
            f.write("ref type=%s\n" % type(data).__name__)
            if isinstance(data, dict):
                f.write("ref keys=%s\n" % list(data.keys()))
            else:
                f.write("ref len=%d\n" % len(data))
                for e in data[:5]:
                    f.write("  %s\n" % json.dumps(e)[:300])
    print("wrote", OUT)


main()
