"""Probe the storehouse check numbers (M5).

Compiles SPEC/scenario into tests/fixtures-generated/dd117 and prints:
  - skill_table[14] and skill_attribute(14)
  - the premade party attributes as the engine sees them
  - the check events of the CP6 run
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wlengine.scenario as scenario  # noqa: E402
import wlengine.headless as headless  # noqa: E402

OUT = Path(__file__).resolve().parent
DD = OUT / "dd117"
SPEC = ROOT / "SPEC" / "scenario"


def main():
    DD.mkdir(exist_ok=True)
    scenario.compile(str(SPEC), str(DD))
    sc = scenario.load(str(DD))
    print("skill_table[14] =", sc.skill_table[14])
    print("skill_table[14] =", sc.skill_table[14])
    eng = headless.Engine(str(DD), seed=20261021)
    eng.new_game(20261021)
    import wlengine.rules as _r
    _orig = _r.check_need

    def _spy(level, attribute, difficulty, tool=False):
        print("check_need(level=%r, attr=%r, diff=%r, tool=%r)" % (level, attribute, difficulty, tool))
        return _orig(level, attribute, difficulty, tool)

    _r.check_need = _spy
    headless.rules.check_need = _spy
    print("skill_attribute(14) =", eng.skill_attribute(14))
    print("ATTR_OFFSETS =", eng.ATTR_OFFSETS)
    for m in eng.party:
        print("slot", m["slot"], m["name"], m["attrs"], "money", m["money"],
              "skills", m["skills"])
    wt = json.loads((SPEC / "walkthrough.json").read_text())
    steps = wt["script"]
    script = []
    for s in steps:
        if isinstance(s, dict) and s.get("checkpoint") == "CP6":
            break
        script.append(s)
    eng.run_script(script)
    for e in eng.events:
        if e.get("type") in ("check", "bump", "unlock", "xp", "message"):
            print(e)
    print("after run: skill_attribute(14) =", eng.skill_attribute(14))
    print("after run: skill_table[14] =", eng.sc.skill_table[14])
    print("after run: attr_value(party[2],14) =", eng.attr_value(eng.party[2], 14))


if __name__ == "__main__":
    main()
