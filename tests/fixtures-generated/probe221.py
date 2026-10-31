"""Probe 221: run the oracle tool on the compiled dd dir and dump the map1 oracle."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "dump221.txt"
DD = Path(__file__).resolve().parent / "dd"

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(DD),
                    str(ROOT / "SPEC" / "scenario")], capture_output=True, text=True)
with OUT.open("w") as f:
    f.write("rc=%s\n" % r.returncode)
    f.write("stderr=%s\n" % r.stderr[-2000:])
    try:
        data = json.loads(r.stdout)
    except ValueError:
        f.write("stdout head=%s\n" % r.stdout[:2000])
        print("wrote", OUT)
        sys.exit(0)
    f.write("keys=%s\n" % list(data.keys()))
    f.write("errors=%s\n" % json.dumps(data.get("errors"))[:2000])
    o = data.get("oracle", {})
    f.write("oracle keys=%s\n" % list(o.keys()))
    for k in ("maps", "map1", "labmaps"):
        if k in o:
            f.write("%s=%s\n" % (k, json.dumps(o[k])[:4000]))
print("wrote", OUT)
