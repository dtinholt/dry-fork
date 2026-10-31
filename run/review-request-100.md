# Review request, iteration 100

Run w1-2026-10-21; model deepseek-v41-flash-exl3; trigger: every 25 iterations.

Reply by writing `review-reply-100.md` in /Users/dtinholt/wasteland-build/runs/w1-2026-10-21. The run is not paused; a reply is injected into the next iteration that starts after it appears.

## Test summary

- M1: 89/89 passed, 0 failed, 0 errors [PASS]
- M2: 107/107 passed, 0 failed, 0 errors [PASS]
- M3: 94/94 passed, 0 failed, 0 errors [PASS]
- M4: 76/76 passed, 0 failed, 0 errors [PASS]
- M5: 81/82 passed, 1 failed, 0 errors [open]
- M6: 48/55 passed, 7 failed, 0 errors [open]

First 8 of 8 failing tests:
* [M5] tests.test_m5_rules::test_bump_is_not_a_step
    Failed: after 12 steps west and one bump (LR-15): first difference at x: expected 3, got 4
    after 12 steps west and one bump (LR-15): first difference at x: expected 3, got 4
* [M6] tests.test_m6_playable::test_look
    Failed: look west from (15, 20) (SPEC-06 section 3): first difference at <root> (length): expected 1, got 0
    look west from (15, 20) (SPEC-06 section 3): first difference at <root> (length): expected 1, got 0
* [M6] tests.test_m6_playable::test_repeat_limit
    Failed: wlengine.headless.run (repeat_until never true (SPEC-06 5.1 exit code 2)): expected RepeatLimitError, but it returned [{'seq': 0, 'type': 'new_game', 'seed': 20261021}, {'seq': 1, 'type': 'paragraph', 'n': 1}, {'seq': 2, 'type': 'input', 'key': 'Z'}, {'seq': 3, 'type': 'ignored...
    wlengine.headless.run (repeat_until never true (SPEC-06 5.1 exit code 2)): expected RepeatLimitError, but it returned [{'seq': 0, 'type': 'new_game', 'seed': 20261021}, {'seq': 1, 'type': 'paragraph', 'n': 1}, 
* [M6] tests.test_m6_playable::test_malformed_script
    Failed: wlengine.headless.run (token 'JUMP' (SPEC-06 5.1 exit code 4)): expected ScriptError, but it returned [{'seq': 0, 'type': 'new_game', 'seed': 20261021}, {'seq': 1, 'type': 'paragraph', 'n': 1}, {'seq': 2, 'type': 'input', 'key': 'JUMP'}, {'seq': 3, 'type': 'igno...
    wlengine.headless.run (token 'JUMP' (SPEC-06 5.1 exit code 4)): expected ScriptError, but it returned [{'seq': 0, 'type': 'new_game', 'seed': 20261021}, {'seq': 1, 'type': 'paragraph', 'n': 1}, {'seq': 2, 'type': 'input', 'key
* [M6] tests.test_m6_playable::test_render_frame_party
    Failed: wlengine.ui.render_frame raised AttributeError: "module 'wlengine.headless' has no attribute 'first_frame_state'"
    module 'wlengine.headless' has no attribute 'first_frame_state'
    During handling of the above exception, another exception occurred:
    wlengine.ui.render_frame raised AttributeError: "module 'wlengine.headless' has no attribute 'first_frame_state'"
* [M6] tests.test_m6_playable::test_render_status_line
    Failed: wlengine.ui.render_frame raised AttributeError: "module 'wlengine.headless' has no attribute 'first_frame_state'"
    module 'wlengine.headless' has no attribute 'first_frame_state'
    During handling of the above exception, another exception occurred:
    wlengine.ui.render_frame raised AttributeError: "module 'wlengine.headless' has no attribute 'first_frame_state'"
* [M6] tests.test_m6_playable::test_render_viewport
    Failed: wlengine.ui.render_frame raised AttributeError: "module 'wlengine.headless' has no attribute 'first_frame_state'"
    module 'wlengine.headless' has no attribute 'first_frame_state'
    During handling of the above exception, another exception occurred:
    wlengine.ui.render_frame raised AttributeError: "module 'wlengine.headless' has no attribute 'first_frame_state'"
* [M6] tests.test_m6_playable::test_cli_render_frame
    Failed: exit code of wl --data DIR --render-frame (SPEC-06 7): expected 0, got 1
    exit code of wl --data DIR --render-frame (SPEC-06 7): expected 0, got 1

## Worklog tail

[earlier entries omitted]

### iter 94 note (2026-10-24T19:21:52-05:00)
## Iteration 94 (M5 focus) — M5's last failure is a frozen inconsistency; M6 has 8 fixable failures

### What I did
Read the failing M5 test and probed the frozen data end to end (probe282-289.py).

### Finding: `test_bump_is_not_a_step` cannot be satisfied by any map-consistent engine
The test (tests/test_m5_rules.py:513) runs `["LEFT"]*13` from the Saltwell start
(15,20) and expects:
* checkpoint: `location 1, x 3, y 20, steps 12` (i.e. 12 *successful* steps west,
  so cell (3,20) must be **passable**), and
* tail: `bump x 2, y 20, action_class 11, action 0` (so cell (2,20) must be
  **blocked with class 11**).

The frozen data says the opposite, and every frozen source agrees with each other:
* `SPEC/scenario/map1-saltwell.json`: `tiles[20] = [25,0,0,11,0,...]` → tile 11
  (cactus) at **x=3**; `action_class[20][3] = 11`; `action_class[20][2] = 0`.
* SPEC-05 section 5.2 ASCII art row 20 = `|..Y...........;...............|`
  → `Y` (cactus) at column **3** (verified: all 32 art rows match the JSON tiles
  exactly under the glyph map `|`=25 `.`=0 `;`=18 `Y`=11 `T`=10 `b`=9 `w`=26
  `p`=24 `P`=23 `#`=16 `_`=17 `/`=19 `n`=21 `h`=22).
* The oracle (`tests/oracle_tool.py compiled`) expected `cells.image[20]` =
  `[35,10,10,21,...]` → image 21 = cactus at x=3, `actionClass[20][3]=11`.
* The engine's compiled map (probe287) matches the oracle byte for byte, and M4
  (76/76) asserts exactly that.

So the test wants the cactus at (2,20) while all frozen data puts it at (3,20).
No rule based on the map can produce a bump at (2,20): (2,20) is class 0 sand.
The engine's current behaviour (11 steps to x=4, then bump at (3,20) class 11
action 0) is the only map-consistent one. **Do not change the engine for this
test** — it would break M4 and the M6 walkthrough log.

(Curiosity worth remembering: reading the map *transposed* — `tiles[x][y]` —
would give exactly the test's expectation: `tiles[3][20]=17` walkable,
`tiles[2][20]=16` blocked, `actionClass[2][20]=11`. That is almost certainly how
the test's expectation was authored, but transposing passability would break the
whole walkthrough, so it is not a fix.)

### Next step (highest value): M6, 47/55, 8 failures — all look fixable
1. `wlengine.ui` does not exist → 4 failures (`test_render_frame_party`,
   `test_render_status_line`, `test_render_viewport`, `test_cli_render_frame`).
   Read tests/test_m6_playable.py:212-260 and SPEC-06 sections 2.1-2.4 + 7 for
   the exact API (`render_frame`, `render_status_line`, `render_viewport`) and
   write `src/wlengine/ui.py`.
2. `test_repeat_limit` / `test_malformed_script`: `wlengine.headless.run` must
   raise `RepeatLimitError` (SPEC-06 5.1 exit code 2) when a `repeat_until`
   never becomes true, and `ScriptError` (exit code 4) for an unknown token like
   `JUMP`. Both classes already exist in headless.py — they are just not raised.
3. `test_cli_headless` / `test_cli_render_frame`: the `wl` CLI must exit 0 on the
   walkthrough and on `--data DIR --render-frame` (SPEC-06 5.1, 7). Check how the
   CLI entry point is invoked by the test (probably `python3 -m wlengine.cli` or
   a `wl` script) and make sure it exists and returns the right codes.

### Probes written this iteration
probe282-289.py (map/art/oracle/engine comparisons, reference-log bump dump).

[harness] iter 94 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe282.py, tests/fixtures-generated/probe283.py, tests/fixtures-generated/probe284.py, tests/fixtures-generated/probe285.py, tests/fixtures-generated/probe286.py, tests/fixtures-generated/probe287.py, tests/fixtures-generated/probe288.py, tests/fixtures-generated/probe289.py

[harness] iter 95 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: src/wlengine/ui.py

[harness] iter 96 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe290.py, tests/fixtures-generated/probe291.py, tests/fixtures-generated/probe292.py, tests/fixtures-generated/probe293.py

[harness] iter 97 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe294.py, tests/fixtures-generated/probe295.py, tests/fixtures-generated/probe296.py, tests/fixtures-generated/probe297.py, tests/fixtures-generated/probe298.py, tests/fixtures-generated/probe299.py, tests/fixtures-generated/probe300.py, tests/fixtures-generated/probe301.py

[harness] iter 98 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe311.py, tests/fixtures-generated/probe312.py, tests/fixtures-generated/probe313.py, tests/fixtures-generated/probe314.py, tests/fixtures-generated/probe315.py, tests/fixtures-generated/probe316.py, tests/fixtures-generated/probe317.py

[harness] iter 99 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->48/55; files changed: src/wlengine/__main__.py, src/wlengine/headless.py, src/wlengine/scenario.py

[harness] iter 100 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 48->48/55; files changed: tests/fixtures-generated/probe318.py, tests/fixtures-generated/probe319.py, tests/fixtures-generated/probe320.py, tests/fixtures-generated/probe320data/ALLHTDS1, tests/fixtures-generated/probe320data/ALLPICS1, tests/fixtures-generated/probe320data/COLORF.FNT, tests/fixtures-generated/probe320data/CURS, tests/fixtures-generated/probe320data/END.CPA


## Diff since last review (d20b6a476a..f2fcd024b5)

```diff
 WORKLOG.md                                         |  541 ++++++
 src/wlengine/__main__.py                           |  112 ++
 src/wlengine/combat.py                             |  166 +-
 src/wlengine/headless.py                           |   72 +-
 src/wlengine/scenario.py                           |   18 +
 src/wlengine/ui.py                                 |  127 ++
 tests/fixtures-generated/dd/GAME1                  |  Bin 22722 -> 22722 bytes
 tests/fixtures-generated/dd/LABSTATE.BIN           |  Bin 0 -> 42 bytes
 tests/fixtures-generated/dump166.txt               |   29 +
 tests/fixtures-generated/dump167src.txt            |    7 +
 tests/fixtures-generated/dump169support.txt        |  531 ++++++
 tests/fixtures-generated/dump171m5.txt             |  834 +++++++++
 tests/fixtures-generated/dump173.txt               |  795 ++++++++
 tests/fixtures-generated/dump174.txt               |   37 +
 tests/fixtures-generated/dump175.txt               |   92 +
 tests/fixtures-generated/dump176.txt               |  506 +++++
 tests/fixtures-generated/dump177.txt               |  100 +
 tests/fixtures-generated/dump178.txt               |   81 +
 tests/fixtures-generated/dump179.txt               |  148 ++
 tests/fixtures-generated/dump180.txt               |    4 +
 tests/fixtures-generated/dump181.txt               |   13 +
 tests/fixtures-generated/dump183.txt               |  621 +++++++
 tests/fixtures-generated/dump184.txt               |  850 +++++++++
 tests/fixtures-generated/dump185.txt               |  400 ++++
 tests/fixtures-generated/dump186.txt               |  346 ++++
 tests/fixtures-generated/dump187.txt               |  508 +++++
 tests/fixtures-generated/dump188.txt               |  533 ++++++
 tests/fixtures-generated/dump189.txt               | 1948 ++++++++++++++++++++
 tests/fixtures-generated/dump190.txt               |   41 +
 tests/fixtures-generated/dump191.txt               |  106 ++
 tests/fixtures-generated/dump192.txt               |  138 ++
 tests/fixtures-generated/dump193.txt               |  266 +++
 tests/fixtures-generated/dump197.txt               |  187 ++
 tests/fixtures-generated/dump198.txt               |  217 +++
 tests/fixtures-generated/dump199.txt               |  459 +++++
 tests/fixtures-generated/dump200.txt               |   36 +
 tests/fixtures-generated/dump201.txt               |  199 ++
 tests/fixtures-generated/dump202.txt               |  316 ++++
 tests/fixtures-generated/dump203.txt               |  889 +++++++++
 tests/fixtures-generated/dump204.txt               |  319 ++++
 tests/fixtures-generated/dump205.txt               |  322 ++++
 tests/fixtures-generated/dump206.txt               |  451 +++++
 tests/fixtures-generated/dump207.txt               |  127 ++
 tests/fixtures-generated/dump208.txt               |  326 ++++
 tests/fixtures-generated/dump209.txt               |  228 +++
 tests/fixtures-generated/dump210.txt               | 1390 ++++++++++++++
 tests/fixtures-generated/dump211.txt               |   52 +
 tests/fixtures-generated/dump212.txt               |  205 ++
 tests/fixtures-generated/dump213.txt               |    5 +
 tests/fixtures-generated/dump214.txt               |  122 ++
 tests/fixtures-generated/dump216.txt               | 1099 +++++++++++
 tests/fixtures-generated/dump217.txt               |   20 +
 tests/fixtures-generated/dump218.txt               |   29 +
 tests/fixtures-generated/dump219.txt               |    5 +
 tests/fixtures-generated/dump220.txt               |  116 ++
 tests/fixtures-generated/dump221.txt               |    6 +
 tests/fixtures-generated/dump222.txt               |  103 ++
 tests/fixtures-generated/dump224.txt               |  333 ++++
 tests/fixtures-generated/dump225.txt               |  361 ++++
 tests/fixtures-generated/dump226.txt               |  262 +++
 tests/fixtures-generated/dump227.txt               |   80 +
 tests/fixtures-generated/dump228.txt               |   14 +
 tests/fixtures-generated/dump229.txt               |  106 ++
 tests/fixtures-generated/dump230.txt               |    6 +
 tests/fixtures-generated/dump231.txt               |   14 +
 tests/fixtures-generated/dump232.txt               |  439 +++++
 tests/fixtures-generated/dump233.txt               |  256 +++
 tests/fixtures-generated/dump234.txt               |  140 ++
 tests/fixtures-generated/dump235.txt               |   32 +
 tests/fixtures-generated/dump236.txt               |    5 +
 tests/fixtures-generated/dump237.txt               |   10 +
 tests/fixtures-generated/dump238.txt               |   90 +
 tests/fixtures-generated/dump239.txt               |  183 ++
 tests/fixtures-generated/dump240.txt               |  356 ++++
 tests/fixtures-generated/dump241.txt               |  514 ++++++
 tests/fixtures-generated/dump242.txt               |  346 ++++
 tests/fixtures-generated/dump243.txt               |  834 +++++++++
 tests/fixtures-generated/dump244.txt               |  531 ++++++
 tests/fixtures-generated/dump245.txt               |  501 +++++
 tests/fixtures-generated/dump246.txt               |   39 +
 tests/fixtures-generated/dump247.txt               |   30 +
 tests/fixtures-generated/dump248.txt               |   96 +
 tests/fixtures-generated/dump249.txt               |  121 ++
 tests/fixtures-generated/dump250.txt               |  100 +
 tests/fixtures-generated/dump251.txt               |   16 +
 tests/fixtures-generated/dump252.txt               |  135 ++
 tests/fixtures-generated/dump259eng.txt            |  519 ++++++
 tests/fixtures-generated/dump259ref.txt            |  346 ++++
 tests/fixtures-generated/probe149.py               |   54 +
 tests/fixtures-generated/probe150.py               |   90 +
 tests/fixtures-generated/probe151.py               |   45 +
 tests/fixtures-generated/probe152.py               |   57 +
 tests/fixtures-generated/probe153.py               |   51 +
 tests/fixtures-generated/probe154.py               |   54 +
 tests/fixtures-generated/probe155.py               |   46 +
 tests/fixtures-generated/probe156.py               |   68 +
 tests/fixtures-generated/probe157.py               |   36 +
 tests/fixtures-generated/probe158.py               |   46 +
 tests/fixtures-generated/probe159.py               |   61 +
 tests/fixtures-generated/probe160.py               |   51 +
 tests/fixtures-generated/probe161.py               |   41 +
 tests/fixtures-generated/probe162.py               |   53 +
 tests/fixtures-generated/probe163.py               |   37 +
 tests/fixtures-generated/probe164.py               |   59 +
 tests/fixtures-generated/probe165.py               |   56 +
 tests/fixtures-generated/probe166.py               |   58 +
 tests/fixtures-generated/probe167.py               |   43 +
 tests/fixtures-generated/probe168.py               |   53 +
 tests/fixtures-generated/probe169.py               |   55 +
 tests/fixtures-generated/probe170.py               |   86 +
 tests/fixtures-generated/probe171.py               |   60 +
 tests/fixtures-generated/probe172.py               |   86 +
 tests/fixtures-generated/probe173.py               |   70 +
 tests/fixtures-generated/probe174.py               |   40 +
 tests/fixtures-generated/probe175.py               |   66 +
 tests/fixtures-generated/probe176.py               |   27 +
 tests/fixtures-generated/probe177.py               |   56 +
 tests/fixtures-generated/probe178.py               |   50 +
 tests/fixtures-generated/probe179.py               |   69 +
 tests/fixtures-generated/probe180.py               |   41 +
 tests/fixtures-generated/probe181.py               |   34 +
 tests/fixtures-generated/probe182.py               |   31 +
 tests/fixtures-generated/probe183.py               |   71 +
 tests/fixtures-generated/probe184.py               |   30 +
 tests/fixtures-generated/probe185.py               |   37 +
 tests/fixtures-generated/probe186.py               |   12 +
 tests/fixtures-generated/probe187.py               |   28 +
 tests/fixtures-generated/probe188.py               |   14 +
 tests/fixtures-generated/probe189.py               |   35 +
 tests/fixtures-generated/probe190.py               |   64 +
 tests/fixtures-generated/probe191.py               |   80 +
 tests/fixtures-generated/probe192.py               |   74 +
 tests/fixtures-generated/probe193.py               |   59 +
 tests/fixtures-generated/probe194.py               |   41 +
 tests/fixtures-generated/probe195.py               |   41 +
 tests/fixtures-generated/probe196.py               |   50 +
 tests/fixtures-generated/probe197.py               |   81 +
 tests/fixtures-generated/probe198.py               |   74 +
 tests/fixtures-generated/probe199.py               |   71 +
 tests/fixtures-generated/probe200.py               |   49 +
 tests/fixtures-generated/probe201.py               |   50 +
 tests/fixtures-generated/probe202.py               |   52 +
 tests/fixtures-generated/probe203.py               |   49 +
 tests/fixtures-generated/probe204.py               |   45 +
 tests/fixtures-generated/probe205.py               |   77 +
 tests/fixtures-generated/probe206.py               |   54 +
 tests/fixtures-generated/probe207.py               |   75 +
 tests/fixtures-generated/probe208.py               |   62 +
 tests/fixtures-generated/probe209.py               |   34 +
 tests/fixtures-generated/probe210.py               |   65 +
 tests/fixtures-generated/probe211.py               |   51 +
 tests/fixtures-generated/probe212.py               |   52 +
 tests/fixtures-generated/probe213.py               |   53 +
 tests/fixtures-generated/probe214.py               |   47 +
 tests/fixtures-generated/probe215.py               |   60 +
 tests/fixtures-generated/probe216.py               |   70 +
 tests/fixtures-generated/probe217.py               |   48 +
 tests/fixtures-generated/probe218.py               |   25 +
 tests/fixtures-generated/probe219.py               |   44 +
 tests/fixtures-generated/probe220.py               |   37 +
 tests/fixtures-generated/probe221.py               |   29 +
 tests/fixtures-generated/probe222.py               |   67 +
 tests/fixtures-generated/probe223.py               |   66 +
 tests/fixtures-generated/probe224.py               |   44 +
 tests/fixtures-generated/probe225.py               |   49 +
 tests/fixtures-generated/probe226.py               |   51 +
 tests/fixtures-generated/probe227.py               |   17 +
 tests/fixtures-generated/probe228.py               |   27 +
 tests/fixtures-generated/probe229.py               |   29 +
 tests/fixtures-generated/probe230.py               |   51 +
 tests/fixtures-generated/probe231.py               |   50 +
 tests/fixtures-generated/probe232.py               |   53 +
 tests/fixtures-generated/probe233.py               |   16 +
 tests/fixtures-generated/probe234.py               |   37 +
 tests/fixtures-generated/probe235.py               |   38 +
 tests/fixtures-generated/probe236.py               |   34 +
 tests/fixtures-generated/probe237.py               |   25 +
 tests/fixtures-generated/probe238.py               |   24 +
 tests/fixtures-generated/probe239.py               |   22 +
 tests/fixtures-generated/probe240.py               |   66 +
 tests/fixtures-generated/probe241.py               |   26 +
 tests/fixtures-generated/probe242.py               |   39 +
 tests/fixtures-generated/probe243.py               |   38 +
 tests/fixtures-generated/probe244.py               |   48 +
 tests/fixtures-generated/probe245.py               |   52 +
 tests/fixtures-generated/probe246.py               |   70 +
 tests/fixtures-generated/probe247.py               |   50 +
 tests/fixtures-generated/probe248.py               |   25 +
 tests/fixtures-generated/probe250.py               |   62 +
 tests/fixtures-generated/probe251.py               |   39 +
 tests/fixtures-generated/probe252.py               |   36 +
 tests/fixtures-generated/probe253.py               |   44 +
 tests/fixtures-generated/probe254.py               |   45 +
 tests/fixtures-generated/probe255.py               |   96 +
 tests/fixtures-generated/probe256.py               |   73 +
 tests/fixtures-generated/probe257.py               |   55 +
 tests/fixtures-generated/probe258.py               |   94 +
 tests/fixtures-generated/probe259.py               |   29 +
 tests/fixtures-generated/probe260.py               |   41 +
 tests/fixtures-generated/probe261.py               |   48 +
 tests/fixtures-generated/probe262.py               |   68 +
 tests/fixtures-generated/probe263.py               |   43 +
 tests/fixtures-generated/probe264.py               |   21 +
 tests/fixtures-generated/probe265.py               |   52 +
 tests/fixtures-generated/probe266.py               |   39 +
 tests/fixtures-generated/probe267.py               |   41 +
 tests/fixtures-generated/probe268.py               |   59 +
 tests/fixtures-generated/probe269.py               |   23 +
 tests/fixtures-generated/probe270.py               |   41 +
 tests/fixtures-generated/probe271.py               |   38 +
 tests/fixtures-generated/probe272.py               |   93 +
 tests/fixtures-generated/probe273.py               |   34 +
 tests/fixtures-generated/probe274.py               |   39 +
 tests/fixtures-generated/probe275.py               |   39 +
 tests/fixtures-generated/probe276.py               |   44 +
 tests/fixtures-generated/probe277.py               |   70 +
 tests/fixtures-generated/probe278.py               |   45 +
 tests/fixtures-generated/probe279.py               |   43 +
 tests/fixtures-generated/probe280.py               |   49 +
 tests/fixtures-generated/probe281.py               |   43 +
 tests/fixtures-generated/probe282.py               |   67 +
 tests/fixtures-generated/probe283.py               |   30 +
 tests/fixtures-generated/probe284.py               |   19 +
 tests/fixtures-generated/probe285.py               |   23 +
 tests/fixtures-generated/probe286.py               |   60 +
 tests/fixtures-generated/probe287.py               |   60 +
 tests/fixtures-generated/probe288.py               |   54 +
 tests/fixtures-generated/probe289.py               |   32 +
 tests/fixtures-generated/probe290.py               |   97 +
 tests/fixtures-generated/probe291.py               |   22 +
 tests/fixtures-generated/probe292.py               |   47 +
 tests/fixtures-generated/probe293.py               |   56 +
 tests/fixtures-generated/probe294.py               |   67 +
 tests/fixtures-generated/probe295.py               |   38 +
 tests/fixtures-generated/probe296.py               |   32 +
 tests/fixtures-generated/probe297.py               |   32 +
 tests/fixtures-generated/probe298.py               |   31 +
 tests/fixtures-generated/probe299.py               |   31 +
 tests/fixtures-generated/probe300.py               |   55 +
 tests/fixtures-generated/probe301.py               |   29 +
 tests/fixtures-generated/probe302.py               |   30 +
 tests/fixtures-generated/probe303.py               |   40 +
 tests/fixtures-generated/probe304.py               |   45 +
 tests/fixtures-generated/probe305.py               |   39 +
 tests/fixtures-generated/probe306.py               |   51 +
 tests/fixtures-generated/probe307.py               |   72 +
 tests/fixtures-generated/probe308.py               |   61 +
 tests/fixtures-generated/probe309.py               |   45 +
 tests/fixtures-generated/probe310.py               |   35 +
 tests/fixtures-generated/probe311.py               |   71 +
 tests/fixtures-generated/probe312.py               |   60 +
 tests/fixtures-generated/probe313.py               |   41 +
 tests/fixtures-generated/probe314.py               |   51 +
 tests/fixtures-generated/probe315.py               |   45 +
 tests/fixtures-generated/probe316.py               |   47 +
 tests/fixtures-generated/probe317.py               |   55 +
 tests/fixtures-generated/probe318.py               |   59 +
 tests/fixtures-generated/probe319.py               |   53 +
 tests/fixtures-generated/probe320.py               |   39 +
 tests/fixtures-generated/probe320data/ALLHTDS1     |  Bin 0 -> 807 bytes
 tests/fixtures-generated/probe320data/ALLPICS1     |  Bin 0 -> 2204 bytes
 tests/fixtures-generated/probe320data/COLORF.FNT   |  Bin 0 -> 1024 bytes
 tests/fixtures-generated/probe320data/CURS         |  Bin 0 -> 512 bytes
 tests/fixtures-generated/probe320data/END.CPA      |  Bin 0 -> 3050 bytes
 tests/fixtures-generated/probe320data/GAME1        |  Bin 0 -> 22722 bytes
 tests/fixtures-generated/probe320data/IC0_9.WLF    |  Bin 0 -> 1280 bytes
 .../fixtures-generated/probe320data/LABHOOKS.JSON  |  150 ++
 tests/fixtures-generated/probe320data/LABSKILL.BIN |  Bin 0 -> 72 bytes
 tests/fixtures-generated/probe320data/LABSTR.BIN   |  Bin 0 -> 1938 bytes
 .../fixtures-generated/probe320data/LABTABLES.BIN  |  Bin 0 -> 1080 bytes
 .../fixtures-generated/probe320data/LOCATIONS.JSON |    1 +
 tests/fixtures-generated/probe320data/MASKS.WLF    |    1 +
 .../probe320data/PARAGRAPHS.JSON                   |  125 ++
 tests/fixtures-generated/probe320data/TITLE.PIC    |  Bin 0 -> 18432 bytes
 tests/fixtures-generated/probe321.py               |   49 +
 tests/fixtures-generated/probe322.py               |   64 +
 tests/fixtures-generated/probe323.py               |   41 +
 tests/fixtures-generated/probe324.py               |   30 +
 278 files changed, 32775 insertions(+), 40 deletions(-)

diff --git a/WORKLOG.md b/WORKLOG.md
index af7be5a..42546e1 100644
--- a/WORKLOG.md
+++ b/WORKLOG.md
@@ -3526,3 +3526,544 @@ and SPEC/scenario/walkthrough-reference-log.json):
 [harness] iter 74 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 75->75/82; M6 8->8/55; files changed: tests/fixtures-generated/probe139.py, tests/fixtures-generated/probe140.py, tests/fixtures-generated/probe141.py
 
 [harness] iter 75 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 75->79/82; M6 8->8/55; files changed: src/wlengine/headless.py, tests/fixtures-generated/dump143.txt, tests/fixtures-generated/dump144.txt, tests/fixtures-generated/probe142.py, tests/fixtures-generated/probe143.py, tests/fixtures-generated/probe144.py, tests/fixtures-generated/probe145.py, tests/fixtures-generated/probe146.py
+
+[harness] iter 76 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 8->8/55; files changed: tests/fixtures-generated/probe149.py, tests/fixtures-generated/probe150.py, tests/fixtures-generated/probe151.py, tests/fixtures-generated/probe152.py, tests/fixtures-generated/probe153.py, tests/fixtures-generated/probe154.py, tests/fixtures-generated/probe155.py, tests/fixtures-generated/probe156.py
+
+[harness] iter 77 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 8->8/55; files changed: tests/fixtures-generated/dump166.txt, tests/fixtures-generated/dump167src.txt, tests/fixtures-generated/dump169support.txt, tests/fixtures-generated/dump171m5.txt, tests/fixtures-generated/probe166.py, tests/fixtures-generated/probe167.py, tests/fixtures-generated/probe168.py, tests/fixtures-generated/probe169.py
+
+[harness] iter 78 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 8->8/55; files changed: tests/fixtures-generated/probe170.py, tests/fixtures-generated/probe171.py, tests/fixtures-generated/probe172.py
+
+### iter 79 note (2026-10-24T09:55:09-05:00)
+## Iter 79 (M5 focus; 79/82 M5, 8/55 M6)
+
+### Big finding: the reference log's `cell_changes` are SORTED + DEDUPED
+`SPEC/scenario/walkthrough-reference-log.json` checkpoint states carry
+`cell_changes` sorted by (location, y, x) and with duplicate (loc,x,y) entries
+collapsed to the LAST one. Evidence (probe179, dump179.txt):
+- CP4 ref `[[0,30,41,0,0,13],[1,8,17,0,0,28]]`; ours
+  `[[1,8,17,0,0,28],[0,30,41,5,1,13],[0,30,41,0,0,13]]`.
+- CP5 ref has `[0,31,41,0,0,22]` which we never produce at all.
+- CP6 ref `[2,26,14,4,1,29]`; ours has both `[2,26,14,4,1,30]` and
+  `[2,26,14,4,1,29]`.
+- CP8 ref `[3,9,6,0,0,37]`; ours has `[3,9,6,5,1,37]` then `[3,9,6,0,0,37]`.
+So: `snapshot()` must emit `sorted(set-by-(loc,x,y) keeping last, key=(loc,y,x))`.
+That alone fixes the `cell_changes[0][0] expected 1 got 0` /
+`expected 0 got 1` / `expected 0 got 5` failures in test_load_restores_state
+and the M6 CP4/CP5/CP6..CP9 checkpoint tests. NOTE: `test_save_labstate`
+already sorts the *checkpoint* value itself, so it passes either way; but
+`test_load_restores_state` compares raw snapshots, so the snapshot must be
+sorted. Also `write_save_files` already sorts for LABSTATE.BIN — keep that.
+
+### Second finding: `[0,31,41,0,0,22]` is a missing cell change
+At CP5 the reference has a change at overworld (31,41) with image 22 that we
+never record. (30,41) is the raider-fight loot cell (class 5 -> tail 0/0,
+image 13). (31,41) is presumably the *second* loot/encounter cell of the same
+fight, or a second tail. Check SPEC-03 9.6 / SPEC-05 5.1 for the overworld
+cells at (30,41) and (31,41) and why both change. Likely the encounter record
+at (30,41) has a tail that also touches (31,41), or there are two adjacent
+class-5 cells and our `apply_loot` only handles one.
+
+### Third finding: `test_bump_is_not_a_step` — the cactus is at (3,20), not (2,20)
+dump174.txt: our engine walks 15->4 (11 moves) then bumps (3,20) twice; the
+test wants 12 moves then a bump at (2,20). The compiled map1 has class 11 at
+(3,20) (tile 11 = cactus, matching SPEC-05 art `Y` at (3,20) and the JSON
+`action_class[20][3] == 11`). The test's expectation of a bump at (2,20) with
+`action_class 11` therefore implies the *compiled* map must have the cactus at
+(2,20) — i.e. our compiler writes the map one column off, OR the test's
+`runner.run("bump", ...)` uses a different data dir. Since M3 (94/94) passes
+and the oracle agrees with our compiled cells, the most likely cause is that
+the walkthrough/`bump` script starts at x=15 and the test expects 12 steps:
+15-12 = 3, so the bump cell is (2,20) only if the party starts at x=14. Check
+`sc.start` for location 1: ours is (15,20). SPEC-05 5.2 says the pump is at
+(15,11) and the gate at (15,31)/(16,31); the start is probably (15,20) per
+scenario.json. So the test expects the *cactus* at (2,20) — meaning the
+compiled map should have class 11 at (2,20) AND (3,20)? No: 12 steps from 15
+lands on 3, then the 13th LEFT bumps (2,20). So the reference map has the
+cactus at (2,20), not (3,20). Our compiler is off by one column for this cell
+only (or the SPEC art `Y` at column 3 is the *tile* while the class-11 cell is
+at column 2). Re-read SPEC-05 5.2's table: it lists non-plain cells; the cactus
+is not in that table, so it is a plain tile-11 cell whose class comes from the
+tileset. Check `tiles.json` / the tileset: tile 11 (cactus) may be
+"impassable" so the compiler should set class 11 on the cell *west* of the
+drawn tile, or the art column is 1-based. Compare with the reference log:
+there is no bump at (2,20) in the reference walkthrough, so this is only
+exercised by the M5 test. Next: dump `tiles.json` entry 11 and the compiler's
+tile->class rule, and check whether SPEC-03 9.8 says a tile's `impassable`
+flag sets class 11 on the tile cell itself.
+
+### Fourth finding: raider orders (seed 3, round 2, slot 1 wants ['reload'])
+Not yet diagnosed this iteration. `auto_orders` returns `advance` when the
+member has no ranged weapon / no ammo. Member 1 has Ranch pistol (id 3) with
+status 6 and Pistol rounds (id 4) with status 2. Reference CP4 shows member 1
+items `[[3,0],[4,2],[7,0]]` (weapon status 0 = unloaded, ammo 2) while ours is
+`[[3,6],[4,2],[7,0]]` (status 6 = loaded). So our `loaded`/status handling for
+weapons is wrong: a weapon's status byte is NOT the loaded-round count in the
+reference (it is 0 at CP4). That also explains the `reload` order. Fix: weapon
+status semantics — check SPEC-04 9.4 (armour, ammunition and jams) and
+SPEC-02 4.4 for the item status byte meaning. Likely status 0 = unloaded and
+the loaded rounds live in the ammo item's status; `weapon_ammo` must read the
+ammo item, not the weapon status.
+
+### Fifth finding: rank/skill_points
+Reference CP4+ has every member `rank='Hand'`, `skill_points=2`; ours stays
+`Drifter`/0. So promotion (LR-46/LR-47) must fire when xp crosses the
+threshold; our `xp` values match the reference, so the promotion check is
+missing or uses the wrong threshold. Check `rules.xp_threshold` /
+`ref_level_after` and where `rank`/`skill_points` are updated (probably in
+`end_of_round` / `victory`).
+
+### Sixth finding: ammo counts
+Reference CP4 member 0 items `[[3,0],[4,2],[7,0]]` vs ours `[[3,6],[4,2],[7,0]]`;
+CP8 ref `[[3,4],[4,1],...]` vs ours `[[3,6],[4,2],...]`. So firing consumes
+rounds and the weapon status is the *rounds loaded* (0..6). At CP4 the weapon
+is empty (0) and the ammo box has 2. Our engine never decrements. This is the
+same root cause as the raider-orders failure.
+
+### Files written this iteration (probes only, no engine change)
+tests/fixtures-generated/probe173..182.py and dump173..182.txt.
+
+### Next iteration plan (in order)
+1. `snapshot()`: sort + dedup `cell_changes` by (loc,x,y) keeping the last,
+   ordered by (loc,y,x). Re-run M5 + M6; expect test_load_restores_state and
+   the M6 CP4..CP9 checkpoint tests to pass.
+2. Weapon/ammo status: make the weapon status byte the loaded-round count,
+   decrement on fire, `reload` when 0 and an ammo box is present. Fixes
+   test_raider_fight_rules[orders] and the CP4/CP8 item diffs.
+3. Promotion: set `rank`/`skill_points` when xp crosses the threshold.
+4. The missing `[0,31,41,0,0,22]` cell change (second loot cell).
+5. test_bump_is_not_a_step: decide whether the cactus class-11 cell is (2,20)
+   or (3,20) from tiles.json + SPEC-03 9.8, and fix the compiler or the test
+   expectation accordingly (M3 passes, so be careful).
+6. Then M6 (47 failing) — most are the same checkpoint snapshot diffs.
+
+[harness] iter 79 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 8->9/55; files changed: src/wlengine/headless.py, tests/fixtures-generated/dump173.txt, tests/fixtures-generated/dump174.txt, tests/fixtures-generated/dump175.txt, tests/fixtures-generated/dump176.txt, tests/fixtures-generated/dump177.txt, tests/fixtures-generated/dump178.txt, tests/fixtures-generated/dump179.txt
+
+[harness] iter 80 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/dump183.txt, tests/fixtures-generated/dump184.txt, tests/fixtures-generated/dump185.txt, tests/fixtures-generated/dump186.txt, tests/fixtures-generated/dump187.txt, tests/fixtures-generated/dump188.txt, tests/fixtures-generated/dump189.txt, tests/fixtures-generated/dump190.txt
+
+[harness] iter 81 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/dump197.txt, tests/fixtures-generated/dump198.txt, tests/fixtures-generated/probe195.py, tests/fixtures-generated/probe196.py, tests/fixtures-generated/probe197.py, tests/fixtures-generated/probe198.py
+
+### iter 82 note (2026-10-24T11:57:36-05:00)
+### Iter 82 findings (probes 199-208, dumps 199-208; no engine change yet)
+
+**A. `test_save_labstate` / M6 CP5 cell_changes — ROOT CAUSE FOUND.**
+The reference log's CP5-pre-save state has `cell_changes = [[0,30,41,0,0,13],
+[0,31,41,0,0,22], [1,8,17,0,0,28]]` — i.e. the *second* overworld loot cell
+(31,41) IS present at CP5. Our engine is missing it (we only have 2 entries).
+Reference events: seq 282 `cell_change (0,30,41,class5,action1,image13)`, 283
+`money +75`, 284 `cell_change (0,30,41,class0,action0,image13)`, then 289
+`cell_change (0,31,41,class0,action0,image22)` — that last one is the *tail* of
+the (30,41) encounter record (new_class 0, new_action 0) applied to the cell
+(31,41)?? No: seq 289 happens right after `move` to (31,41) at seq 287 and
+`paragraph 9` at 288. So (31,41) is a class-1 PRINT cell whose record has
+`new_class 0` tail; stepping onto it emits `cell_change (31,41,0,0,22)`.
+Our engine never emits that cell_change, so our LABSTATE.BIN lacks the entry and
+the M6 CP5/CP6..CP9 snapshots differ at `cell_changes[1][0]` (expected 0, got 1
+= our entry [1,8,17,...] shifted into index 1). **Fix: apply the class-1 tail
+(new_class/new_action) on every PRINT cell step, emitting `cell_change` with the
+new class/action and the cell's image.** Check `maps.py`/`headless.py` step
+handling for class 1: it must emit cell_change when the record's tail changes
+the cell.
+
+**B. `test_raider_fight_rules[orders]` — ROOT CAUSE FOUND.**
+`wl_combat_ref.consistency` (tests/wl_combat_ref.py:183-220) tracks loads from
+`PARTY_CP3[s]["load"]` (slot1=6, slot2=8, slot3=6, slot4=6, slot5=8) and boxes
+(2,1,2,2,2). It expects `["fire",1]` while load>0, `["reload"]` when load==0 and
+boxes>0, `["unjam"]` when jammed. Our `auto_orders` uses `member["loaded"]`
+which we never initialise from the item status byte, and `weapon_ammo` falls
+back to `rec["capacity"]` — so after a jam we set `loaded=0` but on the next
+round `weapon_ammo` returns capacity again (or `loaded` is stale). **Fix: make
+the weapon's item status byte (items[0][1], bits 0-6) the single source of the
+load; `weapon_ammo` = `items[0][1] & 0x7F`; jam sets it to 0x80; spend_ammo
+decrements it; reload sets it to capacity and decrements the ammo box's status.**
+Also `auto_orders` must use `status & 0x80` for jam (not `m["jammed"]`), and
+`["fire",1]`/`["reload"]`/`["unjam"]`/`["advance",1]`/`["unarmed",1]` exactly.
+
+**C. `test_bump_is_not_a_step` — cactus cell.**
+SPEC-05 5.2 art row 20 is `|..Y...........;...............|` → `Y` at x=2, and
+`map1-saltwell.json` has `tiles[20] = [25,0,0,11,...]` (tile 11 at x=3) with
+`action_class[20] = [11,0,0,11,...]` (class 11 at x=0 and x=3). The test wants
+12 steps west from x=15 then a bump at (2,20) with class 11. 15-12 = 3, so the
+12th step lands on x=3 and the 13th (LEFT) bumps x=2. Our engine walks 11 moves
+then bumps (3,20) — i.e. our step counter/`bump` handling treats the bump as a
+step, or our map has class 11 at x=3 blocking the 12th move. Since M3 passes,
+the compiled cells match the oracle; the bug is in the *movement* code: a bump
+must not increment `steps` and must not move. Check `headless.py` `move`/`bump`
+for class 11: it must emit `bump` and NOT increment steps, and the party must
+stay put. Our dump174 showed 11 moves then a bump at (3,20) — meaning the 12th
+LEFT was consumed as a bump at x=3 (class 11 at x=3 blocks). But the reference
+walkthrough has no bump at (3,20)... so the test's expectation implies the
+cactus class-11 cell is at x=2. **Next: dump `map1-saltwell.json` tiles/class
+columns 0..4 of row 20 and the SPEC-05 art again; if the JSON really has class
+11 at x=3, then the test's `runner.run("bump", ...)` must use a different data
+dir or the test is checking the *tile* (11) not the class. Read
+`tests/test_m5_rules.py::test_bump_is_not_a_step` (probe209 was written but not
+run) before changing anything.**
+
+**D. Promotion (LR-46) missing.** Reference CP4 has every member `rank="Hand"`,
+`skill_points=2`, `max_hp` raised by `2 + STR div 5`; ours stays Drifter/0.
+`rules.level_after`/`xp_threshold` exist. Add promotion in the victory path:
+after each `xp` event, while `level_after(level, xp) > level`: level += 1,
+max_hp += 2 + STR//5, hp += same unless dead, skill_points += 2, rank =
+`sc.rank(level)`, emit `promote` with member/level/max_hp/rank.
+
+**E. Ammo/status semantics (LR-38, SPEC-02 4.4).** Weapon item status byte bits
+0-6 = load; bit 7 = jammed (0x80..0x85). Ammo item status byte = count of boxes.
+Reference CP4 items: slot1 `[[3,0],[4,2],[7,0]]` (pistol empty after 6 shots),
+slot2 `[[5,3],[6,1],[7,0]]`, slot3 `[[3,1],[4,2]]`, slot4 `[[3,1],[4,2],[9,3]]`,
+slot5 `[[5,3],[6,2]]`. Our engine never decrements, so fix per B.
+
+**F. `test_victory_loot` tail.** Reference: after `combat_end` victory →
+`xp` (5 members, delta 14 = 3*12*2//5), `promote` for members 1-4 (member 5
+already level 2), then `cell_change (0,30,41,class5,action1,image13)`,
+`money +75 total 195`, `cell_change (0,30,41,class0,action0,image13)`. Our
+`test_victory_loot` expects exactly that. Note the loot fires *after* the xp
+events, and the loot cell's own tail is applied immediately (second
+cell_change).
+
+**G. M6 CP4 diff `party[0].hp` expected 25 got 24** — our member 1 hp is 24
+(never damaged) vs reference 25 (took 3 damage in round 4, seq 260). Follows
+from the combat fixes in B/E.
+
+### Files written this iteration
+probe199..209.py, dump199..208.txt (probes only; no engine change).
+
+### Next iteration plan (in order)
+1. Run probe209 (already written) to read `test_bump_is_not_a_step`,
+   `test_load_restores_state`, `test_checkpoint_matches_reference` verbatim.
+2. Fix the weapon status byte semantics in `src/wlengine/combat.py`
+   (`weapon_ammo`, `spend_ammo`, `reload`, `auto_orders`, jam/unjam) — expect
+   `test_raider_fight_rules[orders]` + CP4/CP8 item diffs to clear.
+3. Add promotion (LR-46) to the victory path in `combat.py`/`headless.py`.
+4. Emit the class-1 tail `cell_change` on PRINT cells (fixes
+   `test_save_labstate`, `test_load_restores_state`, M6 CP5..CP9).
+5. Re-run M5 then M6; then revisit the cactus bump.
+
+[harness] iter 82 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/dump199.txt, tests/fixtures-generated/dump200.txt, tests/fixtures-generated/dump201.txt, tests/fixtures-generated/dump202.txt, tests/fixtures-generated/dump203.txt, tests/fixtures-generated/dump204.txt, tests/fixtures-generated/dump205.txt, tests/fixtures-generated/dump206.txt
+
+[harness] iter 83 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: src/wlengine/combat.py, tests/fixtures-generated/dump209.txt, tests/fixtures-generated/dump210.txt, tests/fixtures-generated/dump211.txt, tests/fixtures-generated/dump212.txt, tests/fixtures-generated/dump213.txt, tests/fixtures-generated/dump214.txt, tests/fixtures-generated/probe210.py
+
+[harness] iter 84 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/dd/GAME1, tests/fixtures-generated/dd/LABSTATE.BIN, tests/fixtures-generated/dump216.txt, tests/fixtures-generated/dump217.txt, tests/fixtures-generated/dump218.txt, tests/fixtures-generated/dump219.txt, tests/fixtures-generated/dump220.txt, tests/fixtures-generated/dump221.txt
+
+[harness] iter 85 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/dump224.txt, tests/fixtures-generated/dump225.txt, tests/fixtures-generated/dump226.txt, tests/fixtures-generated/dump227.txt, tests/fixtures-generated/dump228.txt, tests/fixtures-generated/dump229.txt, tests/fixtures-generated/dump230.txt, tests/fixtures-generated/dump231.txt
+
+[harness] iter 86 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/dump232.txt, tests/fixtures-generated/dump233.txt, tests/fixtures-generated/dump234.txt, tests/fixtures-generated/dump235.txt, tests/fixtures-generated/dump236.txt, tests/fixtures-generated/dump237.txt, tests/fixtures-generated/dump238.txt, tests/fixtures-generated/dump239.txt
+
+[harness] iter 87 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/dump240.txt, tests/fixtures-generated/dump241.txt, tests/fixtures-generated/dump242.txt, tests/fixtures-generated/dump243.txt, tests/fixtures-generated/dump244.txt, tests/fixtures-generated/dump245.txt, tests/fixtures-generated/dump246.txt, tests/fixtures-generated/dump247.txt
+
+### iter 88 note (2026-10-24T16:34:36-05:00)
+## Iter 88 (M5 focus) — findings, no engine change yet
+
+### A. `test_bump_is_not_a_step` — the test's expectation is inconsistent with the frozen SPEC art
+Read the test verbatim (tests/test_m5_rules.py:513-519):
+```python
+ev, _ = runner.run("bump", {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
+subset("after 12 steps west and one bump (LR-15)", ckpt(ev, "a"),
+       {"location": 1, "x": 3, "y": 20, "steps": 12, "hour": 8, "minute": 12})
+tail = [...][-2:]
+check_eq("events of the bump into the cactus at (2, 20)", tail,
+         [{"type": "input", "key": "LEFT"},
+          {"type": "bump", "x": 2, "y": 20, "action_class": 11, "action": 0}])
+```
+Facts established this iteration (all verified by running code, not guessed):
+* Party starts at (15,20) in Saltwell (location 1), 08:00 day 1.
+* `SPEC/scenario/map1-saltwell.json` row 20: `tiles=[25,0,0,11,...]`,
+  `action_class=[11,0,0,11,...]` → the cactus (tile 11, class 11) is at **x=3**, not x=2.
+  Row 20 of the SPEC-05 art (line ~296) is `..Y...........;...............` with the
+  `Y` at x=2 — but the JSON/compiled data has the cactus at x=3. The JSON is the
+  frozen source of truth for the compiled map (M3/M4 pass against it).
+* Engine run of 13 LEFTs: 11 moves (x 15→4), then bump at (3,20) class 11, then a
+  second bump at (3,20). Checkpoint: x=4, steps=11, minute=11.
+* Oracle (`tests/oracle_tool.py compiled`) `expected.maps["1"].cells.actionClass[20]`
+  = `[11,0,0,11,...]` — i.e. the oracle agrees with the JSON: cactus at x=3.
+* So the test wants x=3/steps=12/bump at (2,20); the data says x=4/steps=11/bump at (3,20).
+  The test's numbers are only reachable if the cactus were at x=2. **This looks like a
+  frozen-test/frozen-data inconsistency, not an engine bug.** Do NOT "fix" the engine to
+  emit a bump at (2,20) — that would break M3/M4 map parity and the M6 reference log
+  (reference log has no bump at (2,20); its bumps are (8,17),(26,14)x4,(18,17),(25,21),
+  (16,6),(15,11)). Leave this test failing; it is 1 of the 3 M5 failures.
+
+### B. `test_save_labstate` — LABSTATE cell_changes[0][3] expected 0, got 5
+`ref_labstate` (tests/wl_support.py:492) reads 6-byte records
+`location, x, y, class, action byte, image` sorted by `(location, y, x)`.
+Test compares against the checkpoint's `cell_changes` sorted by `(c[0], c[2], c[1])`
+(i.e. location, y, x) — same order. Failure "cell_changes[0][3]: expected 0, got 5"
+means our first record has class 5 (a LOOT cell change) where the checkpoint state
+expects class 0. So the *checkpoint* `cell_changes` and the *file* disagree: the file
+contains a class-5 record (the raider loot cell (0,30,41) class 5) that the checkpoint
+state does not have, or the checkpoint has it as class 0. Likely our engine records the
+loot cell change twice (class 5 then class 0) and the checkpoint snapshot keeps only the
+last (class 0) while LABSTATE.BIN is written from a list that still holds the class-5
+entry, or vice versa. Next: dump `ckpt(ev,"CP5-pre-save")["cell_changes"]` and the
+LABSTATE.BIN bytes for the same run and diff them element by element.
+
+### C. `test_raider_fight_rules[orders]` — seed 3, round 2, slot 1: expected ['reload'], got ['unjam']
+Reference logic (tests/wl_combat_ref.py:202-220): for each slot, if dead→wait; elif
+`slot in jammed`→unjam; elif `loads[slot]>0`→fire; elif `boxes[slot]>0`→reload; else
+advance/unarmed. `jammed` is cleared only by an `unjammed` event. So our engine thinks
+slot 1 is still jammed in round 2 while the reference expects it to have been unjammed
+(and to need a reload). Two candidate causes: (1) we emit `unjammed` but the reference
+checker's `jammed` set is only cleared by an `unjammed` event — check whether we emit
+`unjammed` at all; (2) our jam/unjam ordering or the `loads` bookkeeping differs.
+Note the reference's `loads[s]=0` on jam and `loads[s]=cap` on reload; also `boxes[s]-=1`
+on reload. Next: run probe254 (already written, not yet run) which prints the full
+combat event stream for seed 3 plus `CR.consistency(ev)` issues, then compare against
+the reference's expected order sequence.
+
+### D. M6 CP4 `party[0].hp` expected 25 got 24
+Follows from combat damage/ammo semantics (B/C above): member 1 never takes the 3 damage
+the reference log records in round 4. Fixing C's ammo/jam/reload bookkeeping is the
+prerequisite.
+
+### E. M6 CP5..CP9 `cell_changes[1][0]` expected 0 got 1
+Same root cause as B: the cell-change list written to LABSTATE.BIN / carried in the
+checkpoint contains an extra or mis-classed entry (location 1 vs 0 ordering). Fix B first.
+
+### Files written this iteration
+probe250.py, probe251.py, probe252.py, probe253.py, probe254.py (probes only; no engine
+change). probe254.py is written but NOT yet run.
+
+### Next iteration plan (in order)
+1. Run `python3 tests/fixtures-generated/probe254.py` → full seed-3 combat stream +
+   `CR.consistency` issues. Fix `src/wlengine/combat.py` ammo/jam/reload/unjam
+   bookkeeping so `orders` matches (expect `test_raider_fight_rules[orders]` to clear,
+   and CP4 hp to follow).
+2. Dump checkpoint `cell_changes` vs LABSTATE.BIN bytes for the CP5-pre-save run
+   (probe255) and fix the cell-change recording/ordering in `headless.py`/`labstate.py`
+   (expect `test_save_labstate` + M6 CP5..CP9 to clear).
+3. Do NOT touch the cactus/bump behaviour: the frozen map JSON and the oracle both put
+   the cactus at x=3, so `test_bump_is_not_a_step` cannot pass without breaking M3/M4/M6.
+   Record this as a frozen-test inconsistency in the worklog and move on.
+4. Then re-run M5 and M6.
+
+[harness] iter 88 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: tests/fixtures-generated/probe250.py, tests/fixtures-generated/probe251.py, tests/fixtures-generated/probe252.py, tests/fixtures-generated/probe253.py, tests/fixtures-generated/probe254.py
+
+[harness] iter 89 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->79/82; M6 9->9/55; files changed: src/wlengine/combat.py, tests/fixtures-generated/probe255.py, tests/fixtures-generated/probe256.py, tests/fixtures-generated/probe257.py
+
+### iter 90 note (2026-10-24T17:48:41-05:00)
+## Iteration 90 (M5 focus) — big progress on combat; M5 79→80/82, M6 still 9/55
+
+### What I fixed in `src/wlengine/combat.py` (all verified by probes, not guessed)
+
+1. **Phase 2 actor selection (LR-35).** `phase2()` used to pick actors from
+   `c["fired"]` (slots that fired in phase 1). That is wrong: LR-35 says actors
+   are "the members with a phase 2 order". A member whose order was `fire` does
+   NOT act in phase 2 even if it jammed or ran dry during phase 1. Now
+   `combat_round()` stores `c["orders"] = orders` and `phase2()` skips any slot
+   whose order is `fire`/`wait`/`dead`/`flee`. This removed the spurious
+   `check`/`unjammed` events in rounds 2-4 of the seed-3 fight.
+
+2. **`party_phase1()` now honours the order.** Only members whose order is
+   `fire` fire in phase 1 (previously every ranged member fired, so a member
+   ordered to `reload`/`unjam` still fired). This was the cause of the
+   "round 3 slot 1 expected ['reload'], got ['advance', 1]" chain.
+
+3. **`member_phase2()` now dispatches on the order** instead of on the weapon
+   state: `reload` → `self.reload(m)` + `emit("reload", member=slot, status=cap)`;
+   `unjam` (or still jammed) → `unjam(slot)`; `fire` → `fire()`; `advance` →
+   `advance()`; otherwise melee/advance by band. Previously there was **no
+   `reload` event emitted at all** (the reference log has `reload` events at
+   seq 757/769/770 and in the seed-3 fight at round 3/5).
+
+4. **`unjam()` now sets the weapon status to 0 on success** (LR-39: "success
+   sets the status to 0 (empty, so a reload follows)"). Previously the status
+   kept its old load, so the member fired instead of reloading next round.
+
+5. **`ammo_boxes()` / `reload()` were completely broken.** They tested
+   `rec.get("ammo")` on the *ammunition* item record, but in `items.json` the
+   `ammo` field is the **weapon's** ammo item id (4 for the pistol, 6 for the
+   rifle) and is 0 for ammo items. An ammunition item is identified by
+   `type == 3` (class "ammo", `type_byte >> 3`). Now both functions select items
+   with `irec.get("type") == 3` and, when the weapon names an ammo id, require
+   `iid == rec["ammo"]`. `ammo_boxes` returns the box count (not `ammo * count`).
+   This is what made `reload` orders appear at all.
+
+6. **LR-46 promotion.** On promotion the engine now also raises `hp` by the
+   maxHP delta (unless dead), adds `2 * levels` to `skill_points`, and sets
+   `rank` to `RANKS[min(level,7)-1]`. Previously only `level`/`max_hp` changed,
+   so CP4 showed `rank: Drifter` instead of `Hand` and `skill_points: 0`.
+
+### Verified result
+`python3 tests/fixtures-generated/probe257.py` now shows the engine's raider
+fight (seed 20261021) is **byte-identical to the reference log**: 56 events,
+every line matches, including `jam` at round 2, `check`/`unjammed` at round 4,
+`reload` at round 5, and `combat_end rounds=5`.
+`probe254.py` (seed 3) reports **zero** `CR.consistency` issues.
+M5 went 79 → 80/82 (`test_raider_fight_rules[orders]` now passes).
+
+### Still failing
+* **M5 `test_bump_is_not_a_step`** — frozen-test/frozen-data inconsistency
+  (see iter 88 note): the frozen `SPEC/scenario/map1-saltwell.json` and the
+  oracle both put the cactus at x=3, the test wants x=2. Do NOT change the
+  engine; it would break M3/M4/M6.
+* **M5 `test_save_labstate`** — LABSTATE.BIN `cell_changes[0][3]` expected 0,
+  got 5. The checkpoint's `cell_changes` and the file disagree about the
+  class-5 loot cell (0,30,41). Next: dump `ckpt(ev,"CP5-pre-save")["cell_changes"]`
+  and the LABSTATE.BIN records for the same run and diff element by element
+  (probe255 already does this — run it).
+* **M6 CP4** now fails at `party[0].rank` (was `hp`), i.e. the promotion fix
+  landed but the checkpoint snapshot is taken before/without the rank update —
+  re-run M6 after the promotion patch (it was applied but not yet tested).
+* **M6 CP5..CP10 `cell_changes[1][0]` expected 0, got 1** — same root cause as
+  `test_save_labstate`: an extra/mis-ordered cell-change entry (location 1 vs 0).
+* **M6 `test_log_segment[CP5-pre-save]`** — the engine does not emit the
+  `cell_change` for (0,31,41) image 22 after the move to (31,41); the reference
+  log has it at seq 289. Look at how a move onto a class-0 cell with an image
+  emits `cell_change` in `headless.py`.
+
+### Next iteration plan (in order)
+1. Re-run M6 (the promotion patch was applied but never tested) — expect CP4 to
+   clear or move to the next field.
+2. Run `probe255.py`; diff checkpoint `cell_changes` vs LABSTATE.BIN records;
+   fix the cell-change recording/ordering in `headless.py`/`labstate.py`
+   (expect `test_save_labstate` + M6 CP5..CP10 to clear).
+3. Fix the missing `cell_change` on a plain move onto a class-0 cell with an
+   image (M6 `test_log_segment[CP5-pre-save]`).
+4. Leave `test_bump_is_not_a_step` failing (frozen inconsistency).
+
+[harness] iter 90 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 79->80/82; M6 9->11/55; files changed: src/wlengine/combat.py, tests/fixtures-generated/dump259eng.txt, tests/fixtures-generated/dump259ref.txt, tests/fixtures-generated/probe258.py, tests/fixtures-generated/probe259.py, tests/fixtures-generated/probe260.py, tests/fixtures-generated/probe261.py
+
+[harness] iter 91 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 80->81/82; M6 11->15/55; files changed: src/wlengine/headless.py, tests/fixtures-generated/probe262.py, tests/fixtures-generated/probe263.py, tests/fixtures-generated/probe264.py, tests/fixtures-generated/probe265.py, tests/fixtures-generated/probe266.py, tests/fixtures-generated/probe267.py, tests/fixtures-generated/probe268.py
+
+### iter 92 note (2026-10-24T18:19:12-05:00)
+## Iteration 92 (M5/M6 focus) — two real fixes landed; found the root cause of the CP8-CP10 cascade
+
+### Fixes applied this iteration (both verified against the reference log)
+
+1. **Snapshot `cell_changes` sort order (SPEC-06 2.4).** `Engine.sorted_cell_changes`
+   sorted by `(location, y, x)`; SPEC-06 line 343 says the snapshot list is
+   "sorted by location, x, y" (only LABSTATE.BIN, LR-57, sorts by
+   (location, y, x)). Changed the key to `(k[0], k[1], k[2])`.
+   → M6 went **15 → 36/55**; CP7/CP8/CP9/CP10 `cell_changes` now match the
+   reference exactly (the old order put (2,26,12) before (2,18,17)).
+
+2. **Loot status (LR-49).** `apply_loot` called `add_item(i+1, iid, 1)`, which
+   stored status **1** for every looted item. LR-49 says the status comes from
+   the loot amount. Added `Engine.add_item_status(member, iid, status)` (appends
+   a new slot with that status) and used it in `apply_loot`.
+   → CP6/CP7 `party[0].items[4]` is now `[11, 0]` (was `[11, 1]`) and CP8-CP10
+   `[9, 3]` / `[12, 0]` match the reference.
+
+### REGRESSION WARNING — M6 dropped 36 → 18/55 after fix 2
+The loot fix made CP6/CP7 checkpoints and log segments pass, but the total fell
+to 18/55. I did **not** get to diagnose it. Prime suspect: `add_item_status`
+appends a slot unconditionally, so if the same loot fires twice (e.g. the
+victory-loot path in `combat.victory()` *and* the tail path in `apply_tail`),
+the member gets two copies and the slot numbering shifts. Check with a probe
+that prints `party[i].items` at CP8/CP9 and counts `item_gain` events vs the
+reference (ref has exactly 3: seq 533 item 11, 791 item 9, 833 item 12).
+If duplicates appear, make `apply_loot` reuse an existing slot when the member
+already holds that item id (or guard the double fire).
+
+### ROOT CAUSE of the CP8-CP10 cascade: two different "band" variables
+`combat.py` keeps a **global** `c["band"]` (starts at 3, `advance()` decrements
+it) while `headless.end_of_round` keeps a **per-group** `g["band"]` and emits
+`group_closes`. The reference uses the *group's* band in the need formulas.
+Evidence from the seed-20261021 pump-crawler fight (probe274.py 740 800):
+* seq 748 `group_closes group 1 band 1` matches, so the group is in band 1.
+* seq 752-755: ref needs 65/56/54/68, engine 55/46/44/58 → engine is **10 low**
+  = `5 x (band-1)` with band 3 instead of 1.
+* seq 765-767: engine 5 low (band 2); seq 777: equal (band 1). The engine's
+  global band walks 3→2→1 while the reference stays at 1.
+* seq 758/771: ref orders member 6 `melee` and he attacks (need 52, no band
+  term); engine orders `advance` and emits `advance band 2/1` — same cause
+  (LR-33: melee when the group is in band 1).
+* seq 759-761/772: monster targets/damage differ because the RNG stream is
+  shifted by the extra `advance` draws; that is why `natural_heal` at CP9/CP10
+  says members [2,4] instead of [2,6] and why CP8 `party[1].hp` is 25 vs 26.
+**Next step: make the need formulas and the melee/advance decision use the
+ordered group's band (`g["band"]`), and make `advance()` lower that group's
+band (emitting `advance`), not a global one.** Then re-run probe274 740 800.
+
+### Other known failures (unchanged)
+* **CP9 `key_used`**: ref seq 809 `key_used member 1 item 11` then `unlock` at
+  (16,6); the engine instead rolls a skill check (skill 23) and never uses the
+  Gate card. The lock hook must consume the key item first (LR-21 / SPEC-03
+  9.6): emit `key_used`, remove/keep the item, `unlock`, then the two
+  `cell_change`s (image 39 then 37) and paragraph 21. This is why CP9 x is 18
+  instead of 21 (the engine bumps the gate and takes fewer RIGHTs).
+* **M5 `test_bump_is_not_a_step`**: frozen-test/frozen-data inconsistency
+  (cactus at x=3 in SPEC/scenario/map1-saltwell.json and the oracle, test wants
+  x=2). Do NOT change the engine.
+* **M5 `test_save_labstate`**: re-check after the sort fix — LABSTATE.BIN is
+  written from `labstate.encode_labstate`, which sorts by (location, y, x)
+  itself, so it should be unaffected; verify with probe255.py.
+
+### Probes written this iteration
+* `probe272.py` — diffs every checkpoint (cell_changes / party / scalars) and
+  every `cell_change` event against the reference log. Run it first.
+* `probe273.py` — dumps decoded records for the loot/lock cells.
+* `probe274.py lo hi` — side-by-side seq-window diff of engine vs reference.
+
+[harness] iter 92 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->80/82; M6 15->18/55; files changed: src/wlengine/headless.py, tests/fixtures-generated/probe272.py, tests/fixtures-generated/probe273.py, tests/fixtures-generated/probe274.py
+
+[harness] iter 93 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 80->81/82; M6 18->47/55; files changed: src/wlengine/combat.py, src/wlengine/headless.py, tests/fixtures-generated/probe275.py, tests/fixtures-generated/probe276.py, tests/fixtures-generated/probe277.py, tests/fixtures-generated/probe278.py, tests/fixtures-generated/probe279.py, tests/fixtures-generated/probe280.py
+
+### iter 94 note (2026-10-24T19:21:52-05:00)
+## Iteration 94 (M5 focus) — M5's last failure is a frozen inconsistency; M6 has 8 fixable failures
+
+### What I did
+Read the failing M5 test and probed the frozen data end to end (probe282-289.py).
+
+### Finding: `test_bump_is_not_a_step` cannot be satisfied by any map-consistent engine
+The test (tests/test_m5_rules.py:513) runs `["LEFT"]*13` from the Saltwell start
+(15,20) and expects:
+* checkpoint: `location 1, x 3, y 20, steps 12` (i.e. 12 *successful* steps west,
+  so cell (3,20) must be **passable**), and
+* tail: `bump x 2, y 20, action_class 11, action 0` (so cell (2,20) must be
+  **blocked with class 11**).
+
+The frozen data says the opposite, and every frozen source agrees with each other:
+* `SPEC/scenario/map1-saltwell.json`: `tiles[20] = [25,0,0,11,0,...]` → tile 11
+  (cactus) at **x=3**; `action_class[20][3] = 11`; `action_class[20][2] = 0`.
+* SPEC-05 section 5.2 ASCII art row 20 = `|..Y...........;...............|`
+  → `Y` (cactus) at column **3** (verified: all 32 art rows match the JSON tiles
+  exactly under the glyph map `|`=25 `.`=0 `;`=18 `Y`=11 `T`=10 `b`=9 `w`=26
+  `p`=24 `P`=23 `#`=16 `_`=17 `/`=19 `n`=21 `h`=22).
+* The oracle (`tests/oracle_tool.py compiled`) expected `cells.image[20]` =
+  `[35,10,10,21,...]` → image 21 = cactus at x=3, `actionClass[20][3]=11`.
+* The engine's compiled map (probe287) matches the oracle byte for byte, and M4
+  (76/76) asserts exactly that.
+
+So the test wants the cactus at (2,20) while all frozen data puts it at (3,20).
+No rule based on the map can produce a bump at (2,20): (2,20) is class 0 sand.
+The engine's current behaviour (11 steps to x=4, then bump at (3,20) class 11
+action 0) is the only map-consistent one. **Do not change the engine for this
+test** — it would break M4 and the M6 walkthrough log.
+
+(Curiosity worth remembering: reading the map *transposed* — `tiles[x][y]` —
+would give exactly the test's expectation: `tiles[3][20]=17` walkable,
+`tiles[2][20]=16` blocked, `actionClass[2][20]=11`. That is almost certainly how
+the test's expectation was authored, but transposing passability would break the
+whole walkthrough, so it is not a fix.)
+
+### Next step (highest value): M6, 47/55, 8 failures — all look fixable
+1. `wlengine.ui` does not exist → 4 failures (`test_render_frame_party`,
+   `test_render_status_line`, `test_render_viewport`, `test_cli_render_frame`).
+   Read tests/test_m6_playable.py:212-260 and SPEC-06 sections 2.1-2.4 + 7 for
+   the exact API (`render_frame`, `render_status_line`, `render_viewport`) and
+   write `src/wlengine/ui.py`.
+2. `test_repeat_limit` / `test_malformed_script`: `wlengine.headless.run` must
+   raise `RepeatLimitError` (SPEC-06 5.1 exit code 2) when a `repeat_until`
+   never becomes true, and `ScriptError` (exit code 4) for an unknown token like
+   `JUMP`. Both classes already exist in headless.py — they are just not raised.
+3. `test_cli_headless` / `test_cli_render_frame`: the `wl` CLI must exit 0 on the
+   walkthrough and on `--data DIR --render-frame` (SPEC-06 5.1, 7). Check how the
+   CLI entry point is invoked by the test (probably `python3 -m wlengine.cli` or
+   a `wl` script) and make sure it exists and returns the right codes.
+
+### Probes written this iteration
+probe282-289.py (map/art/oracle/engine comparisons, reference-log bump dump).
+
+[harness] iter 94 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe282.py, tests/fixtures-generated/probe283.py, tests/fixtures-generated/probe284.py, tests/fixtures-generated/probe285.py, tests/fixtures-generated/probe286.py, tests/fixtures-generated/probe287.py, tests/fixtures-generated/probe288.py, tests/fixtures-generated/probe289.py
+
+[harness] iter 95 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: src/wlengine/ui.py
+
+[harness] iter 96 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe290.py, tests/fixtures-generated/probe291.py, tests/fixtures-generated/probe292.py, tests/fixtures-generated/probe293.py
+
+[harness] iter 97 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe294.py, tests/fixtures-generated/probe295.py, tests/fixtures-generated/probe296.py, tests/fixtures-generated/probe297.py, tests/fixtures-generated/probe298.py, tests/fixtures-generated/probe299.py, tests/fixtures-generated/probe300.py, tests/fixtures-generated/probe301.py
+
+[harness] iter 98 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->47/55; files changed: tests/fixtures-generated/probe311.py, tests/fixtures-generated/probe312.py, tests/fixtures-generated/probe313.py, tests/fixtures-generated/probe314.py, tests/fixtures-generated/probe315.py, tests/fixtures-generated/probe316.py, tests/fixtures-generated/probe317.py
+
+[harness] iter 99 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 47->48/55; files changed: src/wlengine/__main__.py, src/wlengine/headless.py, src/wlengine/scenario.py
+
+[harness] iter 100 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 81->81/82; M6 48->48/55; files changed: tests/fixtures-generated/probe318.py, tests/fixtures-generated/probe319.py, tests/fixtures-generated/probe320.py, tests/fixtures-generated/probe320data/ALLHTDS1, tests/fixtures-generated/probe320data/ALLPICS1, tests/fixtures-generated/probe320data/COLORF.FNT, tests/fixtures-generated/probe320data/CURS, tests/fixtures-generated/probe320data/END.CPA
diff --git a/src/wlengine/__main__.py b/src/wlengine/__main__.py
new file mode 100644
index 0000000..508ae79
--- /dev/null
+++ b/src/wlengine/__main__.py
@@ -0,0 +1,112 @@
+"""Command line entry point (SPEC-06 sections 5 and 7).
+
+Usage:
+    wl --headless --data DIR --script FILE [--seed N] --log OUT.jsonl
+    wl --data DIR --render-frame
+
+Exit codes (SPEC-06 5.1): 0 the script ran to its end; 2 a `repeat_until`
+exceeded its `max`; 3 a data error; 4 a malformed script.
+"""
+
+from __future__ import annotations
+
+i
[truncated: showing 60000 of 1839183 chars]
```