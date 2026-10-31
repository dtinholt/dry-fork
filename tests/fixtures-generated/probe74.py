"""Dump headless.py 100-460 and 1000-1077."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump74.txt")


def read(path, start=None, end=None):
    lines = open(path, encoding="latin-1").read().split("\n")
    if start is not None:
        lines = lines[start - 1:end]
    return ["%4d %s" % (i + 1, l) for i, l in enumerate(lines)]


def main():
    out = []
    out.append("=" * 30 + " headless.py 200-460")
    out.extend(read(os.path.join(ROOT, "src", "wlengine", "headless.py"), 200, 460))
    out.append("=" * 30 + " headless.py 1000-1077")
    out.extend(read(os.path.join(ROOT, "src", "wlengine", "headless.py"), 1000, 1077))
    with open(OUT, "w", encoding="latin-1") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote", OUT, len(out))


if __name__ == "__main__":
    main()
