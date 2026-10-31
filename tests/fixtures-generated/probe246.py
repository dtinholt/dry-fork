"""Probe 246: what does the compiled data dir contain, how does scenario.load
read maps, and what does the oracle see for map1 row 20?"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
OUT = pathlib.Path(__file__).resolve().parent

from wlengine import scenario  # noqa: E402

tmp = pathlib.Path(tempfile.mkdtemp())
scenario.compile(str(ROOT / "SPEC" / "scenario"), str(tmp))

out = []
out.append("compiled dir files: %s" % sorted(p.name for p in tmp.iterdir()))
for p in sorted(tmp.iterdir()):
    if p.is_file():
        out.append("  %s %d bytes" % (p.name, p.stat().st_size))

src = (ROOT / "src" / "wlengine" / "scenario.py").read_text().splitlines()
out.append("")
out.append("scenario.py def lines:")
for i, ln in enumerate(src):
    if ln.lstrip().startswith("def "):
        out.append("%4d %s" % (i + 1, ln))

r = subprocess.run([sys.executable, str(ROOT / "tests" / "oracle_tool.py"), "compiled", str(tmp),
                    str(ROOT / "SPEC" / "scenario")], capture_output=True, text=True)
out.append("")
out.append("oracle rc=%d" % r.returncode)
try:
    data = json.loads(r.stdout)
except ValueError:
    out.append("stdout: %s" % r.stdout[:2000])
    out.append("stderr: %s" % r.stderr[:2000])
    data = None
if data:
    out.append("top keys: %s" % sorted(data.keys()))
    orc = data.get("oracle", {})
    out.append("oracle keys: %s" % sorted(orc.keys()))
    for k in orc:
        v = orc[k]
        if isinstance(v, dict):
            out.append("  %s: dict keys %s" % (k, sorted(v.keys())[:20]))
        elif isinstance(v, list):
            out.append("  %s: list len %d" % (k, len(v)))
    maps = orc.get("maps") or orc.get("map")
    if maps:
        out.append("maps type %s" % type(maps))
        if isinstance(maps, list):
            m1 = maps[1] if len(maps) > 1 else maps[0]
        else:
            m1 = maps.get("1") or maps.get(1)
        out.append("m1 keys: %s" % (sorted(m1.keys()) if isinstance(m1, dict) else type(m1)))
        if isinstance(m1, dict):
            for k, v in m1.items():
                if isinstance(v, list) and v and isinstance(v[0], list):
                    out.append("  %s row20[:8] = %s" % (k, v[20][:8]))
                elif isinstance(v, list):
                    out.append("  %s = %s" % (k, v[:8]))
                else:
                    out.append("  %s = %r" % (k, v))
    out.append("errors: %s" % json.dumps(data.get("errors", {}))[:1000])

(OUT / "dump250.txt").write_text("\n".join(out))
print("ok")
