"""Probe 96: Saltwell row 20 passability, skill attributes, encounter records."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

from wlengine import headless, maps  # noqa: E402

DD = os.path.join(HERE, "dd")


def main():
    out = []
    eng = headless.Engine(DD, seed=20261021)
    eng.new_game(20261021)
    m = eng.sc.map(1)
    out.append("saltwell size %r" % m["size"])
    for y in (19, 20, 21):
        row = []
        for x in range(0, 8):
            row.append("%d:%d/%d/%d/%s" % (x, m["cells"]["actionClass"][y][x],
                                           m["cells"]["action"][y][x],
                                           m["cells"]["image"][y][x],
                                           maps.is_passable(m, x, y)))
        out.append("y=%d %s" % (y, " ".join(row)))
    out.append("record_at(2,20) %r" % (maps.record_at(m, 2, 20),))
    out.append("record_at(3,20) %r" % (maps.record_at(m, 3, 20),))
    out.append("skill_table %r" % (getattr(eng.sc, "skill_table", None),))
    for s in (18, 22, 14, 4, 5, 26, 3):
        out.append("skill %d attr %d" % (s, eng.skill_attribute(s)))
    # encounter records
    for loc in (0, 3):
        mm = eng.sc.map(loc)
        for y in range(mm["size"]):
            for x in range(mm["size"]):
                if mm["cells"]["actionClass"][y][x] == 3:
                    out.append("enc loc%d (%d,%d) %r" % (loc, x, y, maps.record_at(mm, x, y)))
    text = "\n".join(out)
    with open(os.path.join(HERE, "dump96.txt"), "w") as fh:
        fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
