"""Deep probe: reference log vs engine, and the bump/look/pump scripts.

Prints:
  * the first 30 reference-log events (to see the coordinate convention),
  * reference-log events 120..135 (the first bump),
  * the engine's event list for the bump, look and pump scripts,
  * the engine's map cells for rows 19..21 and column 15.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC"
sys.path.insert(0, str(ROOT / "src"))

from wlengine import scenario as S  # noqa: E402
from wlengine import headless as H  # noqa: E402

SEED = 20261021


def show(ev, lo=0, hi=None):
    hi = len(ev) if hi is None else hi
    for i in range(lo, min(hi, len(ev))):
        e = ev[i]
        print("  %4d %s" % (i, json.dumps(e, sort_keys=True)))


def main():
    rl = json.loads((SPEC / "scenario" / "walkthrough-reference-log.json").read_text())["events"]
    print("=== reference log events 0..30 ===")
    show(rl, 0, 30)
    print("=== reference log events 120..135 ===")
    show(rl, 120, 135)

    out = Path(tempfile.mkdtemp(prefix="probe460-"))
    S.compile(str(SPEC / "scenario"), str(out))
    sc = S.load(str(out))
    m = sc.map(1)
    img = m["cells"]["image"]
    cls = m["cells"]["actionClass"]
    act = m["cells"]["action"]
    print("=== engine map rows 19..21 ===")
    for y in (19, 20, 21):
        print("y=%d img=%s" % (y, img[y]))
        print("     cls=%s" % (cls[y],))
        print("     act=%s" % (act[y],))
    print("=== engine map column 15, rows 8..32 ===")
    for y in range(8, 32):
        print("  (15,%2d) img=%2d cls=%2d act=%d" % (y, img[y][15], cls[y][15], act[y][15]))

    for name, script in (("bump", ["LEFT"] * 13),
                         ("look", ["L", "LEFT"]),
                         ("pump", ["UP"] * 9)):
        print("=== engine run %s ===" % name)
        ev = H.run(str(out), {"seed": SEED, "script": script}, SEED)
        show(ev)
        st = H.first_frame_state(str(out), SEED)
        print("  start state x,y:", st.get("x"), st.get("y"))


if __name__ == "__main__":
    main()
