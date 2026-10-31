"""Probe 341: find which map/cell gives image 28 at (14,20) or (20,14), and
which gives class 11 at (2,20)/(20,2).  Also dump the walkthrough script tokens
around any 'L' token.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCEN = ROOT / "SPEC" / "scenario"

for name in ("map0-overworld", "map1-saltwell", "map2-ninemile", "map3-pumphouse"):
    m = json.loads((SCEN / (name + ".json")).read_text())
    t = m["tiles"]
    ac = m["action_class"]
    print("== %s  w=%s h=%s" % (name, m.get("width"), m.get("height")))
    print("   tiles[20][14]=%s ac=%s   tiles[14][20]=%s ac=%s" % (t[20][14], ac[20][14], t[14][20], ac[14][20]))
    print("   tiles[20][2]=%s ac=%s    tiles[2][20]=%s ac=%s" % (t[20][2], ac[20][2], t[2][20], ac[2][20]))
    # where is tile 18 (image 28) in row 20?
    row = t[20]
    print("   row20 tiles:", row)
    print("   row20 ac   :", ac[20])
    col = [t[y][14] for y in range(len(t))]
    print("   col14 tiles:", col)
    print("   col14 ac   :", [ac[y][14] for y in range(len(t))])

wt = json.loads((SCEN / "walkthrough.json").read_text())
script = wt["script"]
print("walkthrough script tokens:", [s if isinstance(s, str) else list(s.keys())[0] for s in script])
print("token_rules:", json.dumps(wt.get("token_rules"), indent=1)[:2000])
