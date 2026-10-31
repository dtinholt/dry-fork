"""Dump map2/map3 records, the reference log bump events, and the walkthrough."""
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tests/fixtures-generated/dump127.txt"
buf = io.StringIO()


def p(*a):
    print(*a, file=buf)


def main():
    for name in ("map2-ninemile.json", "map3-pumphouse.json"):
        m = json.loads((ROOT / "SPEC/scenario" / name).read_text())
        p("=" * 20, name, "records")
        p(json.dumps(m["records"], indent=1))
        p("=" * 20, name, "action_cells")
        p(json.dumps(m["action_cells"], indent=1))
        p("=" * 20, name, "strings")
        p(json.dumps(m["strings"], indent=1))

    p("=" * 20, "reference log: bump events")
    log = json.loads((ROOT / "SPEC/scenario/walkthrough-reference-log.json").read_text())
    p("top keys", sorted(log.keys()) if isinstance(log, dict) else type(log))
    events = log["events"] if isinstance(log, dict) and "events" in log else log
    for e in events:
        if isinstance(e, dict) and e.get("type") in ("bump", "unlock", "cell_change", "check", "key_used", "paragraph", "message"):
            p(e)

    OUT.write_text(buf.getvalue())
    print("wrote", OUT, len(buf.getvalue()))


if __name__ == "__main__":
    main()
