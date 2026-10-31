"""Probe: is the reference log consistent with the JSON map or with a map
shifted left by one column?  Also dump the reference log around the NPC bump."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "SPEC"
j = json.load(open(SPEC / "scenario" / "map1-saltwell.json"))
tiles, cls, act = j["tiles"], j["action_class"], j["action_value"]

print("json tiles[17]   ", tiles[17])
print("json class[17]   ", cls[17])
print("json action[17]  ", act[17])
print("json tiles[20]   ", tiles[20])
print("json class[20]   ", cls[20])
print("json action_cells:")
for c in j["action_cells"]:
    print("   ", c)

ref = json.load(open(SPEC / "scenario" / "walkthrough-reference-log.json"))["events"]
print("--- reference log seq 118..140")
for e in ref:
    if 118 <= e.get("seq", -1) <= 140:
        print(json.dumps(e, sort_keys=True))

# simulate the walkthrough moves under both orientations
wt = json.load(open(SPEC / "scenario" / "walkthrough.json"))
script = wt["script"]
start = json.load(open(SPEC / "scenario" / "scenario.json"))["start"]
print("start", start)

def sim(shift):
    x, y, loc = start["x"], start["y"], start["location"]
    maps = {}
    for i in range(4):
        maps[i] = json.load(open(SPEC / "scenario" / ("map%d-%s.json" % (i, ["overworld", "saltwell", "ninemile", "pumphouse"][i]))))
    out = []
    for tok in script:
        if not isinstance(tok, str) or tok not in ("UP", "DOWN", "LEFT", "RIGHT"):
            continue
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}[tok]
        nx, ny = x + dx, y + dy
        m = maps[loc]
        sx = nx + shift
        if not (0 <= sx < m["width"] and 0 <= ny < m["height"]):
            out.append(("bump", x, y, nx, ny, "oob"))
            continue
        c = m["action_class"][ny][sx]
        t = m["tiles"][ny][sx]
        if c == 11 or (c == 4 and False):
            out.append(("bump", x, y, nx, ny, c))
        else:
            x, y = nx, ny
            out.append(("move", x, y))
    return out

for shift in (0, -1):
    s = sim(shift)
    # compare with the reference log's move/bump sequence
    refseq = [(e["type"], e.get("x"), e.get("y")) for e in ref if e.get("type") in ("move", "bump")]
    got = [(t, (a[1] if t == "move" else a[3]), (a[2] if t == "move" else a[4])) for t, *a in s]
    n = min(len(refseq), len(got))
    first = next((i for i in range(n) if refseq[i] != got[i]), None)
    print("shift", shift, "len ref", len(refseq), "len got", len(got), "first diff", first,
          refseq[first] if first is not None else None, got[first] if first is not None else None)
