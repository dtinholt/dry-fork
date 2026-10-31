import json, sys, os, shutil, tempfile
sys.path.insert(0, "src")
sys.path.insert(0, "tests")
import wl_support as W
from wlengine import headless

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
upto = sys.argv[2] if len(sys.argv) > 2 else "CP6"
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20261021
frm = sys.argv[4] if len(sys.argv) > 4 else "CP5"
dd = tempfile.mkdtemp()
shutil.copytree(src, dd, dirs_exist_ok=True)

script = prefix(upto)
ev = headless.run(dd, {"seed": seed, "script": script}, seed)
start = 0
for i, e in enumerate(ev):
    if e.get("type") == "checkpoint" and e.get("name") == frm:
        start = i
for e in ev[start:]:
    if e.get("type") in ("checkpoint", "check", "bump", "message", "unlock", "cell_change", "paragraph", "prompt", "money", "heal_all", "key_used", "map_change", "blocked", "ignored", "input"):
        print(json.dumps(e)[:260])
