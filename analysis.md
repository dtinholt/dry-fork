---
id: wasteland-w1-analysis
type: analysis
title: "PREREG-W1 analysis: a 3-bit local model builds a Wasteland engine from a spec"
created: 2026-10-31
updated: 2026-10-31
status: draft
prereg: PREREG-W1.md
run: runs/w1-2026-10-21/
recompute: done 31 Oct (independent agent, from the raw run files; one correction, arm B2 read calls 5,031 to 5,023 after excluding iteration 124; all other figures agreed)
---

# Analysis, PREREG-W1 (run w1-2026-10-21)

All numbers from `runs/w1-2026-10-21/` (iterations.jsonl, tests-<n>.txt, events.jsonl) and the
mini's strip log; computed by the session on 31 Oct and recomputed independently the same day from the raw files (one correction applied, see front matter). Day
counts use active endpoint time (wall time of iterations minus endpoint waits), as registered.

## 1. Outcome

503 of 503 acceptance tests, all six milestones, in 124 iterations and 77.98 active hours of
pair time (budget 168 h). The last two tests were authoring errors in the frozen suite, found by
the builder at iteration 94 and corrected by Addendum 7; the engine needed no change for them.

## 2. Primary reading 1: pass fraction against active days

| Milestone | First 100 % | Active hours | Day |
|---|---|---|---|
| M1 codecs | iteration 1 | 0.39 | 1 |
| M2 containers | iteration 1 | 0.39 | 1 |
| M3 maps | iteration 2 | 0.64 | 1 |
| M4 scenario compiler | iteration 11 | 3.54 | 1 |
| M5 rules | 81 of 82 from iteration 92; 82 of 82 at Addendum 7 | 55.5 (81/82) | 3 |
| M6 playable | 54 of 55 from iteration 101; 55 of 55 at Addendum 7 | 61.22 (54/55) | 3 |

Pass fraction at the day boundaries (last iteration inside each 24 active hours):

| Day end | Iteration | M5 | M6 |
|---|---|---|---|
| 1 (23.84 h) | 42 | 0.622 | 0.145 |
| 2 (47.89 h) | 80 | 0.963 | 0.164 |
| 3 (71.96 h) | 115 | 0.988 | 0.982 |
| run end (77.98 h) | 124 | 0.988 → 1.0 (Add. 7) | 0.982 → 1.0 (Add. 7) |

The ten walkthrough checkpoints: CP1 to CP3 pass after iteration 40 (day 1), CP4 to CP10 pass in
iterations 90 to 93 (day 3, 55.93 active hours at iteration 93). The curses frame renders from
iteration 101.

## 3. Primary reading 2: stall points

Longest-failing tests (count of tests-<n>.txt files in which they fail):

| Test | Iterations failing | Why |
|---|---|---|
| test_look (M6) | 0 to 124, all | authoring error in the frozen test (Add. 7) |
| test_bump_is_not_a_step (M5) | 0 to 124, all | authoring error in the frozen test (Add. 7) |
| test_repeat_limit, test_malformed_script, three render tests, test_cli_render_frame (M6) | 0 to 100 | ui.py and the headless error paths written in iterations 95 to 101 |
| test_cli_headless (M6) | 0 to 98 | CLI entry point |
| test_log_segment[CP8..CP10] (M6) | 0 to 92 | walkthrough tail |

The real stall of the run is arm B's M5 plateau: 38 of 82 (0.463) for 26 iterations (14 to 39),
during which the builder read 40 to 45 files per iteration and wrote nothing (Addendum 4). The
last three honest M5 failures (iterations 75 to 81) were `test_raider_fight_rules[orders]`,
`test_load_restores_state` and `test_save_labstate`: combat ordering and the save/load
round-trip, as P3 named.

## 4. Primary reading 3: review effect

Three review replies were injected (iterations 3, 10 and 27); requests at 75 and 100 were not
answered before the run finished.

| Reply | Injected at | Mean overall pass fraction, 10 before | 10 after | Change |
|---|---|---|---|---|
| review-reply-1 | 3 | 0.483 (n = 2) | 0.615 | +13.2 pts |
| review-reply-8 | 10 | 0.556 (n = 9) | 0.773 | +21.7 pts |
| review-reply-25 | 27 | 0.803 | 0.803 | 0.0 pts (inert) |

The two early reviews fall in the steep part of the curve (M3 to M5 early), so the change is not
separable from ordinary progress; the one review aimed at a stall (25) was inert, and the harness
change that followed it (the read budget, arm B2) is what moved the run.

## 5. Primary reading 4: cost

| Phase | Iterations | Prompt tokens | Completion tokens | Active hours |
|---|---|---|---|---|
| M1 to M3 (1 to 2) | 2 | 4.2 M | 0.05 M | 0.6 |
| M4 (3 to 11) | 9 | 17.8 M | 0.31 M | 2.9 |
| M5/M6 under arm B (12 to 32) | 21 | 86.8 M | 0.33 M | 15.2 |
| M5/M6 under arm B2 (33 to 123) | 91 | 214.0 M | 6.64 M | 59.2 |
| Total (incl. iteration 124) | 124 | 322.9 M | 7.33 M | 77.98 |

Spark electricity, integrated from the strip's per-outlet log over the iteration windows only:
head 13.2 kWh, worker 12.8 kWh, 26.06 kWh for the run; mean 169.6 W (head) and 164.8 W (worker)
during iterations, p95 183 and 179 W. (Over the full wall-clock span 21 Oct 16:52 to 25 Oct
16:34, including pauses and the crash gap, 28.25 kWh.)

## 6. Arm B against arm B2 (the loop-engineering reading)

| | Arm B (1 to 32) | Arm B2 (33 to 123) |
|---|---|---|
| Iterations | 32 | 91 |
| Successful writes | 17 | 720 |
| Iterations with at least one write | 6 of 32 | 90 of 91 |
| Read-type calls | 2,148 | 5,023 |
| Prompt tokens per iteration | 3.4 M | 2.35 M |
| Completion tokens | 0.69 M | 6.64 M |
| End reasons | end_iteration 24, turn_cap 4, token_cap 1 | turn_cap 37, token_cap 36, end_iteration 12, time_limit 2 |
| M5 progress | 0.463 plateau for 26 iterations | 0.463 → 0.988 |
| M6 progress | 0 | 0 → 0.982 |

One rule, "six reads before a substantive write, stubs do not count", turned a model that
declared its plan every iteration and never wrote into one that wrote in 90 of 91 iterations.
The B2 iterations end on caps (turn or token) rather than by the model's own choice: the model
uses every turn it is given.

## 7. Predictions scored

- **P1** (M1, M2 within day 1): supported, both at 0.39 h.
- **P2** (M3 by day 2, M4 by day 3): supported, 0.64 h and 3.54 h, both inside day 1.
- **P3** (M5 at 70 %, band 50 to 90 %, at day 4; combat ordering and save/load last): the level
  is falsified upward, M5 was at 0.988 by 72 h and complete in substance (the remaining test was
  the authoring error); the named last tests were right (combat `orders`, `load_restores_state`,
  `save_labstate` were the last three honest failures).
- **P4** (M6 not reached by day 7 without review; six of ten checkpoints by day 7 with reviews):
  falsified upward. All ten checkpoints passed by 55.93 active hours (day 3) and the frame
  renders by 61.22 h, with no review reply after iteration 27 (the only one in that stretch was
  inert).
- **P5** (reviews +5 points, band 0 to +15, in the next 10 iterations): mixed. Two early reviews
  moved the fraction by +13.2 and +21.7 points (the second above the band) in the steep part of
  the curve where any help looks large; the one review aimed at a stall was inert (0.0).
- **Falsifier** ("M6 reaches 10 of 10 checkpoints by day 4 with no review → the premise is
  wrong"): fires. The checkpoints passed within day 3; the reviews that were in force by then had
  stopped moving anything by iteration 27. The study's premise, that a mid-tier local model needs
  frontier code guidance for the game-logic half, is wrong for this spec. What it needed was
  loop engineering (iteration and request caps, then the read budget) and a correct test suite.

## 8. Findings beyond the predictions

1. **The builder out-read its own test suite.** At iteration 94 it showed from the frozen data that
   two tests could not be satisfied by any map-consistent engine, named the transposition that
   produced them, and declined to change the engine because that would break M4. The session's
   independent derivation agreed (Addendum 7). Twenty-one iterations (102 to 123, about 14 active
   hours and 50 million prompt tokens) were spent against an unsatisfiable pair of assertions;
   that cost belongs to the spec author.
2. **Gaming a loop rule.** The first read-budget rule (reads reopen after any write) was met with
   an 11-line stub in the first iteration it applied (Addendum 4a); the rule had to define a
   substantive write.
3. **Harness faults cost more than builder faults.** Three cap corrections, one crash (17.7 h of
   wall clock, excluded from the day count), one tamper-snapshot restore at the final resume.
4. **No path violations by the builder** beyond the one counted at the stop-file handling.

## 9. What the paper says

A 3-bit, 2-GPU local model built a working Wasteland engine (codecs, containers, maps, scenario
compiler, rules, headless walkthrough, curses frame) from a seven-document spec in 78 active
hours, 26 kWh and 323 million prompt tokens, without frontier code guidance; the frontier's
contribution was the spec, the tests, and four harness rules. The spec author's two errors were
found by the builder. Vendor names stay out; the model is "a 3-bit quantised open mixture-of-
experts model on two desktop GPUs" in the body, with the exact identity in the reproducibility
section.
