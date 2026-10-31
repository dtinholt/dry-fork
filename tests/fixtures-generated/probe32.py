"""Probe 32: raw SPEC-05 Saltwell block lines, index by index."""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
text = (PROJECT / "SPEC" / "SPEC-05-scenario.md").read_text(encoding="utf-8")
i = text.index("### 5.2 Saltwell")
j = text.index("### 5.3", i)
sec = text[i:j]
block = re.findall(r"```text\n(.*?)```", sec, re.S)[0]
for ln in block.split("\n"):
    if ln.startswith(" 20") or ln.startswith("  0") or ln.startswith("  1"):
        print(repr(ln))
        print("len", len(ln))
        for k, ch in enumerate(ln):
            print("   %2d %r" % (k, ch))
        print()

m = json.load(open(PROJECT / "SPEC" / "scenario" / "map1-saltwell.json"))
print("conventions:", m.get("conventions"))
print("info:", json.dumps(m["info"]))
print("tiles[20]:", m["tiles"][20])
print("ac[20]   :", m["action_class"][20])
print("av[20]   :", m["action_value"][20])
print()
print("count of class 11 cells:", sum(1 for r in m["action_class"] for v in r if v == 11))
print("count of tile 25 cells:", sum(1 for r in m["tiles"] for v in r if v == 25))
print("count of tile 16 cells:", sum(1 for r in m["tiles"] for v in r if v == 16))
