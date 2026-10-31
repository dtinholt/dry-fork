"""Probe 231: the SPEC-05 art row 20 with indices, and the compiled map's
actionClass row 20 (via the engine's own scenario reader)."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump231.txt"
SC = ROOT / "SPEC" / "scenario"


def main():
    d = Path(tempfile.mkdtemp(prefix="probe231-"))
    W.engine_ready()
    W._armed(W.api("scenario.compile"), str(SC), str(d), allow_reference_log=True)
    with OUT.open("w") as f:
        text = (ROOT / "SPEC" / "SPEC-05-scenario.md").read_text().splitlines()
        for i, line in enumerate(text):
            if line.strip().startswith("20  |") or line.strip().startswith("19  |") or line.strip().startswith("21  |"):
                f.write("spec line %d: %r\n" % (i + 1, line))
                body = line.strip()[4:]
                f.write("  body=%r\n" % body)
                f.write("  Y at %s\n" % [k for k, ch in enumerate(body) if ch == "Y"])
        # compiled map via the engine's scenario reader
        try:
            import wlengine.scenario as S  # noqa: E402
            sc = S.load(str(d))
        except Exception as exc:  # noqa: BLE001
            f.write("scenario load failed: %s\n" % exc)
            sc = None
        if sc is not None:
            m = sc.map(1)
            f.write("map keys=%s\n" % list(m.keys()))
            cells = m["cells"]
            f.write("cells keys=%s\n" % list(cells.keys()))
            for k in ("actionClass", "action", "image", "tile"):
                if k in cells:
                    f.write("cells.%s row20=%s\n" % (k, cells[k][20]))
    shutil.rmtree(d, ignore_errors=True)
    print("wrote", OUT)


main()
