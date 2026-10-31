"""Probe 146: run the bump script through headless.run and print the events."""
import json
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DD = ROOT / "tests" / "fixtures-generated" / "dd"


def main():
    sys.path.insert(0, str(ROOT / "src"))
    from wlengine import headless
    tmp = pathlib.Path(tempfile.mkdtemp())
    for p in DD.iterdir():
        if p.is_file():
            shutil.copy(p, tmp / p.name)
    script = {"seed": 20261021, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]}
    ev = headless.run(str(tmp), script, None)
    for e in ev:
        print(json.dumps(e, sort_keys=True))


if __name__ == "__main__":
    main()
