"""Probe 295: narrow dump of the CLI entry point, errors module and the
headless API surface the M6 tests need.

Run: python3 tests/fixtures-generated/probe295.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)


def dump(path):
    print("=" * 70)
    print(path)
    print("=" * 70)
    if not os.path.exists(path):
        print("<missing>")
        return
    with open(path, encoding="utf-8") as fh:
        print(fh.read())


def main():
    print("ls src/wlengine:", sorted(os.listdir(os.path.join(SRC, "wlengine"))))
    print("ls src:", sorted(os.listdir(SRC)))
    print("ls tests:", sorted(os.listdir(os.path.join(ROOT, "tests"))))
    dump(os.path.join(SRC, "wlengine", "errors.py"))
    dump(os.path.join(SRC, "wlengine", "__main__.py"))
    dump(os.path.join(SRC, "wlengine", "cli.py"))
    dump(os.path.join(SRC, "wlengine", "__init__.py"))


if __name__ == "__main__":
    main()
