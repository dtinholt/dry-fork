# Dry Fork: a Wasteland-format engine built by a local model from a specification

This repository holds the complete artifact of a pre-registered experiment (PREREG-W1.md): a
3-bit quantised open mixture-of-experts model, served on two desktop GPUs and driven by a
tool-calling harness, wrote the engine under `src/wlengine/` from the seven specification
documents under `SPEC/` and the 503 acceptance tests under `tests/`, unattended, in 78 active
hours. The specification, the tests, the original scenario "Dry Fork" (`SPEC/scenario/`) and
the harness (`harness/`) were written by a frontier model session beforehand and frozen
(FREEZE-sha256.txt). The run's logs are under `run/` and the scored analysis is `analysis.md`.

No file from the 1988 game is included. The formats were specified clean-room from public
documentation (BIBLIOGRAPHY.md); the scenario, maps, text and party are original.

## Run it

```
PYTHONPATH=src python3 -c "from wlengine import scenario; scenario.compile('SPEC/scenario', 'data')"
PYTHONPATH=src python3 -m wlengine --data data --render-frame
PYTHONPATH=src python3 -m wlengine --headless --data data --script SPEC/scenario/walkthrough.json
PYTHONPATH=. python3 -m pytest -q tests
```

The headless run prints the event log of the reference walkthrough, 358 steps to the win. A
browser front end (keyboard and screen only, written separately) lives with the paper.

## What the model wrote and what it did not

Everything under `src/wlengine/` and `tests/fixtures-generated/` (its own probe scripts, 626 of
them) is the builder's, as left at the end of the run; the two test files corrected by
Addendum 7 of PREREG-W1 are the only frozen files changed after the freeze, and the change is
explained there. `run/WORKLOG.md` is the builder's own log, including its iteration-94 analysis
of the two tests it could not satisfy.

License: MIT.
