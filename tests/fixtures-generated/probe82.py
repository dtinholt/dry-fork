"""Grep SPEC files for cactus/bump/west and dump SPEC-05 sections 5.6, 12, 14.1."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump80.txt")

SPEC = os.path.join(ROOT, "SPEC")


def main():
    out = []
    for name in sorted(os.listdir(SPEC)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(SPEC, name)
        lines = open(path, encoding="utf-8").read().splitlines()
        for i, l in enumerate(lines):
            if re.search(r"cactus|bump|west|LEFT", l, re.I):
                out.append("%s:%d| %s" % (name, i + 1, l))
    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT, len(out), "lines")


if __name__ == "__main__":
    main()
