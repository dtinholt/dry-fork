"""Probe 216: dump the source regions we need to edit.

Writes dump216.txt with:
  * combat.py: every function mentioning ammo/load/jam/reload/orders/status
  * headless.py: every function mentioning bump/steps/cell_change/class
  * rules.py: promotion helpers
  * the M5 tests we must satisfy (bump, save_labstate, raider orders)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "dump216.txt"

KEYS = {
    "src/wlengine/combat.py": ["ammo", "load", "jam", "reload", "order", "status", "fire", "advance", "unarmed"],
    "src/wlengine/headless.py": ["bump", "steps", "cell_change", "class", "print", "tail", "promote", "xp"],
    "src/wlengine/rules.py": ["promote", "level_after", "xp_threshold", "rank"],
}


def regions(path, keys):
    lines = path.read_text().splitlines()
    hits = set()
    for i, ln in enumerate(lines):
        low = ln.lower()
        if any(k in low for k in keys):
            hits.add(i)
    blocks = []
    i = 0
    while i < len(lines):
        if re.match(r"^\s*(def |class )", lines[i]):
            j = i + 1
            while j < len(lines) and not re.match(r"^\s*(def |class )", lines[j]):
                j += 1
            if any(h in range(i, j) for h in hits):
                blocks.append((i + 1, j))
            i = j
        else:
            i += 1
    return lines, blocks


def dump(f, rel, keys):
    p = ROOT / rel
    f.write("=" * 70 + "\n%s\n" % rel + "=" * 70 + "\n")
    lines, blocks = regions(p, keys)
    for a, b in blocks:
        f.write("--- lines %d..%d ---\n" % (a, b))
        for n in range(a - 1, b):
            f.write("%4d| %s\n" % (n + 1, lines[n]))
        f.write("\n")


def dump_range(f, rel, a, b):
    p = ROOT / rel
    lines = p.read_text().splitlines()
    f.write("=" * 70 + "\n%s lines %d..%d\n" % (rel, a, b) + "=" * 70 + "\n")
    for n in range(a - 1, min(b, len(lines))):
        f.write("%4d| %s\n" % (n + 1, lines[n]))
    f.write("\n")


with OUT.open("w") as f:
    for rel, keys in KEYS.items():
        dump(f, rel, keys)
    dump_range(f, "tests/test_m5_rules.py", 500, 545)
    dump_range(f, "tests/test_m5_rules.py", 760, 840)
    dump_range(f, "tests/wl_combat_ref.py", 150, 240)
print("wrote", OUT)
