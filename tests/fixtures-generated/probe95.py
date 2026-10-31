"""Probe 95: party, items, mobs from the compiled data dir."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

from wlengine import headless  # noqa: E402

DD = os.path.join(HERE, "dd")


def main():
    out = []
    eng = headless.Engine(DD, seed=20261021)
    eng.new_game(20261021)
    out.append("start: %r" % (eng.sc.start,))
    for m in eng.party:
        out.append(json.dumps({k: v for k, v in m.items() if k != "attrs"}))
        out.append("   attrs %r" % (m.get("attrs"),))
    out.append("items table:")
    for i in range(1, 13):
        out.append("  %d %r" % (i, eng.item_record(i)))
    for loc in range(4):
        m = eng.sc.map(loc)
        out.append("map %d size %r mobs %r" % (loc, m["size"], m.get("mobs")))
        out.append("   info %r" % (m["info"],))
    out.append("hooks %r" % (eng.sc.hooks,))
    out.append("skill_table %r" % (getattr(eng.sc, "skill_table", None),))
    text = "\n".join(out)
    with open(os.path.join(HERE, "dump95.txt"), "w") as fh:
        fh.write(text + "\n")
    print(text[:4000])


if __name__ == "__main__":
    main()
