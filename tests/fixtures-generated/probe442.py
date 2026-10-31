"""probe442: compare SPEC-05 5.2 ASCII art with SPEC/scenario/map1-saltwell.json
and with the engine's compiled map, column by column, to locate the off-by-one
that makes test_bump_is_not_a_step and test_look fail."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

SPEC = os.path.join(ROOT, "SPEC")

# ---- 1. the ASCII art ------------------------------------------------------
text = open(os.path.join(SPEC, "SPEC-05-scenario.md"), encoding="utf-8").read()
m = re.search(r"### 5\.2 Saltwell.*?```text\n(.*?)```", text, re.S)
art = m.group(1).splitlines()
rows = []
for line in art:
    mm = re.match(r"\s*(\d+)\s\s(.*)$", line)
    if mm:
        rows.append((int(mm.group(1)), mm.group(2)))
print("ascii rows:", len(rows))
for y, s in rows[:3]:
    print(y, len(s), repr(s))

# ---- 2. the JSON -----------------------------------------------------------
d = json.load(open(os.path.join(SPEC, "scenario", "map1-saltwell.json"), encoding="utf-8"))
print("json keys:", sorted(d.keys()))
tiles = d["tiles"]
print("json dims:", len(tiles), len(tiles[0]))

# ---- 3. compare ------------------------------------------------------------
CH = {".": 0, "#": 196, ";": 18, "Y": 11, "T": 11, "b": 11, "p": 11, "P": 23, "w": 11, "n": 22, "h": 22, "_": 0, "/": 0}
for y, s in rows:
    jrow = tiles[y]
    diffs = []
    for x in range(len(s)):
        c = s[x]
        if c == "|":
            want = 196
        else:
            want = CH.get(c, 0)
        got = jrow[x] if x < len(jrow) else None
        if got != want:
            diffs.append((x, c, want, got))
    print("row %2d diffs=%d %s" % (y, len(diffs), diffs[:12]))

# ---- 4. engine compiled map ------------------------------------------------
import wl_support as W  # noqa: E402

print("SRC:", W.SRC)
try:
    import wlengine.scenario as S  # noqa: E402
    print("scenario module:", S.__file__)
    print([n for n in dir(S) if not n.startswith("_")])
except Exception as e:  # noqa: BLE001
    print("import failed:", e)
