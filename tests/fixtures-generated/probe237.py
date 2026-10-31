"""probe237: dump the compiled map1 cells row 20 via the engine loader."""
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
OUT = []
import wlengine.scenario as sc  # noqa: E402

d = pathlib.Path(tempfile.mkdtemp())
sc.compile(str(ROOT / "SPEC/scenario"), str(d))
loader = sc.load(str(d))
m = loader.map(1)
OUT.append("map keys %s" % sorted(m.keys()))
OUT.append("cells keys %s" % sorted(m["cells"].keys()))
for k in ("actionClass", "action", "image"):
    OUT.append("%s row20 %s" % (k, m["cells"][k][20]))
    OUT.append("%s row17 %s" % (k, m["cells"][k][17]))
OUT.append("actions %s" % json.dumps(m.get("actions"))[:2000])
OUT.append("records %s" % json.dumps(m.get("records"))[:2000])
(ROOT / "tests/fixtures-generated/dump237.txt").write_text("\n".join(OUT))
print("ok")
