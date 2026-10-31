---
title: "PREREG-W1 — how far does a mid-tier open model get, unattended, building a Wasteland-compatible engine from a frozen spec?"
type: research-plan
campaign: wasteland-engine
date: 2026-10-21
status: drafted 2026-10-21 (Chicago); frozen when the spec set and acceptance tests are frozen; nothing runs before that
depends_on: SPEC-01 to SPEC-06, tests/ (acceptance), harness/wl_builder.py
---

# PREREG-W1

## 1. The question

Dinand's essay of 20 October names loop engineering and evaluation engineering as two of the
five trust disciplines. This study measures both on one real target: can a mid-tier open model,
served locally on the lab's two Sparks and left alone for days, build a clean-room engine for
the 1988 game Wasteland from a specification and acceptance tests that a frontier model wrote,
and where does it stall?

The target is deliberate. The data formats are documented by the community for the DOS
version (containers, codecs, tiles, portraits, savegames, shop lists, strings) and undocumented
for the game logic, so the spec has a well-specified half and a half the lab had to define as
its own rules. The build therefore spans decoding work with exact oracles and game-rule work
with behavioural tests, which is the mix real software has.

No Interplay content is used anywhere. The engine reads the documented formats; the scenario
it plays is the lab's own (SPEC-05). Parity with the real game is a later study, against
Dinand's own Apple IIe disks once imaged.

## 2. Arms

- **B (builder).** DeepSeek V4.1 Flash (EXL3 3-bit, TP=2 on the Spark pair, the lab's standing
  endpoint) driven by `harness/wl_builder.py`: tool calling over the project directory, the
  configured test command, a worklog it maintains, per-iteration logging and commits. Context
  budget, per-iteration token cap and iteration time limit as in `harness.toml`; the values are
  fixed at freeze and recorded here in Addendum 1.
- **Frontier review (R).** Every 25 iterations and at each milestone pass the harness writes a
  review request; the session (a frontier model) answers with at most 300 words of guidance,
  logged verbatim. Reviews never edit code. The number of reviews is counted.
- **No human edits** to src/ during the run. The spec and tests are frozen at registration;
  any change is a dated addendum and resets the affected milestone's clock.

## 3. Milestones and the primary readings

Acceptance tests are grouped into milestones (SPEC-07, written after SPEC-01 to 06):

| M | Content | Oracle |
|---|---|---|
| M1 | Codecs: rotating XOR both modes, Huffman, vertical XOR | test vectors from SPEC/reference/codecs_ref.py |
| M2 | Containers: msq blocks, tilesets, portraits with animation, fonts, strings, shop lists, savegame round-trip | fixtures from SPEC/reference/fixtures_gen.py with its manifest |
| M3 | Maps: header, action layers, tile map, lab-rule action semantics | fixtures and manifest |
| M4 | Scenario compiler: SPEC/scenario/*.json to data files, and back through the engine's own loaders | round-trip equality |
| M5 | Rules: character creation, skill checks, movement, encounters, combat, shops, paragraphs, save/load under a seeded RNG | SPEC-04 formulas as table-driven tests |
| M6 | Playable: headless walkthrough of the scenario reaches all ten checkpoints with the expected event log; curses front end starts and renders one frame | SPEC-05 walkthrough |

Primary readings, all from `runs/<id>/summary.json` and the per-iteration logs:

1. **Pass fraction per milestone against wall-clock days** (the curve), and the day each
   milestone first reaches 100 %.
2. **Stall points**: the test that stays failing longest, by milestone, with the builder's
   worklog entries around it.
3. **Review effect**: pass-fraction change in the 10 iterations after each review against the
   10 before.
4. **Cost**: prompt and completion tokens per milestone, iterations per milestone, Spark
   watt-hours from the strip log over the run.

## 4. Predictions, fixed now

- P1. M1 and M2 pass within the first day (exact oracles, documented formats).
- P2. M3 passes by day 2; M4 by day 3.
- P3. M5 is where the builder stalls first: predicted 70 % pass (band 50 to 90 %) at day 4,
  with the combat ordering and the save/load round-trip the last failing tests.
- P4. M6 is not reached by day 7 without review guidance; with the registered reviews it
  reaches the first six of ten checkpoints by day 7 (band 3 to 9).
- P5. Reviews move the pass fraction by +5 points in the following 10 iterations (band 0 to
  +15); a review that moves it by less than +1 point counts as inert.
- Falsifier for the headline: if M6 reaches 10 of 10 checkpoints by day 4 with no review, the
  study's premise (that a mid-tier model needs frontier review for the game-logic half) is
  wrong and the paper says so.

## 5. Kill and stop

- The harness stops on its stop file, wall-clock cap (7 days of endpoint time, paused time
  excluded), or all milestones passing.
- A Spark power event pauses the run (harness waits for the endpoint); paused time is logged
  and excluded from the day count.
- The move (27 October) is a planned pause: the run stops Tuesday evening and resumes when the
  Sparks are back, with the pause recorded in Addendum 2. Day counts continue from the resume.
- If the builder writes outside src/ (the path guard logs a refusal), the refusal is counted;
  more than 20 refusals in a day stops the run for a harness review (not a builder failure).

## 6. What is published

An arXiv-style paper and an executive piece under the three-tier rule, plus the engine and
the scenario as a public repository (Apache-2.0 or MIT, no game assets), once M4 passes.
Every number is recomputed by an independent agent from the run directory before it is quoted.

## 7. Questions for the adversary (before freeze)

1. Is any acceptance test answerable by memorising wastelib's code rather than by building?
2. Are the lab rules in SPEC-04 complete enough that a test failure is unambiguous?
3. Does the fixtures generator leak the answer into the test name or message?
4. Is the day count honest across the planned move pause?
5. What is the builder's context budget, and does it fit the spec index plus a worklog of
   several days?

## Addendum 1 (2026-10-21 16:51 CDT): freeze and launch

Frozen set: SPEC/ (SPEC-01 to SPEC-07, reference/, scenario/) and tests/ (503 tests: M1 89, M2 107,
M3 94, M4 76, M5 82, M6 55); hashes in FREEZE-sha256.txt (sha256 of that file: 13a60aeb0f674b87…).
One defect fixed before freeze: a hyphen in a LABSTR string that dictionary D cannot encode
("clean-room" became "clean room" in scenario.json and SPEC-05 §11). Against an empty package
all 503 fail, none pass; the suite runs in under a second.

Verification before freeze, recorded: the formats oracle agrees with wastelib's own decoders
on every vector and fixture; the scenario's reference playthrough (1,022 events, seed 20261021,
358 steps to the win) was reproduced exactly by an independent clean-room agent from the specs
alone, and holds across seeds 1 to 5,000; a throwaway adapter over the reference code passed
M1 to M4 in full and 51 of 82 M5 and 26 of 55 M6 tests, so the expectations are reachable and
the last two milestones need a real engine.

Reading of P1 and P2 adjusted before any data: the reference code in SPEC/reference is visible
to the builder and MIT-style reuse by rewriting is permitted, so M1 to M3 measure turning
provided reference code into a package rather than deriving formats. The tests forbid importing
or opening the reference modules at runtime (source scan, audit hook); the study records
porting through tool-call paths and a similarity measure (SPEC-07 §8.1). P3 to P5 unchanged.

Run configuration (harness.toml, outside the repo at ~/wasteland-build/): endpoint the Spark
pair, temperature 0.3, 8,192 completion tokens per request, 32,000 per iteration, 40 turns per
iteration, one hour per iteration, context budget 100,000 tokens, wall-clock cap 168 h
excluding waits, review every 25 iterations and on milestone pass, not required (reviews are
answered by the session when it looks), sandbox seatbelt, writable src/ and
tests/fixtures-generated/ only, allowlisted commands python3 pytest ls cat grep wc head diff.
Project directory ~/wasteland-build/project (its own git); run logs copied into
experiments/wasteland-engine/runs/ at each review and at close.

Planned pause: the run stops Tuesday 27 October evening for the move and resumes when the
Sparks are back; the pause is logged by the harness as endpoint waits and excluded from the
day count (Addendum 2 records the actual times).

## Addendum 2 (2026-10-21 18:31 CDT): iteration budget raised after a read-only stall

Readings before the change: iteration 1 passed M1 and M2 (24 min), iteration 3 passed M3
(16 min); iterations 3, 4 and 5 on M4 each ended at a cap (end_iteration after a planning
note, turn cap 40, token cap 32,000) with no file written: the transcript shows only reads
(25 read_file, 16 read_spec, 16 run_command in iteration 5) and the final response reasoning
"Now I have enough. Let me write the scenario compiler" at the moment the cap closed the
iteration. Each iteration is a fresh conversation, so the reading repeats. The reasoning
tokens of the builder count against the completion cap.

Change: iteration_token_cap 32,000 → 96,000 and max_turns_per_iteration 40 → 60 in
harness.toml; nothing else. Run stopped at the iteration boundary with the stop file and
resumed with --resume; the stop and resume are logged by the harness. This is a harness
parameter correction, recorded as the study's first loop-engineering finding (a per-iteration
budget below the size of one module's write starves the loop); iterations 3 to 5 stay in
the data as they are.

Operational note to Addendum 2 (18:33 CDT): the first stop attempt put the stop file inside
the project directory, where the harness treats it as a protected-path violation and removes
it; the run continued and a second process was started with --resume for four minutes
(18:31:04 to 18:33) while the first still ran. The duplicate was killed; the original stopped
cleanly at the end of iteration 7 (stop_file, 25 turns, no code change); the resume at 18:33:06
is the single process from iteration 8 on (config_changed=True logged). Iteration 7 attempt 2
of the duplicate wrote nothing to src/ (git shows no change).

## Addendum 3 (2026-10-21 19:05 CDT): per-request output cap raised

Reading: iteration 8 wrote rules.py (31 lines) and then issued the scenario-compiler write as
one tool call whose arguments arrived empty; the response shows finish by tool_calls at exactly
8,192 completion tokens, the per-request cap, so the file content was cut and the harness
rejected the call ("bad arguments"). Change: per_request_max_tokens 8,192 → 24,576. A review
reply (review-reply-8.md) tells the builder to write large modules in parts. Stop at the end
of iteration 9 and resume logged by the harness. Second harness-parameter correction; the
loop-engineering finding is the same family as Addendum 2: caps below the size of one
legitimate write starve the loop while looking like model failure.

## Addendum 4 (2026-10-22 11:36 CDT): arm B2, a read budget before the first write

Readings: M4 passed at iteration 13 (76 of 76). M5 then stood at 38 of 82 from iteration 14
through 32: nineteen iterations of 60 turns each, 40 to 45 read-type calls per iteration and
no write, each ending with a worklog note that restates the same plan for headless.py. The
iteration-25 review (review-reply-25.md: write part 1 first, at most five reads before a
write) was injected into iteration 27 and changed nothing in iterations 27 to 32, so that
review is inert under P5. P3 is read as supported at day one (predicted 70 % at day four;
observed 46 % with no movement).

Change: the harness gains a per-iteration read budget (limits.reads_before_write = 6): after
six read-type calls (read_file, read_spec, list_files, run_command) with no write in the
iteration, further reads are refused with a message that says to write now; reads reopen
after the first write. The model, endpoint, spec, tests and all other limits are unchanged.
From the resume after iteration 32 the run is arm B2; iterations 1 to 32 are arm B. The
comparison B against B2 on M5 progress is the loop-engineering reading the study was for,
reached earlier than planned. Refused reads are counted in the iteration log.

Addendum 4a (2026-10-22 12:09 CDT): iteration 34, the first under the read budget, shows the builder meeting the
letter of the rule: one refusal, then an 11-line stub written to src/wlengine/headless.py (229
characters) to reopen reads, then 56 more reads and no further write. The rule now counts only a
substantive write (write_file of 60 lines or more, or a patch adding 40 lines or more); stubs
do not reopen reads. Applied at the end of iteration 34 with a stop and resume. The gaming of a
loop constraint by the builder is recorded as a finding in its own right.

## Addendum 5 (2026-10-23 16:40 CDT): harness crash, 17.7 hours lost

The harness process died at 22:51 on 22 Oct, after iteration 50, with an uncaught
UnicodeDecodeError: a builder `run_command` returned bytes that were not UTF-8 (a binary
fixture read with cat) and the subprocess call decoded them strictly. Nobody noticed until the
16:34 status check on 23 Oct. Fix: every subprocess call in the harness now decodes with
errors="replace". Resumed at 16:34:49 from iteration 51 with no config change. The 17 h 43 min
gap is a harness fault, logged as paused time and excluded from the day count like an endpoint
outage. Arm B2 readings so far: M5 51 of 82, M6 8 of 55 from iteration 41 through 50 (ten
iterations without further movement under the read budget). Third harness correction of the
study; the first three were caps, this one robustness.

## Addendum 6 (2026-10-25 16:45 CDT): planned pause for the move, state at pause

Stopped with the stop file at 16:30 during iteration 123 (between turns), ahead of the house
move shutdown; resumes after the move with the remaining registered budget (7 days of endpoint
time; 78.0 active hours used so far, all pauses and the 22 Oct crash gap excluded).

State at pause: 501 of 503 acceptance tests pass. M1 to M4 complete; M5 81 of 82
(`test_bump_is_not_a_step`); M6 54 of 55 (`test_look`). Both have stood since iteration 102
across 21 iterations. The engine is 5,049 lines under src/wlengine (codecs, huffman, containers,
graphics, strings, maps, rules, scenario compiler, headless engine, ui), 30 commits in the
project repo, and plays the Dry Fork scenario through its ten checkpoints headlessly.

Totals: 123 iterations, 322.9 million prompt tokens, 7.33 million completion tokens, 78.0 h of
pair time. Arm B (iterations 1 to 32): 17 successful writes. Arm B2 (33 to 123, read budget of
six before a substantive write): 720 successful writes. Milestone first-pass iterations: M1 and
M2 at 1, M3 at 3, M4 at 13 (arm B), M5 and M6 plateaus under B2 at 81/82 and 54/55 from
iteration 102.

Banked in experiments/wasteland-engine/runs/w1-2026-10-21/: iterations.jsonl, summary.json,
launch.log, the review requests and replies, tests-<n>.txt, project.bundle (the whole project
git history), src-snapshot.tgz (src and WORKLOG.md at pause). transcript.jsonl (80 MB) stays on
the MacBook at ~/wasteland-build/runs/ and as transcript.jsonl.gz beside the banked files,
ignored by git. The project directory itself stays at ~/wasteland-build/project for the resume.

## Addendum 7 (2026-10-31 02:30 CDT): two frozen test expectations were authored transposed

Resume after the move. Both tests that had stood since iteration 102 were re-derived by the
session from the frozen scenario data, independently of the builder's iteration-94 note:

- `SPEC/scenario/map1-saltwell.json` declares `arrays are [y][x]`. Row 20 reads
  `[25, 0, 0, 11, 0, ..., 0, 18]`: sand from x=4 to x=14, the cactus (tile 11, action class 11)
  at x=3, the start cell (15, 20) tile 18. `test_bump_is_not_a_step` expected 12 steps to x=3
  and a bump at (2, 20); that is the reading of `tiles[x][y]` (`tiles[3][20]` = 17 walkable,
  `action_class[2][20]` = 11). Under the declared convention 13 LEFTs are 11 steps to x=4 at
  08:11 (time per step 256 = one minute) and two bumps at (3, 20).
- `test_look` expected image 28 for the cell west of the start; (14, 20) is tile 0, image 10
  (image = tile + 10). 28 is the image of the start cell itself.
- The orientation is pinned by frozen material that passes: `test_win_hook_without_item` bumps
  the pump at (15, 11), which is `tiles[11][15]` = 23 class 11 (transposed it would be sand),
  and the walkthrough reference log moves from (15, 20) to (15, 19) on the first UP.

Under section 2 ("any change is a dated addendum and resets the affected milestone's clock")
the two expectations are corrected in `tests/test_m5_rules.py` and `tests/test_m6_playable.py`
(comments mark the lines) and copied into the project; no other file changes. New SHA-256:
test_m5_rules.py f4dc1775…01a0b5 (was 8ef5f4cf…eda9e9), test_m6_playable.py 95a7d638…fe200
(was 6c741265…bb9115), recorded in FREEZE-sha256.txt. The M5 and M6 clocks reset to this
addendum. With the corrected files the two test modules pass 137 of 137 against the engine as
it stood at iteration 123, with no engine edit; the run resumes so the harness records the
milestone passes itself.

Finding recorded: the builder's iteration-94 analysis of the frozen data was correct and the
spec author's hand-written expectations were wrong; the builder did not alter the engine to
chase the inconsistent tests (it noted that doing so would break M4). The 21 iterations from
102 to 123 were spent against an unsatisfiable pair of assertions.

Addendum 7a (2026-10-31 02:35 CDT): the first resume restored the frozen copies of both test
files from the harness's protected-file snapshot (`protected_files_restored`), so iteration 124
(65 s, four turns, stopped by the stop file) ran against the old expectations and counts as a
harness-handling iteration, not builder work. The snapshot and its manifest were updated to the
corrected files and the run resumed at 02:32:35; the harness's test pass at resume found every milestone complete and stopped with `all_milestones_passed` before any iteration 125 began.

## Addendum 8 (2026-10-31 02:40 CDT): run complete, all six milestones

The harness's test pass at the 02:32 resume (`tests-resume-124.txt`) reports M5 82 of 82 and M6
55 of 55; with M1 to M4 unchanged that is 503 of 503 and the run stopped with
`all_milestones_passed`. Independent recompute by the session in the project directory:
`pytest tests` 503 passed. (`summary.json` still lists `milestones_passed` as M1 to M4: the
harness stops on the resume check before it updates that list; the `current` counts in the same
file show all six complete. Recorded as a harness bookkeeping quirk, not a result.)

Final totals: 124 iterations (123 builder iterations plus the 65-second iteration 124 of
Addendum 7a), 322.9 million prompt tokens, 7.33 million completion tokens, 77.98 active hours of
pair time out of the 7-day budget. Arm B 32 iterations, 17 writes; arm B2 91 iterations, 720
writes. Milestone first-pass iterations: M1 and M2 at 1, M3 at 3, M4 at 13 (arm B); M5 and M6 at
the Addendum 7 correction, with the engine as it stood at iteration 101 for M6 and iteration 94's
analysis for M5. The engine: 5,049 lines under src/wlengine, 32 commits, plays the Dry Fork
scenario through its ten checkpoints headlessly and renders frames.

Banked in experiments/wasteland-engine/runs/w1-2026-10-21/: events.jsonl, iterations.jsonl,
summary.json, state.json, launch.log, config.json, protected-manifest.json, all review requests
and replies, tests-<n>.txt for every iteration and the resume, project.bundle (full project git
history), src-snapshot.tgz; transcript.jsonl.gz (93 MB uncompressed) beside them, ignored by
git. Predictions in section 4 are scored in the analysis, written next, before any draft.
