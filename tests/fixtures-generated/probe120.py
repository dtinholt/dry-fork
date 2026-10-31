"""Probe 120: reproduce the storehouse TypeError and print the traceback."""
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))

from wlengine import headless  # noqa: E402


def main():
    # find the walkthrough script used by the tests
    import json
    wt = os.path.join(HERE, "..", "..", "SPEC", "scenario", "walkthrough.json")
    if not os.path.exists(wt):
        print("no walkthrough.json at", wt)
        for root, dirs, files in os.walk(os.path.join(HERE, "..", "..", "SPEC")):
            for f in files:
                if "walk" in f.lower():
                    print("  candidate:", os.path.join(root, f))
        return
    data = json.load(open(wt))
    print("walkthrough keys:", list(data)[:10] if isinstance(data, dict) else type(data))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
