"""Probe 407: dump the compiled Saltwell map row 20 (images and classes)."""
import sys
import pathlib
import json
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from wlengine import scenario, maps

SCEN = ROOT / "SPEC" / "scenario"
d = pathlib.Path(tempfile.mkdtemp("probe407"))
scenario.compile(str(SCEN), str(d))
print("compiled to", d)

# find the map file for location 1
for p in sorted(d.iterdir()):
    print("  ", p.name)

m = maps.load_map(str(d), 1) if hasattr(maps, "load_map") else None
print("maps attrs:", [a for a in dir(maps) if not a.startswith("_")])
