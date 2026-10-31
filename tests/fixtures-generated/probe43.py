"""Probe 43: dump the engine's combat-related code and run the raider fight.

Part 1 prints every function/method in src/wlengine/headless.py and
src/wlengine/rules.py whose name mentions combat, encounter, group, surprise,
round, phase, monster, bump, step, attack, jam, hp, damage or need, with its
source lines.

Part 2 loads the compiled Dry Fork data directory (tests/fixtures-generated/dd)
and runs the walkthrough script up to the road-raider encounter, printing the
event log so we can compare it with wl_combat_ref.opening().
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEYS = ("combat", "encounter", "group", "surprise", "round", "phase",
        "monster", "bump", "step", "attack", "jam", "damage", "need")


def dump(path: Path, keys=KEYS):
    src = path.read_text()
    lines = src.splitlines()
    tree = ast.parse(src)
    print("=" * 70)
    print(path)
    print("=" * 70)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if any(k in name.lower() for k in keys):
                start = node.lineno - 1
                end = node.end_lineno
                print("-" * 70)
                print("%s:%d  def %s" % (path.name, node.lineno, name))
                for i in range(start, end):
                    print("%5d| %s" % (i + 1, lines[i]))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and any(k in t.id.lower() for k in keys):
                    print("-" * 70)
                    print("%s:%d  %s" % (path.name, node.lineno, t.id))
                    for i in range(node.lineno - 1, node.end_lineno):
                        print("%5d| %s" % (i + 1, lines[i]))


def run_fight(seed=20261021):
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "tests"))
    from wlengine import headless
    data = str(ROOT / "tests" / "fixtures-generated" / "dd")
    eng = headless.Engine(data, seed=seed)
    # Walk to the encounter: use the walkthrough script if available.
    wt = ROOT / "SPEC" / "scenario" / "walkthrough.json"
    script = None
    if wt.exists():
        doc = json.loads(wt.read_text())
        for step in doc.get("steps", []):
            if isinstance(step, dict) and "script" in step:
                script = step["script"]
                break
    if script is None:
        print("no walkthrough script found at", wt)
        return
    for tok in script:
        try:
            eng.step_token(tok)
        except Exception as e:  # noqa: BLE001
            print("stopped at token %r: %s: %s" % (tok, type(e).__name__, e))
            break
        if any(e.get("type") == "encounter_start" for e in eng.events):
            break
    for e in eng.events[-40:]:
        print(json.dumps(e, sort_keys=True))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "headless"
    if which in ("headless", "all"):
        dump(ROOT / "src" / "wlengine" / "headless.py")
    if which in ("rules", "all"):
        dump(ROOT / "src" / "wlengine" / "rules.py")
    if which == "fight":
        run_fight()


if __name__ == "__main__":
    main()
