"""Dump current headless.py combat region + reference log window + scenario
monster/weapon data into dump72.txt."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump72.txt")


def read(path, start=None, end=None):
    lines = open(path, encoding="latin-1").read().split("\n")
    if start is not None:
        lines = lines[start - 1:end]
    return ["%4d %s" % (i + 1, l) for i, l in enumerate(lines)]


def main():
    out = []
    out.append("=" * 30 + " headless.py 460-720")
    out.extend(read(os.path.join(ROOT, "src", "wlengine", "headless.py"), 460, 720))
    out.append("=" * 30 + " headless.py 720-900")
    out.extend(read(os.path.join(ROOT, "src", "wlengine", "headless.py"), 720, 900))
    out.append("=" * 30 + " headless.py 900-1000")
    out.extend(read(os.path.join(ROOT, "src", "wlengine", "headless.py"), 900, 1000))
    with open(OUT, "w", encoding="latin-1") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote", OUT, len(out))


if __name__ == "__main__":
    main()
