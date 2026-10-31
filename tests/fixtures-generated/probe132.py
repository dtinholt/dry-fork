"""Dump conftest.py and wl_support.py."""
import io
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump132.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    for name in ("tests/conftest.py", "tests/wl_support.py"):
        q = ROOT / name
        p("=" * 30, name, q.is_file())
        if q.is_file():
            lines = q.read_text().splitlines()
            for i, l in enumerate(lines):
                p("%4d %s" % (i + 1, l))
    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
