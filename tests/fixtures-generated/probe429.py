"""probe429: compare SPEC-05 section 5.2 ASCII rows against the frozen
SPEC/scenario/map1-saltwell.json tile rows, column by column, with a ruler.

Run: python3 tests/fixtures-generated/probe429.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
SCEN = SPEC / "scenario"


def ruler(n, start=0):
    # two-line ruler: tens and units
    tens = "".join(str((start + i) // 10 % 10) for i in range(n))
    units = "".join(str((start + i) % 10) for i in range(n))
    return tens + "\n" + units


def main():
    text = (SPEC / "SPEC-05-scenario.md").read_text(encoding="utf-8")
    # find section 5.2
    m = re.search(r"^### 5\.2 .*$", text, re.M)
    if not m:
        print("no 5.2 heading")
        return
    start = m.end()
    m2 = re.search(r"^### 5\.3 ", text[start:], re.M)
    body = text[start:start + (m2.start() if m2 else len(text))]
    ascii_rows = [l for l in body.splitlines() if l.startswith("|")]
    print("ASCII rows found:", len(ascii_rows))
    for i, l in enumerate(ascii_rows):
        print("ascii[%d] len=%d %r" % (i, len(l), l))

    j = json.loads((SCEN / "map1-saltwell.json").read_text(encoding="utf-8"))
    print("json keys:", sorted(j.keys()))
    tiles = j["tiles"]
    print("json tiles: %d rows of %d" % (len(tiles), len(tiles[0])))
    for y in (0, 1, 11, 20):
        print("json tiles[%d] = %s" % (y, tiles[y]))

    # compare: assume ascii row i corresponds to json row i (both 32 wide)
    print("\n--- column comparison (ascii index vs json index) ---")
    for i, l in enumerate(ascii_rows):
        if i >= len(tiles):
            break
        row = tiles[i]
        diffs = []
        for x in range(min(len(l), len(row))):
            ch = l[x]
            if ch == "|":
                want = 25
            elif ch == ".":
                want = 0
            else:
                want = None
            if want is not None and row[x] != want:
                diffs.append((x, ch, row[x]))
        if diffs:
            print("row %d: %d diffs, first 8: %s" % (i, len(diffs), diffs[:8]))

    # also compare shifted by one
    print("\n--- shifted comparison (ascii index x -> json index x-1) ---")
    for i, l in enumerate(ascii_rows):
        if i >= len(tiles):
            break
        row = tiles[i]
        diffs = []
        for x in range(1, len(l)):
            ch = l[x]
            if ch == "|":
                want = 25
            elif ch == ".":
                want = 0
            else:
                want = None
            if want is not None and x - 1 < len(row) and row[x - 1] != want:
                diffs.append((x, ch, row[x - 1]))
        if diffs:
            print("row %d: %d diffs, first 8: %s" % (i, len(diffs), diffs[:8]))

    # print the action_class / action_value arrays if present
    for k in sorted(j.keys()):
        v = j[k]
        if isinstance(v, list) and v and isinstance(v[0], list):
            print("\n%s: %d rows of %d" % (k, len(v), len(v[0])))
            for y in (11, 20):
                if y < len(v):
                    print("  %s[%d] = %s" % (k, y, v[y]))
        elif isinstance(v, list):
            print("\n%s: %s" % (k, v[:40]))
        else:
            print("\n%s: %r" % (k, v))


if __name__ == "__main__":
    main()
