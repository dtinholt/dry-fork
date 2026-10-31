"""Dump show_message, save/load, and reference-log bumps near y=20."""
import io
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump128.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def dump(path, a, b, label):
    p("=" * 20, label, path, a, b)
    lines = (ROOT / path).read_text().splitlines()
    for i in range(a - 1, min(b, len(lines))):
        p("%4d %s" % (i + 1, lines[i]))


def main():
    src = (ROOT / "src/wlengine/headless.py").read_text()
    lines = src.splitlines()
    for i, l in enumerate(lines):
        if re.search(r"def (show_message|save_game|load_game|write_save_files|build_savegame_payload|key_o|key_y|new_game|__init__)", l):
            p("LINE %d: %s" % (i + 1, l))
    dump("src/wlengine/headless.py", 1, 120, "headless head")

    log = json.loads((ROOT / "SPEC/scenario/walkthrough-reference-log.json").read_text())
    events = log["events"]
    p("=" * 20, "reference bumps")
    for e in events:
        if e.get("type") == "bump":
            p(e)
    p("=" * 20, "reference events seq 100-140")
    for e in events:
        if 100 <= e.get("seq", 0) <= 140:
            p(e)
    p("=" * 20, "reference events seq 800-830")
    for e in events:
        if 800 <= e.get("seq", 0) <= 830:
            p(e)

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
