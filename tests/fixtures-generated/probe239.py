"""probe239: reference log tail + SPEC-04 LR-15/LR-16 text."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = []
log = json.loads((ROOT / "SPEC/scenario/walkthrough-reference-log.json").read_text())["events"]
OUT.append("---- last 80 events ----")
for e in log[-80:]:
    OUT.append(json.dumps(e)[:300])

spec = (ROOT / "SPEC/SPEC-04-rules.md").read_text()
i = spec.find("## 5. Movement and time")
OUT.append("---- SPEC-04 section 5 ----")
OUT.append(spec[i:i + 2500])

spec5 = (ROOT / "SPEC/SPEC-05-scenario.md").read_text()
i = spec5.find("### 14.1 Step list")
OUT.append("---- SPEC-05 14.1 ----")
OUT.append(spec5[i:i + 4000])
(ROOT / "tests/fixtures-generated/dump239.txt").write_text("\n".join(OUT))
print("ok")
