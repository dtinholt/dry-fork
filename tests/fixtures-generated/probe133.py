"""Extract the Saltwell ASCII art rows exactly and compare with the JSON."""
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump133.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    spec = (ROOT / "SPEC/SPEC-05-scenario.md").read_text().splitlines()
    start = next(i for i, l in enumerate(spec) if l.strip().startswith("00000000001111111111222222222233"))
    p("header", repr(spec[start]))
    art = {}
    for i in range(start + 1, start + 34):
        l = spec[i]
        if "|" not in l:
            break
        body = l.split("|", 1)[1].rsplit("|", 1)[0]
        label = l.split("|", 1)[0].strip()
        art[int(label)] = body
        p("row %2s len=%d %r" % (label, len(body), body))

    m = json.loads((ROOT / "SPEC/scenario/map1-saltwell.json").read_text())
    p("=" * 20, "compare art vs json tiles")
    for y in sorted(art):
        body = art[y]
        marks = [(x, c) for x, c in enumerate(body) if c != "."]
        jt = m["tiles"][y]
        jmarks = [(x, v) for x, v in enumerate(jt) if v != 0]
        p("y=%2d art %s" % (y, marks))
        p("      json %s" % (jmarks,))

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
