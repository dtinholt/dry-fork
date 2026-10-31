"""Probe 144: reference events around every lock check/key_used, plus the map
strings for the hooks' success_message / fail_message indices."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DD = ROOT / "tests" / "fixtures-generated" / "dd"
REF = ROOT / "tests" / "fixtures-generated" / "reflog.txt"


def main():
    import io
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        _main()
    finally:
        sys.stdout = old
    out = ROOT / "tests" / "fixtures-generated" / "dump144.txt"
    out.write_text(buf.getvalue())
    print("wrote", out, len(buf.getvalue().splitlines()), "lines")


def _main():
    lines = REF.read_text().splitlines()
    print("=== reference: context around check / key_used / unlock ===")
    for i, line in enumerate(lines):
        if '"check"' in line or '"key_used"' in line or '"unlock"' in line:
            lo = max(0, i - 3)
            hi = min(len(lines), i + 8)
            for j in range(lo, hi):
                print("%4d %s" % (j + 1, lines[j]))
            print("---")

    sys.path.insert(0, str(ROOT / "src"))
    from wlengine import scenario
    sc = scenario.load(str(DD))
    hooks = json.loads((DD / "LABHOOKS.JSON").read_text())["hooks"]
    print("=== map strings for hook messages ===")
    for h in hooks:
        if h.get("kind") != "lock":
            continue
        loc = h["location"]
        for key in ("success_message", "fail_message"):
            idx = h.get(key)
            if not idx:
                continue
            try:
                text = sc.map_string(loc, idx)
            except Exception as exc:
                text = "ERR %s" % exc
            print("loc %d %s %s -> %r" % (loc, key, idx, text))


if __name__ == "__main__":
    main()
