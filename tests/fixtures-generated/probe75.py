"""Dump wl_combat_ref.py 1-150 and test_m5_rules.py 1-460."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump75.txt")


def read(path, start=None, end=None):
    lines = open(path, encoding="latin-1").read().split("\n")
    if start is not None:
        lines = lines[start - 1:end]
    return ["%4d %s" % (i + 1, l) for i, l in enumerate(lines)]


def main():
    out = []
    out.append("=" * 30 + " wl_combat_ref.py 1-150")
    out.extend(read(os.path.join(ROOT, "tests", "wl_combat_ref.py"), 1, 150))
    out.append("=" * 30 + " wl_combat_ref.py 300-400")
    out.extend(read(os.path.join(ROOT, "tests", "wl_combat_ref.py"), 300, 400))
    out.append("=" * 30 + " test_m5_rules.py 1-460")
    out.extend(read(os.path.join(ROOT, "tests", "test_m5_rules.py"), 1, 460))
    with open(OUT, "w", encoding="latin-1") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote", OUT, len(out))


if __name__ == "__main__":
    main()
