"""probe440: print the RAW SPEC-05 Saltwell ASCII lines (repr, no stripping) to
check for a leading space column, and dump the engine's compiled map cells."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

SPEC = (ROOT / "SPEC/SPEC-05-scenario.md").read_text(encoding="utf-8")
i = SPEC.index("### 5.2 Saltwell")
seg = SPEC[i:i + 3000]
print("=== RAW lines ===")
for line in seg.split("\n")[:40]:
    print(repr(line))

print()
print("=== engine compile ===")
import wlengine.scenario as sc  # noqa: E402
import inspect  # noqa: E402
print(inspect.signature(sc.compile))
print(inspect.getsource(sc.compile)[:1500])
