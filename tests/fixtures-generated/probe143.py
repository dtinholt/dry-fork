"""Probe 143: dump the lock-related code of headless.py and the lock hooks.

Prints:
  * headless.py lines 680-800 (bump_lock, hook_lock, run_hook_at, ...)
  * the lock hooks from LABHOOKS.JSON
  * the reference events around the storehouse / vault gate bumps
  * the class-4 records of Saltwell (location 1) and Pumphouse Deep (3)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "wlengine" / "headless.py"
DD = ROOT / "tests" / "fixtures-generated" / "dd"
REF = ROOT / "tests" / "fixtures-generated" / "reflog.txt"


def dump_code(start, end):
    lines = SRC.read_text().splitlines()
    print("=== headless.py %d-%d ===" % (start, end))
    for i in range(start - 1, min(end, len(lines))):
        print("%4d %s" % (i + 1, lines[i]))


def dump_hooks():
    data = json.loads((DD / "LABHOOKS.JSON").read_text())
    print("=== hooks ===")
    for h in data.get("hooks", []):
        print(json.dumps(h, sort_keys=True))


def dump_ref():
    print("=== reference events 495-535 ===")
    for i, line in enumerate(REF.read_text().splitlines()):
        if 495 <= i + 1 <= 535:
            print("%4d %s" % (i + 1, line))
    print("=== reference events 800-820 ===")
    for i, line in enumerate(REF.read_text().splitlines()):
        if 800 <= i + 1 <= 820:
            print("%4d %s" % (i + 1, line))


def dump_maps():
    sys.path.insert(0, str(ROOT / "src"))
    from wlengine import scenario
    sc = scenario.load(str(DD))
    for loc in (1, 3):
        m = sc.map(loc)
        print("=== map %d size %s ===" % (loc, m["size"]))
        for y in range(m["size"]):
            for x in range(m["size"]):
                cls = m["cells"]["actionClass"][y][x]
                if cls in (4, 11):
                    rec = None
                    try:
                        from wlengine import maps as _maps
                        rec = _maps.record_at(m, x, y)
                    except Exception as exc:  # pragma: no cover
                        rec = "ERR %s" % exc
                    print("loc %d (%d,%d) cls %d action %d rec %s" %
                          (loc, x, y, cls, m["cells"]["action"][y][x], rec))


def main():
    import io
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        dump_code(680, 800)
        dump_hooks()
        dump_ref()
        dump_maps()
    finally:
        sys.stdout = old
    out = ROOT / "tests" / "fixtures-generated" / "dump143.txt"
    out.write_text(buf.getvalue())
    print("wrote", out, len(buf.getvalue().splitlines()), "lines")


if __name__ == "__main__":
    main()
