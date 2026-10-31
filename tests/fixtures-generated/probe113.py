import json, sys, os, shutil, tempfile
sys.path.insert(0, "src")
sys.path.insert(0, "tests")
import wl_support as W
from wlengine import headless, containers

SC = W.SCENARIO
wt = json.load(open(os.path.join(SC, "walkthrough.json")))

def prefix(upto):
    out = []
    for item in wt["script"]:
        out.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == upto:
            return out
    raise SystemExit("no cp " + upto)

src = sys.argv[1] if len(sys.argv) > 1 else "tests/fixtures-generated/dd"
dd = tempfile.mkdtemp()
shutil.copytree(src, dd, dirs_exist_ok=True)

script = prefix("CP5-pre-save") + ["S"]
ev = headless.run(dd, {"seed": 20261021, "script": script}, 20261021)
for e in ev:
    if e.get("type") in ("save", "load", "checkpoint", "prompt", "recruit", "money", "bump", "check"):
        print(json.dumps(e)[:300])
print("---")
t = containers.read_tables(os.path.join(dd, "LABTABLES.BIN"))
g = open(os.path.join(dd, "GAME1"), "rb").read()
off = t["savegameOffsets"][0]
p = containers.decode_savegame(g, off)
print("order", p["groups"][0]["order"])
print("x,y,map", p["groups"][0]["x"], p["groups"][0]["y"], p["groups"][0]["map"])
print("prev", p["groups"][0]["prevX"], p["groups"][0]["prevY"], p["groups"][0]["prevMap"])
print("viewport", p["viewportX"], p["viewportY"], "members", p["currentMembers"], p["totalMembers"])
print("min/hour", p["minute"], p["hour"], "serial", p["serial"])
print("names", [c["name"] for c in p["characters"]])
print("labstate exists", os.path.exists(os.path.join(dd, "LABSTATE.BIN")))
