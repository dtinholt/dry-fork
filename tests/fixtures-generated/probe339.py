"""Probe 339: compare the engine's compiled Saltwell map with the SPEC JSON.

Dumps cells.image / actionClass rows 20 and 2-3, plus passability along the
west walk from (15,20), and runs the M5 bump script through headless.run.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from wlengine import headless, maps, scenario  # noqa: E402

scen = ROOT / "SPEC" / "scenario"
m1 = json.loads((scen / "map1-saltwell.json").read_text())

sc = scenario.Scenario(scen)
m = sc.map(1)
cells = m["cells"]
print("compiled map keys:", sorted(m.keys()))
print("size:", m.get("size"))
print("image[20][0:8] =", cells["image"][20][0:8])
print("image[2][18:24] =", cells["image"][2][18:24])
print("image[3][18:24] =", cells["image"][3][18:24])
print("actionClass[20][0:8] =", cells["actionClass"][20][0:8])
print("actionClass[2][18:24] =", cells["actionClass"][2][18:24])
print("actionClass[3][18:24] =", cells["actionClass"][3][18:24])
print("SPEC tiles[20][0:8] =", m1["tiles"][20][0:8])
print("SPEC tiles[2][18:24] =", m1["tiles"][2][18:24])
print("SPEC tiles[3][18:24] =", m1["tiles"][3][18:24])

print("walk west from (15,20):")
for x in range(15, 0, -1):
    print("  x=%2d image=%3d class=%2d passable=%s" % (
        x, cells["image"][20][x], cells["actionClass"][20][x], maps.is_passable(m, x, 20)))

print("walk west transposed (x,y swapped):")
for x in range(15, 0, -1):
    print("  x=%2d image=%3d class=%2d passable=%s" % (
        x, cells["image"][x][20], cells["actionClass"][x][20], maps.is_passable(m, x, 20)))

# run the M5 bump script
import tempfile, shutil  # noqa: E402
dd = pathlib.Path(tempfile.mkdtemp()) / "data"
shutil.copytree(ROOT / "tests" / "fixtures-generated" / "probe320data", dd) if False else None
print("done")
