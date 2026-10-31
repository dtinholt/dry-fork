"""probe439: dump the engine's compiled Saltwell map around row 20 and compare
with SPEC/scenario/map1-saltwell.json.  Also show the engine's compile API."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import wlengine.scenario as sc  # noqa: E402

print("scenario API:", [n for n in dir(sc) if not n.startswith("_")])

d = json.loads((ROOT / "SPEC/scenario/map1-saltwell.json").read_text(encoding="utf-8"))
for y in (19, 20, 21):
    print("JSON tiles[%d] =" % y, d["tiles"][y])
    print("JSON class[%d] =" % y, d["action_class"][y])
    print("JSON value[%d] =" % y, d["action_value"][y])

tmp = Path(tempfile.mkdtemp())
try:
    sc.compile_scenario(ROOT / "SPEC/scenario", tmp)
    print("compiled ->", tmp)
    for p in sorted(tmp.rglob("*")):
        print("   ", p.relative_to(tmp), p.stat().st_size if p.is_file() else "<dir>")
except Exception:  # noqa: BLE001
    import traceback
    traceback.print_exc()

print()
print("=== engine map read ===")
import wlengine.maps as mp  # noqa: E402
print("maps API:", [n for n in dir(mp) if not n.startswith("_")])
try:
    m = mp.load_map(tmp, 1)
    print("map type", type(m))
    print("attrs", [n for n in dir(m) if not n.startswith("_")])
except Exception:  # noqa: BLE001
    import traceback
    traceback.print_exc()
