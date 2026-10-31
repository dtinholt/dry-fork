"""Probe 28: extract the Saltwell ASCII map from SPEC-05 and index it."""
from __future__ import annotations

import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
text = (PROJECT / "SPEC" / "SPEC-05-scenario.md").read_text(encoding="utf-8")

# find the saltwell section
i = text.index("### 5.2 Saltwell")
j = text.index("### 5.3", i)
sec = text[i:j]
blocks = re.findall(r"```text\n(.*?)```", sec, re.S)
print("blocks:", len(blocks))
for b in blocks:
    lines = b.split("\n")
    for ln in lines:
        print(repr(ln))
    print("----")
    # header line
    hdr = lines[0]
    print("header len", len(hdr), "first digit at", hdr.index("0"))
    for ln in lines[2:]:
        if not ln.strip():
            continue
        # find the '|' or first map char
        k = ln.index("|") if "|" in ln else None
        print("row", repr(ln[:8]), "bar at", k, "len", len(ln))
    break
