"""Probe 259: write the reference combat checker source and our combat module
source to dump files, then print the parts relevant to jam/unjam/reload.

Run: python3 tests/fixtures-generated/probe259.py
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_combat_ref as CR  # noqa: E402
import wlengine.combat as C  # noqa: E402

OUT = Path(__file__).resolve().parent


def main():
    (OUT / "dump259ref.txt").write_text(inspect.getsource(CR))
    (OUT / "dump259eng.txt").write_text(inspect.getsource(C))
    print("wrote dump259ref.txt", len(inspect.getsource(CR)))
    print("wrote dump259eng.txt", len(inspect.getsource(C)))


main()
