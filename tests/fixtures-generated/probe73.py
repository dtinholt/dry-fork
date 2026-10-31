"""Dump CP3/CP4 checkpoint states, items, encounters, map0 mobs."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump73.txt")


def j(name):
    with open(os.path.join(SC, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    out = []
    log = j("walkthrough-reference-log.json")["events"]
    for e in log:
        if e.get("type") == "checkpoint" and e.get("name") in ("CP3", "CP4"):
            out.append("---- %s" % e["name"])
            out.append(json.dumps(e["state"], indent=1))
    out.append("---- items.json")
    out.append(json.dumps(j("items.json"), indent=1))
    out.append("---- encounters.json")
    out.append(json.dumps(j("encounters.json"), indent=1))
    out.append("---- skills.json")
    out.append(json.dumps(j("skills.json"), indent=1))
    out.append("---- map0 mobs")
    m0 = j("map0-overworld.json")
    out.append("keys %r" % list(m0.keys()))
    out.append(json.dumps({k: v for k, v in m0.items() if k in ("monsters", "mobs", "encounters", "info")}, indent=1)[:4000])
    out.append("---- scenario.json")
    out.append(json.dumps(j("scenario.json"), indent=1)[:2000])
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote", OUT, len(out))


if __name__ == "__main__":
    main()
