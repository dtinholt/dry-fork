"""Dump walkthrough scripts, reference-log combat events, scenario tables."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(ROOT, "SPEC", "scenario")
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump71.txt")


def j(name):
    with open(os.path.join(SC, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    out = []
    wt = j("walkthrough.json")
    out.append("walkthrough keys: %r" % list(wt.keys()))
    out.append(json.dumps(wt, indent=1)[:6000])
    log = j("walkthrough-reference-log.json")
    ev = log["events"]
    out.append("log keys %r n=%d" % (list(log.keys()), len(ev)))
    # find encounter_start
    idx = [i for i, e in enumerate(ev) if e.get("type") == "encounter_start"]
    out.append("encounter_start at %r" % idx)
    if idx:
        i = idx[0]
        for e in ev[i - 6:i + 90]:
            out.append(json.dumps(e))
    out.append("---- items")
    out.append(json.dumps(j("items.json"))[:3000])
    out.append("---- encounters")
    out.append(json.dumps(j("encounters.json"))[:3000])
    out.append("---- scenario")
    out.append(json.dumps(j("scenario.json"))[:3000])
    out.append("---- skills")
    out.append(json.dumps(j("skills.json"))[:3000])
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote", OUT, len(out))


if __name__ == "__main__":
    main()
