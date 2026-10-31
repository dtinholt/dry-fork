"""Probe 148: raw Saltwell ASCII art lines with lengths and repr."""
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
    for line in text[start:start + 45]:
        if re.match(r"^\s*\d+\s+\|", line):
            print(len(line), repr(line))
    print("=== legend search ===")
    for i, line in enumerate(text):
        if "cactus" in line or "legend" in line.lower():
            print(i + 1, line)


if __name__ == "__main__":
    main()
