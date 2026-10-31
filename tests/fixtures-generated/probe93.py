"""Dump the scenario JSON action_cells and check grid orientation."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SC = os.path.join(ROOT, "SPEC", "scenario")


def main():
    d = json.load(open(os.path.join(SC, "map1-saltwell.json")))
    print("action_cells:")
    for c in d["action_cells"]:
        print("  ", json.dumps(c))
    print()
    print("records:")
    for k, v in d["records"].items():
        print("  ", k, json.dumps(v)[:200])
    print()
    d0 = json.load(open(os.path.join(SC, "map0-overworld.json")))
    ac0 = d0["action_class"]
    print("overworld ac[41][30]=", ac0[41][30], " ac[30][41]=", ac0[30][41])
    print("overworld action_cells sample:")
    for c in d0["action_cells"][:20]:
        print("  ", json.dumps(c))
    print("overworld non-plain cells:")
    for c in d0["action_cells"]:
        if c.get("class") not in (0, 11):
            print("  ", json.dumps(c))


if __name__ == "__main__":
    main()
