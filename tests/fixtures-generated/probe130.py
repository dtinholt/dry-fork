"""Compare the JSON map1 rows with the ASCII art and our compiled map."""
import io
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump130.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    m = json.loads((ROOT / "SPEC/scenario/map1-saltwell.json").read_text())
    for y in (10, 11, 20):
        p("JSON tiles[%d]" % y, list(enumerate(m["tiles"][y])))
        p("JSON action_class[%d]" % y, list(enumerate(m["action_class"][y])))
        p("JSON action_value[%d]" % y, list(enumerate(m["action_value"][y])))

    spec = (ROOT / "SPEC/SPEC-05-scenario.md").read_text().splitlines()
    for i, l in enumerate(spec):
        if l.startswith("  20 ") or l.startswith("  11 ") or l.startswith("  10 "):
            body = l.split("|", 1)[1].rsplit("|", 1)[0]
            p("ASCII", l[:6], list(enumerate(body)))

    p("=" * 20, "our compiled map1")
    sys.path.insert(0, str(ROOT / "src"))
    from wlengine import scenario as S
    sc = S.load(ROOT / "tests/fixtures-generated/dd117")
    mm = sc.map(1)
    for y in (10, 11, 20):
        p("compiled y=%d" % y, [(x, mm["cells"]["actionClass"][y][x], mm["cells"]["action"][y][x],
                                 mm["cells"]["image"][y][x]) for x in range(0, 32)])

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
