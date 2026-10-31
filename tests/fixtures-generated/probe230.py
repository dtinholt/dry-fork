"""Probe 230: compile and dump the compiled map1 action_class row 20 plus the
scenario JSON action_cells."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump230.txt"
SC = ROOT / "SPEC" / "scenario"


def main():
    d = Path(tempfile.mkdtemp(prefix="probe230-"))
    W.engine_ready()
    W._armed(W.api("scenario.compile"), str(SC), str(d), allow_reference_log=True)
    with OUT.open("w") as f:
        j = json.loads((SC / "map1-saltwell.json").read_text())
        f.write("action_cells=%s\n" % json.dumps(j.get("action_cells"))[:3000])
        f.write("records=%s\n" % json.dumps(j.get("records"))[:3000])
        f.write("conventions=%s\n" % json.dumps(j.get("conventions"))[:2000])
        # compiled map
        import wlengine.maps as M  # noqa: E402
        import wlengine.containers as C  # noqa: E402
        g = (d / "GAME1").read_bytes()
        t = C.read_tables(str(d / "LABTABLES.BIN"))
        f.write("tables keys=%s\n" % list(t.keys()))
        f.write("mapOffsets=%s\n" % t.get("mapOffsets"))
        try:
            blk = M.read_map(g, t, 1)
        except Exception as exc:  # noqa: BLE001
            f.write("read_map failed: %s\n" % exc)
            blk = None
        if blk is not None:
            f.write("map keys=%s\n" % list(blk.keys()))
            cells = blk.get("cells") or {}
            f.write("cells keys=%s\n" % list(cells.keys()))
            for k in ("actionClass", "action", "image", "tile"):
                if k in cells:
                    f.write("cells.%s row20=%s\n" % (k, cells[k][20]))
    shutil.rmtree(d, ignore_errors=True)
    print("wrote", OUT)


main()
