"""Probe 145: Saltwell row y=20 (the cactus row) and the bump test trace."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DD = ROOT / "tests" / "fixtures-generated" / "dd"


def main():
    sys.path.insert(0, str(ROOT / "src"))
    from wlengine import scenario, maps
    sc = scenario.load(str(DD))
    m = sc.map(1)
    print("size", m["size"])
    for y in (19, 20, 21):
        row = []
        for x in range(0, 18):
            cls = m["cells"]["actionClass"][y][x]
            act = m["cells"]["action"][y][x]
            img = m["cells"]["image"][y][x]
            pas = maps.is_passable(m, x, y)
            row.append("x%d:c%d/a%d/i%d/p%s" % (x, cls, act, img, int(bool(pas))))
        print("y=%d" % y, " ".join(row))
    print("start info", m["info"])


if __name__ == "__main__":
    main()
