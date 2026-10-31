"""Probe 147: count the SPEC-05 Saltwell ASCII art columns for the cactus row."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = ROOT / "SPEC" / "SPEC-05-scenario.md"


def main():
    text = SPEC.read_text().splitlines()
    start = None
    for i, line in enumerate(text):
        if line.strip().startswith("### 5.2 Saltwell"):
            start = i
            break
    print("section starts at line", start + 1)
    for line in text[start:start + 50]:
        m = re.match(r"^\s*(\d+)\s+\|(.*)\|\s*$", line)
        if m:
            y = int(m.group(1))
            body = m.group(2)
            marks = [(x, ch) for x, ch in enumerate(body) if ch not in ".;"]
            print("y=%2d len=%d marks=%s" % (y, len(body), marks))


if __name__ == "__main__":
    main()
