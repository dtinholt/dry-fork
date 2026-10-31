"""probe234: bump semantics: tiles.json, SPEC-05 s3, reference log context."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = []

tj = json.loads((ROOT / "SPEC/scenario/tiles.json").read_text())
OUT.append("tiles.json keys: %s" % sorted(tj.keys()))
tiles = tj.get("tiles") or tj
for t in (tiles if isinstance(tiles, list) else []):
    if t.get("id") in (11, 23, 25, 18, 19, 22, 24, 26, 9, 10, 16, 17, 21):
        OUT.append("tile %s: %s" % (t.get("id"), json.dumps(t)))

spec = (ROOT / "SPEC/SPEC-05-scenario.md").read_text()
i = spec.find("## 3. Tiles")
OUT.append("---- SPEC-05 section 3 ----")
OUT.append(spec[i:i + 3000])

log = json.loads((ROOT / "SPEC/scenario/walkthrough-reference-log.json").read_text())["events"]
# print context around each bump
for k, e in enumerate(log):
    if e.get("type") == "bump":
        OUT.append("---- bump at seq %s ----" % e.get("seq"))
        for j in range(max(0, k - 4), min(len(log), k + 3)):
            OUT.append("   %s" % json.dumps(log[j])[:300])

# checkpoint states with x,y
OUT.append("---- checkpoints ----")
for e in log:
    if e.get("type") == "checkpoint":
        st = e.get("state") or {}
        OUT.append("seq %s name %s loc %s x %s y %s steps %s" % (e.get("seq"), e.get("name"), st.get("location"),
                                                                 st.get("x"), st.get("y"), st.get("steps")))

(ROOT / "tests/fixtures-generated/dump234.txt").write_text("\n".join(OUT))
print("ok", len(OUT))
