"""Probe 222: reference vs ours at CP5-pre-save (cell_changes) and CP4 (party)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402

OUT = Path(__file__).resolve().parent / "dump222.txt"
SC = ROOT / "SPEC" / "scenario"
DD = Path(__file__).resolve().parent / "dd"
SEED = 20261021


def main():
    ref = W.load_json(SC / "walkthrough-reference-log.json")["events"]
    wt = W.load_json(SC / "walkthrough.json")
    script = []
    for item in wt["script"]:
        script.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == "CP5":
            break
    script = script + ["S", {"checkpoint": "CP5-pre-save"}]
    with OUT.open("w") as f:
        # reference checkpoints
        for e in ref:
            if e.get("type") == "checkpoint" and e.get("name") in ("CP4", "CP5", "CP5-pre-save", "CP6"):
                st = e["state"]
                f.write("REF %s cell_changes=%s\n" % (e["name"], json.dumps(st.get("cell_changes"))))
                f.write("REF %s party=%s\n" % (e["name"], json.dumps([{k: m.get(k) for k in
                        ("slot", "hp", "max_hp", "level", "xp", "rank", "skill_points", "items", "money")}
                        for m in st.get("party", [])])))
        f.write("\n--- ref cell_change events ---\n")
        for e in ref:
            if e.get("type") == "cell_change":
                f.write(json.dumps(e) + "\n")
        f.write("\n--- ref events around seq 120..135 ---\n")
        for e in ref[118:140]:
            f.write(json.dumps(e)[:250] + "\n")
        f.write("\n--- ref events around seq 495..530 ---\n")
        for e in ref[495:530]:
            f.write(json.dumps(e)[:250] + "\n")
        f.write("\n--- ours ---\n")
        try:
            ev = W.call("headless.run", str(DD), {"seed": SEED, "script": script}, None)
        except Exception as exc:  # noqa: BLE001
            f.write("run failed: %s\n" % exc)
            print("wrote", OUT)
            return
        for e in ev:
            if e.get("type") == "checkpoint" and e.get("name") in ("CP4", "CP5", "CP5-pre-save"):
                st = e["state"]
                f.write("OUR %s cell_changes=%s\n" % (e["name"], json.dumps(st.get("cell_changes"))))
                f.write("OUR %s party=%s\n" % (e["name"], json.dumps([{k: m.get(k) for k in
                        ("slot", "hp", "max_hp", "level", "xp", "rank", "skill_points", "items", "money")}
                        for m in st.get("party", [])])))
        f.write("\n--- our cell_change events ---\n")
        for e in ev:
            if e.get("type") == "cell_change":
                f.write(json.dumps(e) + "\n")
    print("wrote", OUT)


main()
