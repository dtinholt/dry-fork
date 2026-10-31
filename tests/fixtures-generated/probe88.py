"""Probe: dump items.json, shops.json, scenario.json, party.json, encounters.json,
npcs.json, hooks.json, skills.json and the monster tables of the four maps."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "dump88.txt"
SCEN = ROOT / "SPEC" / "scenario"


def main():
    out = []
    for name in ("items.json", "shops.json", "scenario.json", "party.json",
                 "encounters.json", "npcs.json", "hooks.json", "skills.json",
                 "paragraphs.json"):
        p = SCEN / name
        if not p.exists():
            out.append("==== %s MISSING ====" % name)
            continue
        out.append("==== %s ====" % name)
        out.append(json.dumps(json.loads(p.read_text()), indent=1))
        out.append("")
    for name in ("map0-overworld.json", "map1-saltwell.json", "map2-ninemile.json",
                 "map3-pumphouse.json"):
        p = SCEN / name
        data = json.loads(p.read_text())
        out.append("==== %s keys ====" % name)
        out.append(repr(sorted(data.keys())))
        for k in ("monsters", "mobs", "encounters", "info", "size"):
            if k in data:
                out.append("-- %s.%s --" % (name, k))
                out.append(json.dumps(data[k], indent=1))
        out.append("")
    OUT.write_text("\n".join(out) + "\n")
    print("wrote", OUT, len(out), "lines")


if __name__ == "__main__":
    main()
