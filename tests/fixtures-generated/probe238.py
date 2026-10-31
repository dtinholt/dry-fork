"""probe238: reference log movement around row 20 and the start of the walk."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = []
log = json.loads((ROOT / "SPEC/scenario/walkthrough-reference-log.json").read_text())["events"]
OUT.append("total events %d" % len(log))
for e in log[:70]:
    OUT.append(json.dumps(e)[:250])
OUT.append("---- location 1 moves with y==20 ----")
for e in log:
    if e.get("type") == "move" and e.get("location") == 1 and e.get("y") == 20:
        OUT.append(json.dumps(e))
OUT.append("---- location 1 moves with y==19 or 21 ----")
for e in log:
    if e.get("type") == "move" and e.get("location") == 1 and e.get("y") in (19, 21):
        OUT.append(json.dumps(e))
OUT.append("---- all bumps with location ----")
for e in log:
    if e.get("type") == "bump":
        OUT.append(json.dumps(e))
(ROOT / "tests/fixtures-generated/dump238.txt").write_text("\n".join(OUT))
print("ok")
