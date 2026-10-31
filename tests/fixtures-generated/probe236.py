"""probe236: search the reference log and SPEC for x=2 / y=20 evidence."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = []
log = json.loads((ROOT / "SPEC/scenario/walkthrough-reference-log.json").read_text())["events"]
for e in log:
    if e.get("x") == 2 and e.get("y") == 20:
        OUT.append("REF %s" % json.dumps(e))
    if e.get("type") == "move" and e.get("x") == 3 and e.get("y") == 20:
        OUT.append("REF move %s" % json.dumps(e))
OUT.append("ref events with x==2: %s" % [json.dumps(e)[:120] for e in log if e.get("x") == 2][:20])

for p in sorted((ROOT / "SPEC").rglob("*.md")):
    txt = p.read_text()
    for i, line in enumerate(txt.splitlines()):
        if "20  |" in line and "Y" in line:
            OUT.append("%s:%d %r" % (p.name, i + 1, line))

ref = ROOT / "SPEC/reference"
if ref.is_dir():
    OUT.append("reference dir: %s" % sorted(x.name for x in ref.iterdir())[:40])
    for p in sorted(ref.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".json", ".txt"):
            OUT.append("  %s (%d bytes)" % (p.relative_to(ref), p.stat().st_size))

# walkthrough.json: any LEFT runs?
wt = json.loads((ROOT / "SPEC/scenario/walkthrough.json").read_text())
OUT.append("walkthrough keys: %s" % sorted(wt.keys()))
OUT.append(json.dumps(wt["script"])[:3000])

(ROOT / "tests/fixtures-generated/dump236.txt").write_text("\n".join(OUT))
print("ok")
