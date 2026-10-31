"""Dump the code regions and hook data needed for the M5 lock fixes.

Writes tests/fixtures-generated/dump124.txt
"""
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump124.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def dump(path, a, b, label):
    p("=" * 20, label, path, a, b)
    lines = (ROOT / path).read_text().splitlines()
    for i in range(a - 1, min(b, len(lines))):
        p("%4d %s" % (i + 1, lines[i]))


def show_json(path, limit=8000):
    p("=" * 20, "JSON", path)
    try:
        data = json.loads((ROOT / path).read_text())
    except Exception as e:
        p("ERR", e)
        return
    txt = json.dumps(data, indent=1)
    p(txt[:limit])
    if len(txt) > limit:
        p("... (%d more chars)" % (len(txt) - limit))


def main():
    dump("src/wlengine/headless.py", 590, 660, "bump_effect/blocked")
    dump("src/wlengine/headless.py", 690, 800, "hooks/locks")
    dump("src/wlengine/headless.py", 800, 880, "unlock/skill_level")
    dump("src/wlengine/combat.py", 430, 498, "victory")
    dump("src/wlengine/rules.py", 90, 130, "check_need")

    p("=" * 20, "LABHOOKS.JSON")
    q = ROOT / "tests/fixtures-generated/dd117/LABHOOKS.JSON"
    try:
        p(q.read_text())
    except Exception as e:
        p("ERR", e)

    p("=" * 20, "scenario dir listing")
    for q in sorted((ROOT / "SPEC/scenario").glob("*")):
        p(q.name)

    p("=" * 20, "hooks json in SPEC")
    for q in sorted((ROOT / "SPEC").rglob("*HOOK*")):
        p(q)

    p("=" * 20, "hooks json in tests")
    for q in sorted((ROOT / "tests").rglob("*HOOK*")):
        p(q)

    show_json("SPEC/scenario/walkthrough.json", 6000)
    show_json("SPEC/scenario/hooks.json", 6000)
    show_json("SPEC/scenario/labhooks.json", 6000)

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
