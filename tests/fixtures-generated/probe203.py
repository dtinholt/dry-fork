"""Probe 203: PARTY_CP3, rest of consistency, party loading, combat round loop."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "fixtures-generated", "dump203.txt")
buf = []


def out(s=""):
    buf.append(str(s))


def show(path, pats, before=2, after=25, limit=900):
    full = os.path.join(ROOT, path)
    lines = open(full, encoding="utf-8", errors="replace").read().split("\n")
    hits = [i for i, l in enumerate(lines) if any(p in l for p in pats)]
    shown, rows = set(), []
    for i in hits:
        for j in range(max(0, i - before), min(len(lines), i + after + 1)):
            if j in shown:
                continue
            shown.add(j)
            rows.append("%s:%d: %s" % (path, j + 1, lines[j]))
        rows.append("---")
    out("\n".join(rows[:limit]))


out("=== wl_combat_ref PARTY_CP3 ===")
show("tests/wl_combat_ref.py", ["PARTY_CP3", "RAIDER =", "def ref_ranged_need"], before=1, after=40)
out("=== wl_combat_ref consistency rest ===")
show("tests/wl_combat_ref.py", ["if hit and 0 <= tg < 3"], before=0, after=80)

out("=== headless party load ===")
show("src/wlengine/headless.py", ["def load_party", "def new_game", "def character_dict",
                                  "def member_snapshot", "loaded", "def restore_party"],
     before=2, after=30)

out("=== combat member_weapon / round loop ===")
show("src/wlengine/combat.py", ["def member_weapon", "RANGED_SKILLS", "def _alive",
                                "def round", "def run_round", "def phase1", "def phase2",
                                "def end_of_round", "def start_combat", "def combat_round"],
     before=2, after=35)

out("=== scenario party ===")
show("src/wlengine/scenario.py", ["party.json", "def _party", "def load_party", "loaded",
                                  "def load("], before=2, after=30)

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote", OUT, len(buf))
