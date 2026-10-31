"""Measure the ASCII art lines and test both array interpretations."""
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump131.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    spec = (ROOT / "SPEC/SPEC-05-scenario.md").read_text().splitlines()
    start = next(i for i, l in enumerate(spec) if l.strip().startswith("0000000000"))
    p("header line", repr(spec[start]), len(spec[start]))
    art = []
    for i in range(start + 1, start + 34):
        l = spec[i]
        body = l.split("|", 1)[1].rsplit("|", 1)[0] if "|" in l else ""
        art.append(body)
        p("%4d len=%d %r" % (i + 1, len(body), body))

    m = json.loads((ROOT / "SPEC/scenario/map1-saltwell.json").read_text())
    p("=" * 20, "full action_class")
    for y, row in enumerate(m["action_class"]):
        p("ac[%2d]" % y, row)
    p("=" * 20, "full action_value")
    for y, row in enumerate(m["action_value"]):
        p("av[%2d]" % y, row)
    p("=" * 20, "full tiles")
    for y, row in enumerate(m["tiles"]):
        p("ti[%2d]" % y, row)

    p("=" * 20, "action_cells")
    for c in m["action_cells"]:
        p(c)

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
