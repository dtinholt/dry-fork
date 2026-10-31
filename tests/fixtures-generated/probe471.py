"""probe471: dump reference log context around each bump, and the SPEC-06
section 3 (look) and SPEC-04 LR-15 (bump) text."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "SPEC")

ref = json.load(open(os.path.join(SPEC, "scenario", "walkthrough-reference-log.json")))
ev = ref["events"]
for i, e in enumerate(ev):
    if e.get("type") == "bump":
        print("=== bump at seq", e["seq"], e)
        for j in range(max(0, i - 6), min(len(ev), i + 4)):
            print("   ", json.dumps(ev[j]))

txt = open(os.path.join(SPEC, "SPEC-06-ui.md")).read()
i = txt.find("## 3.")
print("=== SPEC-06 section 3 ===")
print(txt[i:i + 3000])

s4 = open(os.path.join(SPEC, "SPEC-04-rules.md")).read()
for m in re.finditer(r"LR-15", s4):
    print("=== LR-15 context ===")
    print(s4[max(0, m.start() - 800):m.start() + 800])
    break
