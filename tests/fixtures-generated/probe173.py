"""Dump the source of the functions involved in the three failing M5 tests.

Also dumps the M5 test bodies for the three failing tests, and the reference
support helpers used by them, so the next iteration can reason without
re-reading the frozen tests.
"""
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wlengine.headless as H  # noqa: E402
import wlengine.combat as CB  # noqa: E402
import wlengine.labstate as LS  # noqa: E402
import wlengine.containers as CT  # noqa: E402
import wlengine.rules as RU  # noqa: E402

TARGETS = [
    (H, ["try_move", "move", "bump", "bump_effect", "bump_lock", "key_o", "key_y",
         "load_game", "write_save_files", "save_game", "restore_party", "character_dict",
         "build_savegame_payload", "snapshot", "checkpoint", "dispatch", "input",
         "member_from_character", "advance_time", "apply_tail", "cell_action"]),
    (CB, ["auto_orders", "weapon_ammo", "ammo_boxes", "member_weapon", "loaded",
          "combat_round", "resolve_round", "member_has_ammo"]),
    (LS, ["encode_labstate", "decode_labstate"]),
    (CT, ["encode_savegame", "decode_savegame"]),
    (RU, ["skill_level", "best_salvage"]),
]

out = []
for mod, names in TARGETS:
    out.append("=" * 70)
    out.append("MODULE %s" % mod.__name__)
    out.append("=" * 70)
    for n in names:
        fn = getattr(mod, n, None)
        if fn is None:
            out.append("### %s: MISSING" % n)
            continue
        try:
            src = inspect.getsource(fn)
        except Exception as e:  # noqa: BLE001
            out.append("### %s: %s" % (n, e))
            continue
        out.append("### %s" % n)
        out.append(src)

# The three failing test bodies, plus the helpers they use.
test_path = ROOT / "tests" / "test_m5_rules.py"
lines = test_path.read_text().splitlines()
out.append("=" * 70)
out.append("TEST FILE EXCERPTS")
out.append("=" * 70)
for start, end in [(500, 545), (660, 700), (795, 834)]:
    out.append("--- lines %d..%d ---" % (start, end))
    out.extend(lines[start - 1:end])

sup = ROOT / "tests" / "wl_support.py"
if sup.is_file():
    slines = sup.read_text().splitlines()
    out.append("=" * 70)
    out.append("wl_support.py (%d lines)" % len(slines))
    out.append("=" * 70)
    out.extend(slines)

Path(__file__).with_name("dump173.txt").write_text("\n".join(out))
print("wrote dump173.txt", len(out), "lines")
