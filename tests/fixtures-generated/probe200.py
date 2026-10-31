"""Probe 200: dump the reference checkpoint cell_changes and our own.

Reads SPEC/scenario/walkthrough-reference-log.json and prints, for each
checkpoint, the cell_changes list.  Also runs our engine to CP5-pre-save and
prints our checkpoint + the LABSTATE.BIN bytes we write.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump200.txt")
buf = []


def out(s=""):
    buf.append(str(s))


ref = json.load(open(os.path.join(ROOT, "SPEC", "scenario",
                                  "walkthrough-reference-log.json")))
out("top keys: %s" % (list(ref)[:20] if isinstance(ref, dict) else type(ref)))
if isinstance(ref, dict):
    for k, v in ref.items():
        if isinstance(v, list):
            out("%s: list of %d" % (k, len(v)))
        else:
            out("%s: %r" % (k, v))

# find checkpoints
def walk(o, path=""):
    if isinstance(o, dict):
        if "cell_changes" in o:
            out("--- %s" % path)
            out("    cc=%s" % json.dumps(o.get("cell_changes")))
            out("    steps=%s rng=%s" % (o.get("steps"), o.get("rng_state")))
        for k, v in o.items():
            walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)


walk(ref)

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
