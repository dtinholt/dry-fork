"""Probe 172: align the SPEC-05 Saltwell ASCII art with the JSON arrays.

Prints the header and a few rows with character indices, then scores the art
against the JSON under both conventions ([y][x] and [x][y]).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCEN = os.path.join(ROOT, "SPEC", "scenario")

GLYPH = {"|": 25, "#": 25, "Y": 11, ".": 0, ";": 18, "P": 23, "T": 24, "b": 22,
         "w": 21, "p": 20, "n": 17, "h": 19, "/": 19, "_": 0}


def main():
    text = open(os.path.join(ROOT, "SPEC", "SPEC-05-scenario.md"), encoding="utf-8").read().split("\n")
    # find the Saltwell block
    start = None
    for i, l in enumerate(text):
        if l.strip().startswith("### 5.2 Saltwell"):
            start = i
            break
    block = text[start:start + 60]
    art = []
    header = None
    for l in block:
        if l.startswith("     0000"):
            header = l
        if len(l) > 6 and l[1:3].strip().isdigit() and "|" in l:
            art.append(l)
    print("header:", repr(header))
    for i, c in enumerate(header):
        if c != " ":
            print("  header idx", i, repr(c))
            break
    print("art rows:", len(art))
    for l in art[:3]:
        print(repr(l))
    # body offset: index of the first '|' or '.' after the row number
    off = art[0].index("|")
    print("body offset", off)

    j = json.load(open(os.path.join(SCEN, "map1-saltwell.json")))
    ac = j["action_class"]
    tiles = j["tiles"]

    def art_cell(r, c):
        line = art[r]
        if off + c >= len(line):
            return None
        return line[off + c]

    # score: for each art cell, does the JSON class match the glyph class?
    for conv in ("yx", "xy"):
        bad = 0
        examples = []
        for r in range(len(art)):
            for c in range(32):
                g = art_cell(r, c)
                if g is None:
                    continue
                if conv == "yx":
                    cls = ac[r][c]
                else:
                    cls = ac[c][r]
                want = 11 if g in "|#Y" else (0 if g == "." else None)
                if want is None:
                    continue
                if cls != want:
                    bad += 1
                    if len(examples) < 5:
                        examples.append((r, c, g, cls))
        print("convention %s: mismatches %d %s" % (conv, bad, examples))

    print("tiles[2][20]=%r tiles[20][2]=%r tiles[20][3]=%r tiles[3][20]=%r"
          % (tiles[2][20], tiles[20][2], tiles[20][3], tiles[3][20]))
    print("ac[2][20]=%r ac[20][2]=%r ac[20][3]=%r ac[3][20]=%r"
          % (ac[2][20], ac[20][2], ac[20][3], ac[3][20]))
    print("art row 20:", repr(art[20]), "-> cells",
          [(c, art_cell(20, c)) for c in range(0, 6)])


main()
