import os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src"))
import wl_support as W

out = open(os.path.join(HERE, "dump112.txt"), "w")


def p(*a):
    print(*a, file=out)


SC = W.SCENARIO
p("SCENARIO DIR", SC)
p("files:", sorted(os.listdir(SC)))
for name in ("hooks.json", "LABHOOKS.JSON", "skills.json", "party.json", "items.json",
             "maps.json", "walkthrough.json", "shops.json", "monsters.json"):
    fp = SC / name
    if fp.exists():
        p("=== %s ===" % name)
        p(fp.read_text()[:6000])
for name in sorted(os.listdir(SC)):
    if name.endswith(".json") and name not in ("hooks.json", "skills.json", "party.json",
                                               "items.json", "maps.json", "walkthrough.json",
                                               "shops.json", "monsters.json"):
        p("=== %s ===" % name)
        p((SC / name).read_text()[:3000])
out.close()
