"""Dump action_cells, records, and the scenario loader API."""
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump126.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    m = json.loads((ROOT / "SPEC/scenario/map1-saltwell.json").read_text())
    p("=" * 20, "action_cells")
    p(json.dumps(m["action_cells"], indent=1))
    p("=" * 20, "records")
    p(json.dumps(m["records"], indent=1))
    p("=" * 20, "action_class rows 18..22")
    for y in range(18, 23):
        p("y", y, m["action_class"][y][:8])
    p("=" * 20, "action_value rows 18..22")
    for y in range(18, 23):
        p("y", y, m["action_value"][y][:8])
    p("=" * 20, "tiles rows 18..22")
    for y in range(18, 23):
        p("y", y, m["tiles"][y][:8])

    p("=" * 20, "scenario module API")
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from wlengine import scenario as S
    p([n for n in dir(S) if not n.startswith("_")])

    p("=" * 20, "test harness head")
    lines = (ROOT / "tests/test_m5_rules.py").read_text().splitlines()
    for i, l in enumerate(lines[:120]):
        p("%4d %s" % (i + 1, l))

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
