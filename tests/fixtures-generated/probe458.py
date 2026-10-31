"""Compare SPEC-05 Saltwell ASCII art with SPEC/scenario/map1-saltwell.json.

Prints, for a few rows, the JSON tiles/action_class/action_value with x indices,
and the ASCII art characters with string indices, so we can see any column shift.

Also dumps the engine's view of the compiled map around (14..16, 19..21) and
runs a look/move probe so we can see whether the engine agrees with the JSON.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
sys.path.insert(0, str(ROOT / "src"))


def ascii_rows(section_title):
    txt = (SPEC / "SPEC-05-scenario.md").read_text(encoding="utf-8")
    i = txt.index(section_title)
    seg = txt[i:]
    m = re.search(r"```text\n(.*?)```", seg, re.S)
    block = m.group(1)
    rows = {}
    for line in block.split("\n"):
        mm = re.match(r"^\s*(\d+)\s+(.*)$", line)
        if mm:
            rows[int(mm.group(1))] = mm.group(2)
    return rows


def main():
    rows = ascii_rows("### 5.2 Saltwell")
    print("ascii rows:", sorted(rows)[:5], "...", sorted(rows)[-3:])
    for y in (0, 1, 2, 7, 9, 11, 20, 30, 31):
        r = rows.get(y)
        if r is None:
            continue
        print("ascii y=%2d len=%d %r" % (y, len(r), r))
        marks = [(x, c) for x, c in enumerate(r) if c not in ".|"]
        print("   non-plain at string idx:", marks)

    d = json.loads((SPEC / "scenario" / "map1-saltwell.json").read_text())
    tiles = d["tiles"]
    aclass = d["action_class"]
    aval = d["action_value"]
    print("json width/height:", d["width"], d["height"])
    for y in (0, 1, 2, 7, 9, 11, 20, 30, 31):
        print("json y=%2d tiles=%s" % (y, tiles[y]))
        print("        class=%s" % (aclass[y],))
        print("        value=%s" % (aval[y],))
    print("action_cells:")
    for c in d["action_cells"]:
        print("   ", c)
    print("records keys:", sorted(d["records"].keys()))

    # engine view
    try:
        from wlengine import scenario as S
    except Exception as e:  # pragma: no cover
        print("import scenario failed:", e)
        return
    print("scenario module attrs:", [a for a in dir(S) if not a.startswith("_")][:40])


if __name__ == "__main__":
    main()
