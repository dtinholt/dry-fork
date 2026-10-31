"""Dump SPEC/scenario/hooks.json and the Saltwell cactus cells."""
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump125.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    p("=" * 20, "SPEC/scenario/hooks.json")
    p((ROOT / "SPEC/scenario/hooks.json").read_text())

    p("=" * 20, "map1-saltwell.json keys")
    m = json.loads((ROOT / "SPEC/scenario/map1-saltwell.json").read_text())
    p(sorted(m.keys()))
    for k, v in m.items():
        if isinstance(v, list):
            p(k, "list len", len(v))
        elif isinstance(v, dict):
            p(k, "dict keys", sorted(v.keys())[:20])
        else:
            p(k, "=", v)

    p("=" * 20, "action_cells around (0..7, 18..22)")
    ac = m.get("action_cells")
    if ac:
        for y in range(18, 23):
            p("y", y, [(x, ac[y][x] if y < len(ac) and x < len(ac[y]) else None)
                       for x in range(0, 8)])

    p("=" * 20, "records around (1..5, 19..21)")
    recs = m.get("records")
    if isinstance(recs, dict):
        for k in sorted(recs.keys()):
            if k in ("1,20", "2,20", "3,20", "1,19", "2,19", "3,19", "1,21", "2,21", "3,21"):
                p(k, recs[k])
    elif isinstance(recs, list):
        for r in recs:
            if isinstance(r, dict) and r.get("y") in (19, 20, 21) and r.get("x") in (1, 2, 3, 4, 5):
                p(r)

    p("=" * 20, "our compiled map1 cells around (0..7,18..22)")
    try:
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from wlengine import scenario as S
        sc = S.load_scenario(ROOT / "tests/fixtures-generated/dd117")
        mm = sc.map(1)
        for y in range(18, 23):
            p("y", y, [(x, mm["cells"]["actionClass"][y][x], mm["cells"]["action"][y][x],
                        mm["cells"]["image"][y][x]) for x in range(0, 8)])
    except Exception as e:
        import traceback
        p("ERR", traceback.format_exc())

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
