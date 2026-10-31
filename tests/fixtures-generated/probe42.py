"""Compare JSON rows with the SPEC-05 art and run the bump script.

Usage: python3 tests/fixtures-generated/probe42.py
"""
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402


def art_rows(section="### 5.2 Saltwell", n=4000):
    txt = (ROOT / "SPEC" / "SPEC-05-scenario.md").read_text()
    i = txt.index(section)
    seg = txt[i:i + n]
    rows = {}
    for ln in seg.splitlines():
        m = re.match(r"^\s*(\d+)\s*\|(.*)\|\s*$", ln)
        if m:
            rows[int(m.group(1))] = m.group(2)
    return rows


def main():
    rows = art_rows()
    m = json.load(open(ROOT / "SPEC" / "scenario" / "map1-saltwell.json"))
    for y in (1, 20, 31):
        print("y=%d art : %s" % (y, rows.get(y)))
        print("     tile: %s" % " ".join("%2d" % v for v in m["tiles"][y]))
        print("     cls : %s" % " ".join("%2d" % v for v in m["action_class"][y]))
        print("     act : %s" % " ".join("%2d" % v for v in m["action_value"][y]))
    # run the bump script
    d = Path(tempfile.mkdtemp())
    from wlengine import scenario as sc
    sc.compile(str(W.SCENARIO), str(d))
    ev = W.call("headless.run", str(d), {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]},
                20261021)
    for e in ev:
        print(json.dumps(e)[:200])


if __name__ == "__main__":
    main()
