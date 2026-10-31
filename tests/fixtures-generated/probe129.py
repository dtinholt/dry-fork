"""Raw map1 JSON rows and SPEC-05 cactus mentions."""
import io
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump129.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    txt = (ROOT / "SPEC/scenario/map1-saltwell.json").read_text()
    p("=" * 20, "raw json length", len(txt))
    # print the action_class / action_value / tiles blocks raw
    for key in ("action_class", "action_value", "tiles"):
        i = txt.find('"%s"' % key)
        p("=" * 20, key, "at", i)
        p(txt[i:i + 900])

    p("=" * 20, "SPEC-05 cactus mentions")
    spec = (ROOT / "SPEC/SPEC-05-scenario.md").read_text().splitlines()
    for i, l in enumerate(spec):
        if "cactus" in l or "(2, 20)" in l or "(2,20)" in l or "(3, 20)" in l:
            p("%4d %s" % (i + 1, l))

    p("=" * 20, "SPEC-05 section 5.2 Saltwell")
    start = next(i for i, l in enumerate(spec) if l.startswith("### 5.2"))
    end = next(i for i, l in enumerate(spec) if l.startswith("### 5.3"))
    for i in range(start, end):
        p("%4d %s" % (i + 1, spec[i]))

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
