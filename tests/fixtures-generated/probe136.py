"""Probe 136: run headless scenarios directly (compile + headless.run).

Uses the frozen test support module (wl_support) the same way conftest does:
compile SPEC/scenario into a temp dir, copy it, then call headless.run with a
script.  Writes tests/fixtures-generated/dump136.txt with the event stream of
several M5 scenarios so the engine output can be compared with the reference
log.

Scenarios:
  * bump : 13 LEFT from the Dry Fork start (12 steps then a bump into a cactus)
  * cp6  : walkthrough prefix to CP6 (storehouse lock, class 4 action 2)
  * cp9  : walkthrough prefix to CP9 (vault gate key lock, class 4 action 5)
"""
import sys
import os
import json
import shutil
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, SRC)
sys.path.insert(0, TESTS)

import wl_support as W  # noqa: E402

OUT = os.path.join(HERE, "dump136.txt")
out = open(OUT, "w")


def w(line=""):
    out.write(line + "\n")


def compile_data():
    d = Path(tempfile.mkdtemp(prefix="probe136-"))
    fn = W.api("scenario.compile")
    W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)
    return d


def run(data_dir, script, seed=20261021):
    dd = Path(tempfile.mkdtemp(prefix="probe136-run-"))
    shutil.copytree(data_dir, dd, dirs_exist_ok=True)
    ev = W.call("headless.run", str(dd), script, seed=seed)
    return ev, dd


def prefix(script, name):
    i = next(i for i, s in enumerate(script)
             if isinstance(s, dict) and s.get("checkpoint") == name)
    return script[:i] + [{"checkpoint": name}]


def main():
    data = compile_data()
    w("compiled into %s" % data)
    w("files: %s" % sorted(p.name for p in data.iterdir()))
    w()

    walk = W.load_json(W.SCENARIO / "walkthrough.json")
    script = walk["script"]
    w("script length %d" % len(script))
    w("checkpoints: %s" % [s.get("checkpoint") for s in script if isinstance(s, dict)])
    w()

    for name, sc in [
        ("bump", ["LEFT"] * 13 + [{"checkpoint": "a"}]),
        ("cp6", prefix(script, "CP6")),
        ("cp9", prefix(script, "CP9")),
    ]:
        w("=== scenario %s ===" % name)
        try:
            ev, dd = run(data, sc)
            for e in ev:
                w(json.dumps(e, sort_keys=True))
        except Exception:
            import traceback
            w(traceback.format_exc())
        w()

    out.close()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
