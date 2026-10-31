# Review request, iteration 75

Run w1-2026-10-21; model deepseek-v41-flash-exl3; trigger: every 25 iterations.

Reply by writing `review-reply-75.md` in /Users/dtinholt/wasteland-build/runs/w1-2026-10-21. The run is not paused; a reply is injected into the next iteration that starts after it appears.

## Test summary

- M1: 89/89 passed, 0 failed, 0 errors [PASS]
- M2: 107/107 passed, 0 failed, 0 errors [PASS]
- M3: 94/94 passed, 0 failed, 0 errors [PASS]
- M4: 76/76 passed, 0 failed, 0 errors [PASS]
- M5: 79/82 passed, 3 failed, 0 errors [open]
- M6: 8/55 passed, 47 failed, 0 errors [open]

First 10 of 50 failing tests:
* [M5] tests.test_m5_rules::test_bump_is_not_a_step
    Failed: after 12 steps west and one bump (LR-15): first difference at x: expected 3, got 4
    after 12 steps west and one bump (LR-15): first difference at x: expected 3, got 4
* [M5] tests.test_m5_rules::test_raider_fight_rules[orders]
    Failed: seed 3, orders: round 2: slot 1 order expected ['reload'], got ['advance', 1]
    seed 3, orders: round 2: slot 1 order expected ['reload'], got ['advance', 1]
* [M5] tests.test_m5_rules::test_load_restores_state
    Failed: a fresh run that loads the save sees the saved state (LR-4, LR-56): first difference at cell_changes[0][0]: expected 1, got 0
    a fresh run that loads the save sees the saved state (LR-4, LR-56): first difference at cell_changes[0][0]: expected 1, got 0
* [M6] tests.test_m6_playable::test_checkpoint_matches_reference[CP4]
    Failed: checkpoint CP4, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][0]: expected 0, got 1
    checkpoint CP4, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][0]: expected 0, got 1
* [M6] tests.test_m6_playable::test_checkpoint_matches_reference[CP5-pre-save]
    Failed: checkpoint CP5-pre-save, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][0]: expected 0, got 1
    checkpoint CP5-pre-save, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][0]: expected 0, got 1
* [M6] tests.test_m6_playable::test_checkpoint_matches_reference[CP5]
    Failed: checkpoint CP5, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
    checkpoint CP5, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
* [M6] tests.test_m6_playable::test_checkpoint_matches_reference[CP6]
    Failed: checkpoint CP6, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
    checkpoint CP6, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
* [M6] tests.test_m6_playable::test_checkpoint_matches_reference[CP7]
    Failed: checkpoint CP7, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
    checkpoint CP7, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
* [M6] tests.test_m6_playable::test_checkpoint_matches_reference[CP8]
    Failed: checkpoint CP8, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
    checkpoint CP8, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
* [M6] tests.test_m6_playable::test_checkpoint_matches_reference[CP9]
    Failed: checkpoint CP9, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5
    checkpoint CP9, seed 20261021, full snapshot against the reference log: first difference at cell_changes[0][3]: expected 0, got 5

## Worklog tail

[earlier entries omitted]
  key 11): `bump → message(10) → key_used → unlock → cell_change(39) →
  cell_change(37) → paragraph(21)` (no xp).
- Our failure is "events after the successful check: [4].type expected
  'paragraph', got 'input'" → we emit an extra event (an `input` echo) or we
  emit `success_message` (string 8/11) where the reference emits nothing. Per
  LR-21 the success path ends with `success_message`; the reference log shows
  paragraph 12/21 as the *last* event, and the record's own message 7/10 is
  shown *before* the check. So `bump_lock` must NOT emit `success_message`
  (the hook's success_message 8/11 is never shown in the reference), and
  `bump_effect` for class 4 impassable must show the record message then run the
  hook (no `apply_tail` before the hook). Both changes are already written down
  in the iter-70 worklog; they are still not applied. Apply them first.

### C. test_load_restores_state (and 4 more save/load tests)
- `_saved()` runs the walkthrough prefix to CP5-pre-save then sends "S".
- Expected payload (from iter 68 worklog): order [1,2,3,4,5,0,0], x=25,y=5,
  map=2, prevX=43,prevY=28,prevMap=0, viewport [25,5], members [5,5], clock
  [28,17], serial 1, names Hessa..Orla, slots 6/7 zero.
- Failure "cell_changes[0][0] expected 1, got 0" means the loaded state's first
  cell change has location 0 instead of 1 → `load_game` restores LABSTATE.BIN
  cell changes with the wrong location, or does not restore them at all and the
  comparison is against a fresh run. `write_save_files`/`load_game` exist at
  headless.py lines 983-1052; `build_savegame_payload` at 1015 uses
  `containers.encode_savegame(sg, 0)`; `load_game` swallows all exceptions
  (must let FormatError propagate for `test_load_bad_labstate`).
- `key_o` (line 903) / `key_y` (line 907) handle the load prompt; the test sends
  "O" then "Y".

### D. test_raider_fight_rules[orders] (seed 3, round 2, slot 1 wants ['reload'])
- `auto_orders` returns `advance` when `member_weapon` is None / skill not in
  RANGED_SKILLS / `ammo_boxes(m) == 0`. Member 1 has Ranch pistol (id 3,
  status 6) + Pistol rounds (id 4). Suspect `loaded` is never initialised, or
  the ammo item's `ammo` field is 0, so `weapon_ammo` returns capacity and the
  member should `fire` not `reload` — but the test wants `reload`, so the
  opposite: our engine thinks there is ammo when there is none (or vice versa).
  Next: print `item_record(3)`, `RANGED_SKILLS`, `weapon_ammo(m)`,
  `ammo_boxes(m)` for slot 1 at round 2 of the seed-3 fight.

### E. test_healer (member 1 total 51 vs our -9)
- Reference seq 446 `money member 1 delta -104 total 91`, seq 606 `money member 1
  delta -40 total 51`. Our member 1 has 31 before the healer (60 too little).
  Likely the same `skill_level`/money divergence as the victory loot (Salvage
  must be 0 when the member lacks skill 26) plus a shop payment difference.
  Next: dump member-1 money at CP1..CP7 and compare with reference money events
  (seq 59, 66, 74, 80, 390, 446, 606).

### F. test_victory_loot (already diagnosed in iter 70)
- `skill_level` must return 0 for a skill the member lacks (it does, line 848:
  returns 0). But `best_salvage()` returned 1 in iter 70 → check
  `combat.best_salvage` / `SALVAGE` constant and whether `party` members carry a
  bogus skill 26 entry. Also `victory()` must apply the encounter record's tail
  then fire the loot at once (already coded at combat.py 439-480) — verify the
  ordering matches reference seq 272-284.

### Files written this iteration (probes only, no engine change)
- tests/fixtures-generated/probe124.py … probe133.py and dump124..dump133.txt
  (code dumps, hooks JSON, map JSON rows, ASCII art, conftest/wl_support).

### Next iteration plan (in order)
1. Fix `move()`/`try_move()` so a class-11 cell is bumped, never entered
   (test_bump_is_not_a_step). Verify with a probe that prints move events.
2. Apply the two lock fixes: `bump_effect` class-4-impassable shows the record
   message then runs the hook (no pre-hook `apply_tail`); `bump_lock` drops
   `success_message` (test_storehouse_lock x3, test_key_lock).
3. Re-run M5; then raider orders (D), healer money (E).
4. Then the 5 save/load tests (C), then M6.

[harness] iter 71 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 75->75/82; M6 8->8/55; files changed: tests/fixtures-generated/dump124.txt, tests/fixtures-generated/dump125.txt, tests/fixtures-generated/dump126.txt, tests/fixtures-generated/dump127.txt, tests/fixtures-generated/dump128.txt, tests/fixtures-generated/dump129.txt, tests/fixtures-generated/dump130.txt, tests/fixtures-generated/dump131.txt

[harness] iter 72 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 75->75/82; M6 8->8/55; files changed: tests/fixtures-generated/dump135.txt, tests/fixtures-generated/dump136.txt, tests/fixtures-generated/dump137.txt, tests/fixtures-generated/probe134.py, tests/fixtures-generated/probe135.py, tests/fixtures-generated/probe136.py, tests/fixtures-generated/probe137.py

[harness] iter 73 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 75->75/82; M6 8->8/55; files changed: tests/fixtures-generated/probe138.py

[harness] iter 74 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 75->75/82; M6 8->8/55; files changed: tests/fixtures-generated/probe139.py, tests/fixtures-generated/probe140.py, tests/fixtures-generated/probe141.py

[harness] iter 75 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 75->79/82; M6 8->8/55; files changed: src/wlengine/headless.py, tests/fixtures-generated/dump143.txt, tests/fixtures-generated/dump144.txt, tests/fixtures-generated/probe142.py, tests/fixtures-generated/probe143.py, tests/fixtures-generated/probe144.py, tests/fixtures-generated/probe145.py, tests/fixtures-generated/probe146.py


## Diff since last review (0a2c90b8ec..d20b6a476a)

```diff
 WORKLOG.md                                     | 1932 +++++++++
 src/wlengine/combat.py                         |  498 +++
 src/wlengine/headless.py                       | 1193 ++++++
 src/wlengine/scenario.py                       |  264 +-
 tests/fixtures-generated/analyze.py            |  114 +
 tests/fixtures-generated/cmp.py                |   94 +
 tests/fixtures-generated/cmpmap.py             |   30 +
 tests/fixtures-generated/dd/ALLHTDS1           |  Bin 0 -> 807 bytes
 tests/fixtures-generated/dd/ALLPICS1           |  Bin 0 -> 2204 bytes
 tests/fixtures-generated/dd/COLORF.FNT         |  Bin 0 -> 1024 bytes
 tests/fixtures-generated/dd/CURS               |  Bin 0 -> 512 bytes
 tests/fixtures-generated/dd/END.CPA            |  Bin 0 -> 3050 bytes
 tests/fixtures-generated/dd/GAME1              |  Bin 0 -> 22722 bytes
 tests/fixtures-generated/dd/IC0_9.WLF          |  Bin 0 -> 1280 bytes
 tests/fixtures-generated/dd/LABHOOKS.JSON      |  150 +
 tests/fixtures-generated/dd/LABSKILL.BIN       |  Bin 0 -> 72 bytes
 tests/fixtures-generated/dd/LABSTR.BIN         |  Bin 0 -> 1938 bytes
 tests/fixtures-generated/dd/LABTABLES.BIN      |  Bin 0 -> 1080 bytes
 tests/fixtures-generated/dd/MASKS.WLF          |    1 +
 tests/fixtures-generated/dd/PARAGRAPHS.JSON    |  125 +
 tests/fixtures-generated/dd/TITLE.PIC          |  Bin 0 -> 18432 bytes
 tests/fixtures-generated/dd117/ALLHTDS1        |  Bin 0 -> 807 bytes
 tests/fixtures-generated/dd117/ALLPICS1        |  Bin 0 -> 2204 bytes
 tests/fixtures-generated/dd117/COLORF.FNT      |  Bin 0 -> 1024 bytes
 tests/fixtures-generated/dd117/CURS            |  Bin 0 -> 512 bytes
 tests/fixtures-generated/dd117/END.CPA         |  Bin 0 -> 3050 bytes
 tests/fixtures-generated/dd117/GAME1           |  Bin 0 -> 22722 bytes
 tests/fixtures-generated/dd117/IC0_9.WLF       |  Bin 0 -> 1280 bytes
 tests/fixtures-generated/dd117/LABHOOKS.JSON   |  150 +
 tests/fixtures-generated/dd117/LABSKILL.BIN    |  Bin 0 -> 72 bytes
 tests/fixtures-generated/dd117/LABSTATE.BIN    |  Bin 0 -> 30 bytes
 tests/fixtures-generated/dd117/LABSTR.BIN      |  Bin 0 -> 1938 bytes
 tests/fixtures-generated/dd117/LABTABLES.BIN   |  Bin 0 -> 1080 bytes
 tests/fixtures-generated/dd117/MASKS.WLF       |    1 +
 tests/fixtures-generated/dd117/PARAGRAPHS.JSON |  125 +
 tests/fixtures-generated/dd117/TITLE.PIC       |  Bin 0 -> 18432 bytes
 tests/fixtures-generated/dd2/ALLHTDS1          |  Bin 0 -> 807 bytes
 tests/fixtures-generated/dd2/ALLPICS1          |  Bin 0 -> 2204 bytes
 tests/fixtures-generated/dd2/COLORF.FNT        |  Bin 0 -> 1024 bytes
 tests/fixtures-generated/dd2/CURS              |  Bin 0 -> 512 bytes
 tests/fixtures-generated/dd2/END.CPA           |  Bin 0 -> 3050 bytes
 tests/fixtures-generated/dd2/GAME1             |  Bin 0 -> 22722 bytes
 tests/fixtures-generated/dd2/IC0_9.WLF         |  Bin 0 -> 1280 bytes
 tests/fixtures-generated/dd2/LABHOOKS.JSON     |  150 +
 tests/fixtures-generated/dd2/LABSKILL.BIN      |  Bin 0 -> 72 bytes
 tests/fixtures-generated/dd2/LABSTR.BIN        |  Bin 0 -> 1938 bytes
 tests/fixtures-generated/dd2/LABTABLES.BIN     |  Bin 0 -> 1080 bytes
 tests/fixtures-generated/dd2/MASKS.WLF         |    1 +
 tests/fixtures-generated/dd2/PARAGRAPHS.JSON   |  125 +
 tests/fixtures-generated/dd2/TITLE.PIC         |  Bin 0 -> 18432 bytes
 tests/fixtures-generated/dd3/ALLHTDS1          |  Bin 0 -> 807 bytes
 tests/fixtures-generated/dd3/ALLPICS1          |  Bin 0 -> 2204 bytes
 tests/fixtures-generated/dd3/COLORF.FNT        |  Bin 0 -> 1024 bytes
 tests/fixtures-generated/dd3/CURS              |  Bin 0 -> 512 bytes
 tests/fixtures-generated/dd3/END.CPA           |  Bin 0 -> 3050 bytes
 tests/fixtures-generated/dd3/GAME1             |  Bin 0 -> 22722 bytes
 tests/fixtures-generated/dd3/IC0_9.WLF         |  Bin 0 -> 1280 bytes
 tests/fixtures-generated/dd3/LABHOOKS.JSON     |  150 +
 tests/fixtures-generated/dd3/LABSKILL.BIN      |  Bin 0 -> 72 bytes
 tests/fixtures-generated/dd3/LABSTR.BIN        |  Bin 0 -> 1938 bytes
 tests/fixtures-generated/dd3/LABTABLES.BIN     |  Bin 0 -> 1080 bytes
 tests/fixtures-generated/dd3/MASKS.WLF         |    1 +
 tests/fixtures-generated/dd3/PARAGRAPHS.JSON   |  125 +
 tests/fixtures-generated/dd3/TITLE.PIC         |  Bin 0 -> 18432 bytes
 tests/fixtures-generated/dd9/ALLHTDS1          |  Bin 0 -> 807 bytes
 tests/fixtures-generated/dd9/ALLPICS1          |  Bin 0 -> 2204 bytes
 tests/fixtures-generated/dd9/COLORF.FNT        |  Bin 0 -> 1024 bytes
 tests/fixtures-generated/dd9/CURS              |  Bin 0 -> 512 bytes
 tests/fixtures-generated/dd9/END.CPA           |  Bin 0 -> 3050 bytes
 tests/fixtures-generated/dd9/GAME1             |  Bin 0 -> 22722 bytes
 tests/fixtures-generated/dd9/IC0_9.WLF         |  Bin 0 -> 1280 bytes
 tests/fixtures-generated/dd9/LABHOOKS.JSON     |  150 +
 tests/fixtures-generated/dd9/LABSKILL.BIN      |  Bin 0 -> 72 bytes
 tests/fixtures-generated/dd9/LABSTR.BIN        |  Bin 0 -> 1938 bytes
 tests/fixtures-generated/dd9/LABTABLES.BIN     |  Bin 0 -> 1080 bytes
 tests/fixtures-generated/dd9/MASKS.WLF         |    1 +
 tests/fixtures-generated/dd9/PARAGRAPHS.JSON   |  125 +
 tests/fixtures-generated/dd9/TITLE.PIC         |  Bin 0 -> 18432 bytes
 tests/fixtures-generated/difftool.py           |  120 +
 tests/fixtures-generated/dump103.txt           | 5277 ++++++++++++++++++++++++
 tests/fixtures-generated/dump104.txt           | 1522 +++++++
 tests/fixtures-generated/dump105.txt           | 2746 ++++++++++++
 tests/fixtures-generated/dump106.txt           |   24 +
 tests/fixtures-generated/dump107.txt           |   63 +
 tests/fixtures-generated/dump110.txt           | 1464 +++++++
 tests/fixtures-generated/dump111.txt           | 2440 +++++++++++
 tests/fixtures-generated/dump112.txt           | 2444 +++++++++++
 tests/fixtures-generated/dump117.txt           |  252 ++
 tests/fixtures-generated/dump124.txt           | 1195 ++++++
 tests/fixtures-generated/dump125.txt           |  183 +
 tests/fixtures-generated/dump126.txt           |  294 ++
 tests/fixtures-generated/dump127.txt           |  667 +++
 tests/fixtures-generated/dump128.txt           |  214 +
 tests/fixtures-generated/dump129.txt           |  114 +
 tests/fixtures-generated/dump130.txt           |   13 +
 tests/fixtures-generated/dump131.txt           |  144 +
 tests/fixtures-generated/dump132.txt           |  771 ++++
 tests/fixtures-generated/dump135.txt           |  524 +++
 tests/fixtures-generated/dump136.txt           | 1355 ++++++
 tests/fixtures-generated/dump137.txt           |   46 +
 tests/fixtures-generated/dump143.txt           | 1314 ++++++
 tests/fixtures-generated/dump144.txt           |  144 +
 tests/fixtures-generated/dump70.txt            | 3672 +++++++++++++++++
 tests/fixtures-generated/dump71.txt            |  590 +++
 tests/fixtures-generated/dump72.txt            |  546 +++
 tests/fixtures-generated/dump73.txt            | 1372 ++++++
 tests/fixtures-generated/dump74.txt            |  341 ++
 tests/fixtures-generated/dump78.txt            | 1626 ++++++++
 tests/fixtures-generated/dump79.txt            |  978 +++++
 tests/fixtures-generated/dump80.txt            |   55 +
 tests/fixtures-generated/dump81.txt            |  838 ++++
 tests/fixtures-generated/dump86.txt            | 3146 ++++++++++++++
 tests/fixtures-generated/dump87.txt            | 1450 +++++++
 tests/fixtures-generated/dump88.txt            | 1752 ++++++++
 tests/fixtures-generated/dump89.txt            | 4243 +++++++++++++++++++
 tests/fixtures-generated/dump94.txt            | 2566 ++++++++++++
 tests/fixtures-generated/dump95.txt            |   32 +
 tests/fixtures-generated/dump96.txt            |   20 +
 tests/fixtures-generated/dumpcells.py          |   10 +
 tests/fixtures-generated/dumpmap1.py           |    7 +
 tests/fixtures-generated/dumpref.py            |    8 +
 tests/fixtures-generated/dumpspec.py           |    8 +
 tests/fixtures-generated/probe.py              |   54 +
 tests/fixtures-generated/probe10.py            |   44 +
 tests/fixtures-generated/probe100.py           |   17 +
 tests/fixtures-generated/probe101.py           |   10 +
 tests/fixtures-generated/probe102.py           |   42 +
 tests/fixtures-generated/probe103.py           |   43 +
 tests/fixtures-generated/probe104.py           |   74 +
 tests/fixtures-generated/probe105.py           |   71 +
 tests/fixtures-generated/probe106.py           |   53 +
 tests/fixtures-generated/probe107.py           |   95 +
 tests/fixtures-generated/probe108.py           |   67 +
 tests/fixtures-generated/probe109.py           |   28 +
 tests/fixtures-generated/probe11.py            |   70 +
 tests/fixtures-generated/probe110.py           |   99 +
 tests/fixtures-generated/probe111.py           |   11 +
 tests/fixtures-generated/probe112.py           |   30 +
 tests/fixtures-generated/probe113.py           |   38 +
 tests/fixtures-generated/probe114.py           |   28 +
 tests/fixtures-generated/probe115.py           |   33 +
 tests/fixtures-generated/probe116.py           |   14 +
 tests/fixtures-generated/probe117.py           |   69 +
 tests/fixtures-generated/probe118.py           |   63 +
 tests/fixtures-generated/probe119.py           |   72 +
 tests/fixtures-generated/probe12.py            |   96 +
 tests/fixtures-generated/probe120.py           |   32 +
 tests/fixtures-generated/probe121.py           |   37 +
 tests/fixtures-generated/probe122.py           |   41 +
 tests/fixtures-generated/probe123.py           |   47 +
 tests/fixtures-generated/probe124.py           |   73 +
 tests/fixtures-generated/probe125.py           |   67 +
 tests/fixtures-generated/probe126.py           |   47 +
 tests/fixtures-generated/probe127.py           |   38 +
 tests/fixtures-generated/probe128.py           |   51 +
 tests/fixtures-generated/probe129.py           |   42 +
 tests/fixtures-generated/probe13.py            |   48 +
 tests/fixtures-generated/probe130.py           |   43 +
 tests/fixtures-generated/probe131.py           |   46 +
 tests/fixtures-generated/probe132.py           |   27 +
 tests/fixtures-generated/probe133.py           |   44 +
 tests/fixtures-generated/probe134.py           |   59 +
 tests/fixtures-generated/probe135.py           |   60 +
 tests/fixtures-generated/probe136.py           |   89 +
 tests/fixtures-generated/probe137.py           |   66 +
 tests/fixtures-generated/probe138.py           |   64 +
 tests/fixtures-generated/probe139.py           |   51 +
 tests/fixtures-generated/probe14.py            |   50 +
 tests/fixtures-generated/probe140.py           |   84 +
 tests/fixtures-generated/probe141.py           |   56 +
 tests/fixtures-generated/probe142.py           |   50 +
 tests/fixtures-generated/probe143.py           |   83 +
 tests/fixtures-generated/probe144.py           |   58 +
 tests/fixtures-generated/probe145.py           |   28 +
 tests/fixtures-generated/probe146.py           |   26 +
 tests/fixtures-generated/probe147.py           |   27 +
 tests/fixtures-generated/probe148.py           |   26 +
 tests/fixtures-generated/probe15.py            |   61 +
 tests/fixtures-generated/probe16.py            |   41 +
 tests/fixtures-generated/probe17.py            |   61 +
 tests/fixtures-generated/probe18.py            |   45 +
 tests/fixtures-generated/probe19.py            |   67 +
 tests/fixtures-generated/probe2.py             |   60 +
 tests/fixtures-generated/probe20.py            |   53 +
 tests/fixtures-generated/probe21.py            |   44 +
 tests/fixtures-generated/probe22.py            |   61 +
 tests/fixtures-generated/probe23.py            |   33 +
 tests/fixtures-generated/probe24.py            |   36 +
 tests/fixtures-generated/probe25.py            |   44 +
 tests/fixtures-generated/probe26.py            |   79 +
 tests/fixtures-generated/probe27.py            |   27 +
 tests/fixtures-generated/probe28.py            |   30 +
 tests/fixtures-generated/probe29.py            |   57 +
 tests/fixtures-generated/probe3.py             |   69 +
 tests/fixtures-generated/probe30.py            |   55 +
 tests/fixtures-generated/probe31.py            |   50 +
 tests/fixtures-generated/probe32.py            |   31 +
 tests/fixtures-generated/probe33.py            |   41 +
 tests/fixtures-generated/probe34.py            |   81 +
 tests/fixtures-generated/probe35.py            |   67 +
 tests/fixtures-generated/probe36.py            |   88 +
 tests/fixtures-generated/probe37.py            |   63 +
 tests/fixtures-generated/probe38.py            |   43 +
 tests/fixtures-generated/probe39.py            |   47 +
 tests/fixtures-generated/probe4.py             |   43 +
 tests/fixtures-generated/probe40.py            |   48 +
 tests/fixtures-generated/probe41.py            |   46 +
 tests/fixtures-generated/probe42.py            |   49 +
 tests/fixtures-generated/probe43.py            |   92 +
 tests/fixtures-generated/probe44.py            |   48 +
 tests/fixtures-generated/probe45.py            |   81 +
 tests/fixtures-generated/probe46.py            |   42 +
 tests/fixtures-generated/probe47.py            |   43 +
 tests/fixtures-generated/probe48.py            |   35 +
 tests/fixtures-generated/probe49.py            |   45 +
 tests/fixtures-generated/probe5.py             |   38 +
 tests/fixtures-generated/probe50.py            |   71 +
 tests/fixtures-generated/probe51.py            |   39 +
 tests/fixtures-generated/probe52.py            |   75 +
 tests/fixtures-generated/probe53.py            |   41 +
 tests/fixtures-generated/probe54.py            |   23 +
 tests/fixtures-generated/probe55.py            |   40 +
 tests/fixtures-generated/probe56.py            |   39 +
 tests/fixtures-generated/probe57.py            |   50 +
 tests/fixtures-generated/probe58.py            |   42 +
 tests/fixtures-generated/probe59.py            |   21 +
 tests/fixtures-generated/probe6.py             |   40 +
 tests/fixtures-generated/probe60.py            |   21 +
 tests/fixtures-generated/probe61.py            |   77 +
 tests/fixtures-generated/probe62.py            |   39 +
 tests/fixtures-generated/probe63.py            |   38 +
 tests/fixtures-generated/probe64.py            |   64 +
 tests/fixtures-generated/probe65.py            |   29 +
 tests/fixtures-generated/probe66.py            |   42 +
 tests/fixtures-generated/probe67.py            |   48 +
 tests/fixtures-generated/probe68.py            |   32 +
 tests/fixtures-generated/probe69.py            |   64 +
 tests/fixtures-generated/probe7.py             |   29 +
 tests/fixtures-generated/probe70.py            |   66 +
 tests/fixtures-generated/probe71.py            |   44 +
 tests/fixtures-generated/probe72.py            |   31 +
 tests/fixtures-generated/probe73.py            |   40 +
 tests/fixtures-generated/probe74.py            |   27 +
 tests/fixtures-generated/probe75.py            |   29 +
 tests/fixtures-generated/probe76.py            |   42 +
 tests/fixtures-generated/probe77.py            |   42 +
 tests/fixtures-generated/probe78.py            |   61 +
 tests/fixtures-generated/probe79.py            |   35 +
 tests/fixtures-generated/probe8.py             |   33 +
 tests/fixtures-generated/probe80.py            |   22 +
 tests/fixtures-generated/probe81.py            |   25 +
 tests/fixtures-generated/probe82.py            |   26 +
 tests/fixtures-generated/probe83.py            |   15 +
 tests/fixtures-generated/probe84.py            |   25 +
 tests/fixtures-generated/probe85.py            |   63 +
 tests/fixtures-generated/probe86.py            |   59 +
 tests/fixtures-generated/probe87.py            |   43 +
 tests/fixtures-generated/probe88.py            |   40 +
 tests/fixtures-generated/probe89.py            |   59 +
 tests/fixtures-generated/probe9.py             |   38 +
 tests/fixtures-generated/probe90.py            |   43 +
 tests/fixtures-generated/probe91.py            |   31 +
 tests/fixtures-generated/probe92.py            |   49 +
 tests/fixtures-generated/probe93.py            |   34 +
 tests/fixtures-generated/probe94.py            |   91 +
 tests/fixtures-generated/probe95.py            |   40 +
 tests/fixtures-generated/probe96.py            |   49 +
 tests/fixtures-generated/probe97.py            |   60 +
 tests/fixtures-generated/probe98.py            |   96 +
 tests/fixtures-generated/probe99.py            |   57 +
 tests/fixtures-generated/refcheck.py           |   74 +
 tests/fixtures-generated/refdiff.py            |  120 +
 tests/fixtures-generated/refdump.txt           | 1022 +++++
 tests/fixtures-generated/show.py               |    7 +
 274 files changed, 60521 insertions(+), 1 deletion(-)

diff --git a/WORKLOG.md b/WORKLOG.md
index cbd469d..af7be5a 100644
--- a/WORKLOG.md
+++ b/WORKLOG.md
@@ -1594,3 +1594,1935 @@ Then `src/wlengine/ui.py` (`render_frame`) and `src/wlengine/__main__.py` for M6
 Diff every step against `tests/fixtures-generated/reflog4.txt` (line N = event N, `seq` stripped).
 
 [harness] iter 25 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 38->38/82; M6 0->0/55; no file changes
+
+### iter 26 note (2026-10-22T07:15:32-05:00)
+## Iter 26 (M5 focus): read-only reconnaissance, no code written yet
+
+`src/wlengine/headless.py` still does not exist -> all 44 failing M5 tests + all 55 M6 tests
+fail on `ModuleNotFoundError: No module named 'wlengine.headless'`. M1-M4 remain green.
+This iteration was spent reading SPEC-04/06, the walkthrough, the reference log and the
+existing engine modules to pin down the exact contract. Nothing was written, so no
+regression risk, but no progress either. Next iteration MUST start writing code.
+
+### Contract (confirmed from tests/conftest.py Runner + tests/wl_support.py)
+- `headless.run(str(data_dir), script_dict, seed=None) -> list[dict]`; `seed` overrides
+  `script["seed"]`. Must RAISE (not return) `ScriptError`/`RepeatLimitError`/`FormatError`.
+- `script = {"seed": N, "start": "new"|"create", "script": [token|macro,...]}`.
+- token = `UP|DOWN|LEFT|RIGHT|ESC|ENTER` or one printable char (case-sensitive).
+- macros: `{"repeat_until": COND, "keys":[...], "max":N}` (COND `mode:NAME` or `cell:L,X,Y`;
+  exceeded max -> `RepeatLimitError`), `{"checkpoint": NAME}` (no input consumed).
+- Every token logged as `{"type":"input","key":K}` BEFORE its effects; every event gets `seq`.
+- `run` writes GAME1's savegame block in place at `tables["savegameOffsets"][0]` (0x1206 bytes
+  reserved) and `LABSTATE.BIN` next to it. A later `run(..., data_dir=dd)` with `["O","Y"]`
+  must restore state. `test_load_bad_labstate` flips the last byte of LABSTATE.BIN and expects
+  `FormatError` from the load (decode_labstate already raises it).
+
+### Exact event shapes (from SPEC/scenario/walkthrough-reference-log.json, 1022 events)
+- `new_game{seed}` then `paragraph{n:1}`; mode `map`. Start: location 1 (Saltwell), (15,20),
+  day 1, hour 8, minute 0, steps 0, rng_state = seed.
+- move: `move{location,x,y,steps}`; bump: `bump{x,y,action_class,action}` (no step/time);
+  transition: `map_change{location,x,y}` (arriving is NOT a step).
+- Clock: Saltwell 1 min/step (`time_per_step` 256 -> high byte 1 min, low 0 s), overworld
+  10 min/step. Crossing a full hour -> `natural_heal{members:[...]}` (omitted when nobody is
+  below maxHP) and `day{day}` at hour 0.
+- `R` -> `rest` only (no other events when nobody hurt and no Foraging).
+- Shop: `shop_open{shop}` on stepping onto a class 6 cell (after the record `message`);
+  `B` -> `prompt{buy_item,items:[ids with stock 1..255 in id order]}`; item letter ->
+  `prompt{member}`; digit -> `money{member,delta:-price,total}` then
+  `buy{member,item,price,slot,status}`; `S` -> `prompt{member}` -> digit ->
+  `prompt{item_slot}` -> letter -> `sell{member,item,price,slot}` then `money`;
+  `X` -> `shop_close`. Ammo stacks onto the existing box in the same slot (status += 1).
+- `C` -> `prompt{member}` -> digit -> `char_open{member}`; `E` -> `prompt{item_slot}` ->
+  letter -> `equip{member,slot,item,ac}`; `X` -> `char_close`.
+  AC = `rules.armour_class(AGL, armour damage byte, Evasion level)`.
+- Recruit: bump class 11 -> `bump` -> `paragraph` (refuse/join text) -> `prompt{recruit}` ->
+  `Y` -> `cell_change{location,x,y,action_class:0,action:0,image:cleared_image}` then
+  `recruit{location,npc,slot}`.
+- Lock (LR-21): bump -> `message` (fail msg) -> `check{member,skill,level,need,roll,success}`;
+  on success `unlock{x,y}`, `cell_change` (tail, image unchanged), `cell_change` (record tile),
+  `xp{member,delta:10,total}`, `paragraph`. Key path: `message` -> `key_used{member,item}` ->
+  `unlock` -> two `cell_change` -> `paragraph`.
+- Healer: bump -> `prompt{heal,price}` -> `Y` -> `money{member:1,delta:-price,total}` ->
+  `heal_all{price}`.
+- Win: bump -> `paragraph{not_yet}` without the item; with it `paragraph{win_paragraph}` then
+  `win{steps,day,minutes}` (minutes = time of day).
+- Combat (LR-26..44): `encounter_start{groups:[{monster,count,band,hp}]}` -> record
+  `paragraph` -> `check{member,skill:18,...}` -> `surprised{}` on failure -> `round_start{round:0}`
+  -> monster phase 1 -> `group_closes{group,band}`. Then `A` -> `round_orders{round:N,orders:{"1":["fire",1],...}}`
+  -> `round_start{round:N}` -> party phase 1 in slot order (`attack`/`click`/`jam`/`reload`/`unjam`/
+  `monster_dies`) -> monster phase 1 -> phase 2 speed order -> `group_closes`. Victory:
+  `combat_end{result:victory,rounds:N}`, then per member in slot order `xp{member,delta,total}` +
+  `promote{member,level,max_hp,rank}` on a level rise, then the record tail `cell_change` (class 5),
+  loot `money{member:1,delta:75,total:195}`, then `cell_change` back to class 0.
+  Auto orders (LR-33): wait / unjam / fire lowest living group / reload / melee-or-advance.
+- Save: `S` -> `save{serial:1}`; `O` -> `prompt{load}` -> `Y` -> `load{serial:1}`.
+- Checkpoint snapshot keys: location,x,y,steps,day,hour,minute,mode,cell_changes (sorted by
+  location,x,y), party[{slot,name,npc,level,xp,max_hp,hp,cond,money,ac,rank,skill_points,
+  items[[id,status]],weapon_slot,armour_slot}], rng_state. `cell_changes` entries are
+  `[location,x,y,class,action,image]`.
+
+### Useful existing API (all already implemented and green)
+- `containers.read_tables(path)`, `resolve_location(tables, loc)`, `decode_savegame(game, off)`,
+  `encode_savegame(sg, disk)`, `decode_shop_list(game, off)`, `decode_character/encode_character`.
+- `maps.load_map(data_dir, location)`, `record_at(map,x,y)`, `is_passable(map,x,y)`,
+  `apply_tail(rec)`, `resolve_transition(tables,rec,x,y,prev)`, `image_at(map,x,y)`.
+  Map dict: `size`, `info` (timePerStep, healRate, borderImage, ...), `cells.{actionClass,action,image}`,
+  `actions[str(cls)]` (list, index 0 = null), `npcs`, `mobs`, `strings`.
+- `rules.Rng`, `skill_check`, `check_need`, `pick_checker`, `advance_clock`, `xp_threshold`,
+  `level_after`, `buy_price`, `sell_price`, `pay`, `monster_values`, `monster_hp`, `monster_damage`,
+  `build_groups`, `ranged_need`, `melee_need`, `monster_need`, `flee_need`, `jam_chance`,
+  `unarmed_attacks`, `melee_damage_bonus`, `damage_member`, `speed_order`, `max_hp`, `armour_class`.
+- `labstate.encode_labstate(state)` / `decode_labstate(data)` (raises FormatError on bad sum).
+- `strings.read_labstr(path)` -> list of tables; LABSTR table 1 = UI strings, table 2 = skill/item
+  names, table 3 = ranks. `scenario.compile(scenario_dir, out_dir)` writes the whole data set.
+- Data dir files: GAME1, GAME2, LABTABLES.BIN, LABSTR.BIN, LABSKILL.BIN, LABHOOKS.JSON,
+  PARAGRAPHS.JSON, ALLHTDS1, ALLPICS1, IC0_9.WLF, MASKS.WLF, COLORF.FNT, CURS, TITLE.PIC, END.CPA.
+- `SPEC/scenario/hooks.json` = LABHOOKS.JSON source; `paragraphs.json`; `npcs.json` (recruit index);
+  `encounters.json` (derived index); `items.json` (id N = shop record N-1); `shops.json`;
+  `party.json` (premade party, already compiled into GAME1's savegame).
+- `tests/wl_combat_ref.py` is the independent oracle for the raider fight (opening() + consistency()).
+
+### Concrete next step (unchanged, now with exact shapes above)
+Write `src/wlengine/headless.py` in this order, running `run_tests M5` after each chunk:
+1. `Engine.__init__(data_dir)`: `containers.read_tables`, `maps.load_map` per location,
+   `rules.read_skill_table`, `LABHOOKS.JSON`, `PARAGRAPHS.JSON`, `LABSTR.BIN`, shop lists from
+   GAME1, savegame from GAME1 at `savegameOffsets[0]` to build the party.
+2. `new_game(seed)`: emit `new_game`, seed `rules.Rng`, load party from the savegame characters,
+   mode `map`, emit `paragraph{1}`.
+3. Map mode: movement/bump/transition/paragraph/message/look/rest/save/load, `input` before each
+   effect, `ignored` for unlisted keys, checkpoint snapshots.
+4. Hooks (lock/recruit/healer/win), shops, character screen.
+5. Combat per LR-26..44 (use `tests/wl_combat_ref.py` as the oracle for the raider fight).
+Then `src/wlengine/ui.py` (`render_frame`) and `src/wlengine/__main__.py` for M6.
+Diff every step against `tests/fixtures-generated/reflog4.txt` (line N = event N, `seq` stripped).
+
+[harness] iter 26 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 38->38/82; M6 0->0/55; no file changes
+
+[harness] iter 27 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 38->38/82; M6 0->0/55; files changed: tests/fixtures-generated/dd/ALLHTDS1, tests/fixtures-generated/dd/ALLPICS1, tests/fixtures-generated/dd/COLORF.FNT, tests/fixtures-generated/dd/CURS, tests/fixtures-generated/dd/END.CPA, tests/fixtures-generated/dd/GAME1, tests/fixtures-generated/dd/IC0_9.WLF, tests/fixtures-generated/dd/LABHOOKS.JSON
+
+### iter 28 note (2026-10-22T08:41:31-05:00)
+## iter 28 (M5 focus): read-only reconnaissance, no code written yet
+
+Budget went to reading specs/tests. Everything needed to write `src/wlengine/headless.py`
+is now pinned down. Key facts (verified against the compiled data in
+`tests/fixtures-generated/dd/` and `SPEC/scenario/walkthrough-reference-log.json`):
+
+### API the tests call
+- `wlengine.headless.run(data_dir: str, script: dict, seed: int|None) -> list[dict]`
+  (conftest `Runner.run`). `script` = `{"seed": int, "start": "new"|"create", "script": [token|macro]}`.
+  `seed` arg overrides script seed. Raises `wlengine.errors.ScriptError` for a bad token
+  ("JUMP"), `RepeatLimitError` (subclass of ScriptError) when `repeat_until` exceeds `max`,
+  `FormatError` when a load finds a bad LABSTATE.BIN.
+- M6 also needs `wlengine.ui.render_frame(data_dir) -> 25 strings of 80 chars` and
+  `python3 -m wlengine` CLI: `--headless --data DIR --script FILE [--seed N] --log OUT.jsonl`
+  (exit 0; JSONL, no trailing spaces) and `--data DIR --render-frame` (prints 25 lines, exit 0).
+
+### Data loading (Engine.__init__)
+`containers.read_tables(dd/LABTABLES.BIN)`; `maps.load_map(dd, loc)` for loc 0..3;
+`rules.read_skill_table(dd/LABSKILL.BIN)`; `json.load(dd/LABHOOKS.JSON)["hooks"]`;
+`json.load(dd/PARAGRAPHS.JSON)["paragraphs"]`; `strings.read_labstr(dd/LABSTR.BIN)`
+(table 1 = UI strings, 2 = skill/item names, 3 = ranks);
+savegame = `containers.decode_savegame(GAME1, tables["savegameOffsets"][0])`
+(group0 order [1,2,3,4,0,0,0], x15 y20 map1, prev 0, viewport 15/20, currentMembers 4,
+hour 8 minute 0, serial 0; characters 1..4 = Hessa/Tobin/Maro/Dell, xp 90, level 1).
+Shop lists: `decode_shop_list(GAME1, savegameOffsets[0] + shopListRelOffsets[n])`
+(shopListRelOffsets = [0,766,1532,2298] — relative to the savegame block start; verify).
+Start: location 1, x 15, y 20, hour 8, minute 0, day 1, paragraph 1, seed 20261021.
+
+### Event order (from refdump, see below)
+- new game: `new_game{seed}` then `paragraph{n:1}`.
+- step: `input{key}` -> `move{location,x,y,steps}` -> clock events (`natural_heal{members}`,
+  `day{day}`) -> class effect (`paragraph`, `message`, `shop_open`, `encounter_start`, ...).
+- bump: `input` -> `bump{x,y,action_class,action}` -> record message -> tail `cell_change` -> hook events.
+- transition: `map_change{location,x,y}` (no step for arrival); L-TR4 stores prev cell.
+- Saltwell timePerStep = 1 minute; overworld = 10 minutes.
+- `R` -> `rest` (60 min, natural_heal per hour crossed, then Foraging heal).
+- `L`+dir -> `look{x,y,image,action_class}` (no step/time/draw). Unlisted key -> `ignored{key}`.
+- Shop: `B`->`prompt{buy_item,items:[ids]}`; letter->`prompt{member}`; digit->`money` then
+  `buy{member,item,price,slot,status}`; `S`->`prompt{member}`->digit->`prompt{item_slot}`->
+  letter->`sell{member,item,price,slot}` then `money`; `X`->`shop_close`.
+  `C`->`prompt{member}`->digit->`char_open{member}`; `E`->`prompt{item_slot}`->letter->
+  `equip{member,slot,item,ac}`; `X`->`char_close`.
+- Recruit: bump class 11 -> `paragraph` -> `prompt{recruit}` -> `Y` -> `cell_change`
+  (class 0, action 0, cleared_image) then `recruit{location,npc,slot}`.
+- Lock: bump -> `message` (fail msg) -> `check{member,skill,level,need,roll,success}`;
+  success: `unlock{x,y}`, `cell_change` (tail, image unchanged), `cell_change` (record tile),
+  `xp{member,delta:10,total}`, `paragraph`; failure: `message` (fail msg). Key path:
+  `message` -> `key_used{member,item}` -> `unlock` -> 2x `cell_change` -> `paragraph`.
+- Healer: bump -> `prompt{heal,price}` -> `Y` -> `money{member:1,delta:-price,total}` -> `heal_all{price}`.
+- Win: bump -> `paragraph{not_yet}` without item; with item `paragraph{win_paragraph}` then
+  `win{steps,day,minutes}` (minutes = time of day).
+- Combat (LR-26..44): `encounter_start{groups:[{monster,count,band,hp}]}` -> record `paragraph`
+  -> `check{member,skill:18,...}` -> `surprised{}` on failure -> `round_start{round:0}` ->
+  monster phase 1 -> `group_closes`. Then `A` -> `round_orders{round:N,orders:{"1":["fire",1],...}}`
+  -> `round_start{round:N}` -> party phase 1 in slot order (`attack`/`click`/`jam`/`reload`/
+  `unjam`/`monster_dies`) -> monster phase 1 -> phase 2 speed order -> `group_closes`.
+  Victory: `combat_end{result:victory,rounds:N}`, then per member in slot order `xp` +
+  `promote{member,level,max_hp,rank}` on a rise, then record tail `cell_change` (class 5),
+  loot `money{member:1,delta:75,total:195}`, then `cell_change` back to class 0.
+  Auto orders (LR-33): wait / unjam / fire lowest living group / reload / melee-or-advance.
+- Save: `S` -> `save{serial:1}`; `O` -> `prompt{load}` -> `Y` -> `load{serial:1}`.
+- Checkpoint snapshot keys: location,x,y,steps,day,hour,minute,mode,cell_changes (sorted by
+  location,x,y), party[{slot,name,npc,level,xp,max_hp,hp,cond,money,ac,rank,skill_points,
+  items[[id,status]],weapon_slot,armour_slot}], rng_state. cell_changes entries are
+  [location,x,y,class,action,image].
+
+### Diff target I created this iteration
+`tests/fixtures-generated/refdump.txt` (1022 lines) = the reference log with `seq` stripped,
+`CP <name>` for checkpoints and `IN <key>` for inputs. It is byte-identical to
+`tests/fixtures-generated/reflog4.txt`. Use it for manual diffing only — src/ must never
+open it (SPEC-07 rule 6.1 forbids src/ naming the reference log; the audit hook also
+forbids opening SPEC/reference/* and SPEC/scenario/walkthrough-reference-log.json).
+`tests/fixtures-generated/dd/` is a compiled data dir usable for local runs.
+
+### Next step (unchanged plan, now with exact shapes)
+Write `src/wlengine/headless.py` in this order, running `run_tests M5` after each chunk:
+1. Engine init + `new_game(seed)` + checkpoint snapshots (gets test_new_game,
+   test_seed_override, test_steps_clock_and_transition, test_bump_is_not_a_step,
+   test_rest, test_win_hook_without_item).
+2. Map mode: movement/bump/transition/paragraph/message/look/rest/save/load, `input`
+   before each effect, `ignored` for unlisted keys.
+3. Hooks (lock/recruit/healer/win), shops, character screen.
+4. Combat per LR-26..44 (oracle: `tests/wl_combat_ref.py`).
+Then `src/wlengine/ui.py` (`render_frame`) and `src/wlengine/__main__.py` for M6.
+Diff every step against `tests/fixtures-generated/refdump.txt`.
+
+[harness] iter 28 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 38->38/82; M6 0->0/55; files changed: tests/fixtures-generated/refdump.txt
+
+### iter 29 note (2026-10-22T09:22:17-05:00)
+## Iteration 29 (M5 focus) — read-only reconnaissance, no code written
+
+### Status
+M1-M4 PASS. M5 38/82. M6 0/55. The single blocker for all 44 M5 failures and all
+55 M6 failures is `ModuleNotFoundError: No module named 'wlengine.headless'`.
+Nothing else in M5 fails. So the whole job is: write `src/wlengine/headless.py`
+(and later `ui.py`, `__main__.py`).
+
+### API contract (SPEC-07 2.10, 2.11) — exact
+- `wlengine.headless.run(data_dir: str, script: dict, seed: int = None) -> list[dict]`
+  returns the event log; each event dict has `seq` (0,1,2,...) then `type` then
+  the SPEC-06 section 6 fields, in that key order.
+- `seed` overrides `script["seed"]`.
+- `script` = `{"seed": N, "start": "new"|"create" (default "new"),
+  "script": [token | macro, ...]}`. Tokens: `UP DOWN LEFT RIGHT ESC ENTER` or one
+  printable ASCII char (case-sensitive). Macros:
+  `{"repeat_until": COND, "keys": [...], "max": N}` (COND is `mode:NAME` or
+  `cell:L,X,Y`; on exceeding max raise `RepeatLimitError`) and
+  `{"checkpoint": NAME}` (emits a `checkpoint` event with `name` + `state`, consumes
+  no input).
+- Exceptions: malformed token -> `wlengine.errors.ScriptError`; repeat limit ->
+  `RepeatLimitError` (subclass of ScriptError); data error / bad load ->
+  `FormatError` (or `ChecksumError`). All from `wlengine.errors`.
+- Save writes the GAME1 savegame block (via `containers.encode_savegame`) and
+  `LABSTATE.BIN` (via `labstate.encode_labstate`) into `data_dir`; load reads them.
+- `wlengine.ui.render_frame(data_dir) -> list[str]` (25 strings of exactly 80
+  chars, no curses import); `python3 -m wlengine` CLI:
+  `--headless --data DIR --script FILE [--seed N] --log OUT.jsonl` (exit 0, JSONL,
+  no trailing spaces) and `--data DIR --render-frame` (25 lines, exit 0).
+
+### Checkpoint snapshot (SPEC-06 6.4) — exact key order
+`{"location","x","y","steps","day","hour","minute","mode","cell_changes","party","rng_state"}`
+- `cell_changes`: `[[location,x,y,class,action,image], ...]` sorted by (location,x,y).
+- party member: `{"slot","name","npc","level","xp","max_hp","hp","cond","money","ac",
+  "rank","skill_points","items":[[id,status],...],"weapon_slot","armour_slot"}`.
+  `npc` is 0 for premade PCs, 1 for recruits. `weapon_slot`/`armour_slot` 1-based, 0=none.
+- `rng_state` = `Rng.state` after the last draw.
+Reference CP1 (seed 20261021) confirms: location 1, x15 y20, steps 0, day 1, hour 8,
+minute 0, mode "map", cell_changes [], rng_state 20261021, 4 members Hessa/Tobin/
+Maro/Dell, xp 90, level 1, rank "Drifter", skill_points 0, ac 3/2/3/2, money
+120/60/80/70, items [[3,6],[4,2],[7,0]] / [[5,8],[6,1],[1,0]] / [[3,6],[4,1]] /
+[[3,6],[4,1],[9,3]], weapon_slot 1, armour_slot 3/0/0/0.
+
+### Data loading (Engine.__init__), all confirmed against tests/fixtures-generated/dd/
+- `containers.read_tables(dd/LABTABLES.BIN)` -> dict with keys mapOffsets,
+  tileMapOffsets, locationMapping, mapSizes, sharedLocations, mobSpriteMap,
+  savegameOffsets, savegameSize, shopListRelOffsets, mapCounts, shopListCounts,
+  tilesetOffsets, tilesetSizes, portraitOffsets1/2, portraitIndices1/2.
+- `maps.load_map(dd, loc)` for loc 0..3. Verified: mapSize 64/32/32/32,
+  timePerStep 2560/256/256/512 (low byte seconds, high byte minutes -> overworld
+  10 min/step, towns 1 min/step), borderImage 18/35/26/38.
+- `rules.read_skill_table(dd/LABSKILL.BIN)` -> 36 x [min_iq, cost, attr_offset].
+- `json.load(dd/LABHOOKS.JSON)["hooks"]`; `json.load(dd/PARAGRAPHS.JSON)["paragraphs"]`.
+- `strings.read_labstr(dd/LABSTR.BIN)` -> list of tables; table 1 = UI strings,
+  2 = skill/item names, 3 = ranks.
+- savegame = `containers.decode_savegame(GAME1, tables["savegameOffsets"][0])`;
+  group0 order [1,2,3,4,0,0,0], x15 y20 map1, prev 0, viewport 15/20,
+  currentMembers 4, hour 8 minute 0, serial 0.
+- Shop lists: `decode_shop_list(GAME1, savegameOffsets[0] + shopListRelOffsets[n])`
+  (shopListRelOffsets = [0,766,1532,2298]).
+- Start: location 1, x 15, y 20, hour 8, minute 0, day 1, paragraph 1, seed 20261021.
+
+### Event order (verified against SPEC/scenario/walkthrough-reference-log.json, 1022 events)
+Event type counts: input 412, move 358, attack 48, paragraph 22, prompt 20,
+cell_change 17, xp 12, checkpoint 11, message 11, bump 9, round_start 9,
+natural_heal 9, money 8, check 8, round_orders 8, monster_dies 7, map_change 6,
+buy 5, promote 4, shop_open 3, shop_close 3, item_gain 3, reload 3, char_open 2,
+equip 2, char_close 2, recruit 2, encounter_start 2, combat_end 2, unlock 2,
+new_game 1, sell 1, jam 1, unjammed 1, save 1, load 1, heal_all 1, surprised 1,
+group_closes 1, key_used 1, day 1, win 1.
+
+- new game: `new_game{seed}` then `paragraph{n:1}`.
+- step: `input{key}` -> `move{location,x,y,steps}` -> clock events
+  (`natural_heal{members}`, `day{day}`) -> class effect (`paragraph`, `message`,
+  `shop_open`, `encounter_start`, ...).
+- bump: `input` -> `bump{x,y,action_class,action}` -> record message -> tail
+  `cell_change` -> hook events.
+- transition: `map_change{location,x,y}` (no step for arrival); L-TR4 stores prev cell.
+- `R` -> `rest` (60 min, natural_heal per hour crossed, then Foraging heal).
+- `L`+dir -> `look{x,y,image,action_class}` (no step/time/draw). Unlisted key ->
+  `ignored{key}`.
+- Shop: `B`->`prompt{buy_item,items:[ids]}`; letter->`prompt{member}`; digit->
+  `money` then `buy{member,item,price,slot,status}`; `S`->`prompt{member}`->digit->
+  `prompt{item_slot}`->letter->`sell{member,item,price,slot}` then `money`;
+  `X`->`shop_close`. `C`->`prompt{member}`->digit->`char_open{member}`;
+  `E`->`prompt{item_slot}`->letter->`equip{member,slot,item,ac}`; `X`->`char_close`.
+- Recruit: bump class 11 -> `paragraph` -> `prompt{recruit}` -> `Y` -> `cell_change`
+  (class 0, action 0, cleared_image) then `recruit{location,npc,slot}`.
+- Lock: bump -> `message` (fail msg) -> `check{member,skill,level,need,roll,success}`;
+  success: `unlock{x,y}`, `cell_change` (tail, image unchanged), `cell_change`
+  (record tile), `xp{member,delta:10,total}`, `paragraph`; failure: `message`.
+  Key path: `message` -> `key_used{member,item}` -> `unlock` -> 2x `cell_change` ->
+  `paragraph`.
+- Healer: bump -> `prompt{heal,price}` -> `Y` -> `money{member:1,delta:-price,total}`
+  -> `heal_all{price}`.
+- Win: bump -> `paragraph{not_yet}` without item; with item `paragraph{win_paragraph}`
+  then `win{steps,day,minutes}` (minutes = time of day).
+- Combat (LR-26..44): `encounter_start{groups:[{monster,count,band,hp}]}` -> record
+  `paragraph` -> `check{member,skill:18,...}` -> `surprised{}` on failure ->
+  `round_start{round:0}` -> monster phase 1 -> `group_closes`. Then `A` ->
+  `round_orders{round:N,orders:{"1":["fire",1],...}}` -> `round_start{round:N}` ->
+  party phase 1 in slot order (`attack`/`click`/`jam`/`reload`/`unjam`/`monster_dies`)
+  -> monster phase 1 -> phase 2 speed order -> `group_closes`.
+  Victory: `combat_end{result:victory,rounds:N}`, then per member in slot order `xp` +
+  `promote{member,level,max_hp,rank}` on a rise, then record tail `cell_change`
+  (class 5), loot `money{member:1,delta:75,total:195}`, then `cell_change` back to
+  class 0.
+- Auto orders (LR-33): wait / unjam / fire lowest living group / reload /
+  melee-or-advance.
+- Save: `S` -> `save{serial:1}`; `O` -> `prompt{load}` -> `Y` -> `load{serial:1}`.
+
+### Diff target I created earlier
+`tests/fixtures-generated/refdump.txt` (1022 lines) = the reference log with `seq`
+stripped, `CP <name>` for checkpoints and `IN <key>` for inputs. Byte-identical to
+`tests/fixtures-generated/reflog4.txt`. Manual diffing only — src/ must never open
+it (SPEC-07 6.1 forbids src/ naming the reference log; the audit hook also forbids
+opening SPEC/reference/* and SPEC/scenario/walkthrough-reference-log.json).
+`tests/fixtures-generated/dd/` is a compiled data dir usable for local runs.
+
+### Next step (unchanged plan, now with exact shapes)
+Write `src/wlengine/headless.py` in this order, running `run_tests M5` after each
+chunk:
+1. Engine init + `new_game(seed)` + checkpoint snapshots (gets test_new_game,
+   test_seed_override, test_steps_clock_and_transition, test_bump_is_not_a_step,
+   test_rest, test_win_hook_without_item).
+2. Map mode: movement/bump/transition/paragraph/message/look/rest/save/load,
+   `input` before each effect, `ignored` for unlisted keys.
+3. Hooks (lock/recruit/healer/win), shops, character screen.
+4. Combat per LR-26..44 (oracle: `tests/wl_combat_ref.py`).
+Then `src/wlengine/ui.py` (`render_frame`) and `src/wlengine/__main__.py` for M6.
+Diff every step against `tests/fixtures-generated/refdump.txt`.
+
+[harness] iter 29 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 38->38/82; M6 0->0/55; no file changes
+
+### iter 30 note (2026-10-22T10:09:43-05:00)
+### Iter 30 (M5 focus): read-only recon, no code written yet. Key findings to reuse.
+
+**Blocker**: `wlengine.headless` does not exist -> 44 M5 failures + all 55 M6.
+Everything else in M5 (38 tests: Rng, characters, checks, time, xp, prices, pay,
+monsters, combat formulas, LABSTATE) already passes. So M5 needs ONLY
+`src/wlengine/headless.py` (plus `ui.py`/`__main__.py` for M6).
+
+**API contract (SPEC-07 2.10)**: `headless.run(data_dir: str, script: dict,
+seed: int = None) -> list[dict]`. Script = `{"seed": N, "start": "new"|"create",
+"script": [token | {"repeat_until": COND, "keys": [...], "max": N} |
+{"checkpoint": NAME}]}`. Tokens: "UP","DOWN","LEFT","RIGHT","ESC","ENTER", or one
+printable char (case-sensitive). `seed` arg overrides script seed. Errors:
+RepeatLimitError (exit 2), FormatError/ChecksumError (3), ScriptError (4).
+Every event dict has `seq` (0,1,2,...) and `type`; tests strip `seq` before
+comparing. `checkpoint` events carry `name` + `state` (SPEC-06 6.4) and consume
+no input. A save writes GAME1's savegame block AND LABSTATE.BIN in data_dir.
+
+**Checkpoint state keys** (SPEC-06 6.4): location, x, y, steps, day, hour,
+minute, mode, cell_changes (sorted by location,x,y; each [loc,x,y,class,action,
+image]), party (list of {slot,name,npc,level,xp,max_hp,hp,cond,money,ac,rank,
+skill_points,items (non-empty slots in slot order, [id,status]),weapon_slot,
+armour_slot}), rng_state.
+
+**Verified event shapes from tests/fixtures-generated/refdump.txt (1022 lines,
+= reference log with seq stripped, CP <name> for checkpoints, IN <key> for
+inputs). This is my diff target; src/ must never open it.**
+- new game: `new_game{seed}` then `paragraph{n:1}`.
+- step: `input{key}` -> `move{location,x,y,steps}` -> clock events
+  (`natural_heal{members:[slots]}`, `day{day}`) -> class effect.
+- bump: `input` -> `bump{x,y,action_class,action}` -> record message ->
+  tail `cell_change` -> hook events. Bump does NOT increment steps.
+- transition: `map_change{location,x,y}` (no step for arrival).
+- `R` -> `rest` (60 min; natural_heal per hour crossed; no message).
+- Shop: `B`->`prompt{buy_item,items:[ids]}`; letter->`prompt{member}`;
+  digit->`money{member,delta:-price,total}` then `buy{member,item,price,slot,
+  status}`; `S`->`prompt{member}`->digit->`prompt{item_slot}`->letter->
+  `sell{member,item,price,slot}` then `money`; `X`->`shop_close`.
+  `C`->`prompt{member}`->digit->`char_open{member}`; `E`->`prompt{item_slot}`
+  ->letter->`equip{member,slot,item,ac}`; `X`->`char_close`.
+- Recruit (class 11 hook): bump -> `paragraph` -> `prompt{recruit}` -> `Y` ->
+  `cell_change` (class 0, action 0, cleared_image) then `recruit{location,npc,
+  slot}`.
+- Lock: bump -> `message` (fail msg) -> `check{member,skill,level,need,roll,
+  success}`; success: `unlock{x,y}`, `cell_change` (tail, image unchanged),
+  `cell_change` (record tile), `xp{member,delta:10,total}`, `paragraph`;
+  failure: `message`. Key path: `message` -> `key_used{member,item}` ->
+  `unlock` -> 2x `cell_change` -> `paragraph`.
+- Healer: bump -> `prompt{heal,price}` -> `Y` -> `money{member:1,delta:-price,
+  total}` -> `heal_all{price}`.
+- Win: bump -> `paragraph{not_yet}` w/o item; with item `paragraph{win_para}`
+  then `win{steps,day,minutes}` (minutes = time of day).
+- Combat: `encounter_start{groups:[{monster,count,band,hp}]}` -> record
+  `paragraph` -> `check{member,skill:18,...}` -> `surprised{}` on failure ->
+  `round_start{round:0}` -> monster phase 1 -> `group_closes`. Then `A` ->
+  `round_orders{round:N,orders:{"1":["fire",1],...}}` -> `round_start{round:N}`
+  -> party phase 1 in slot order (`attack`/`click`/`jam`/`reload`/`unjam`/
+  `monster_dies`) -> monster phase 1 -> phase 2 speed order -> `group_closes`.
+  Victory: `combat_end{result:victory,rounds:N}`, then per member in slot order
+  `xp` + `promote{member,level,max_hp,rank}` on a rise, then record tail
+  `cell_change` (class 5), loot `money{member:1,delta:75,total:195}`, then
+  `cell_change` back to class 0.
+- Save: `S` -> `save{serial:1}`; `O` -> `prompt{load}` -> `Y` -> `load{serial:1}`.
+- Unlisted key -> `ignored{key}`.
+
+**Data loading (already verified in earlier iterations)**: containers.read_tables
+(dd/LABTABLES.BIN); maps.load_map(dd, loc) for loc 0..3 (sizes 64/32/32/32,
+timePerStep 2560/256/256/512 = low byte seconds, high byte minutes);
+rules.read_skill_table(dd/LABSKILL.BIN); json LABHOOKS.JSON["hooks"],
+PARAGRAPHS.JSON["paragraphs"]; strings.read_labstr(dd/LABSTR.BIN) (table 1 = UI
+strings, 2 = skill/item names, 3 = ranks). Savegame =
+containers.decode_savegame(GAME1, tables["savegameOffsets"][0]); group0 order
+[1,2,3,4,0,0,0], x15 y20 map1, prev 0, viewport 15/20, currentMembers 4, hour 8
+minute 0, serial 0. Shop lists: decode_shop_list(GAME1, savegameOffsets[0] +
+shopListRelOffsets[n]) (rel offsets [0,766,1532,2298]). Start: location 1, x 15,
+y 20, hour 8, minute 0, day 1, paragraph 1, seed 20261021.
+
+**Existing helpers to build on**: maps.record_at/is_passable/apply_tail/
+resolve_transition/image_at; rules.* (all formulas); containers.encode_savegame/
+encode_character/decode_shop_list; labstate.encode_labstate/decode_labstate;
+errors.{FormatError,ChecksumError,ScriptError,RepeatLimitError}.
+
+**Next step (unchanged plan)**: write `src/wlengine/headless.py` in chunks,
+running `run_tests M5` after each:
+1. Engine init + `new_game(seed)` + checkpoint snapshots (gets test_new_game,
+   test_seed_override, test_steps_clock_and_transition, test_bump_is_not_a_step,
+   test_rest, test_win_hook_without_item).
+2. Map mode: movement/bump/transition/paragraph/message/look/rest/save/load,
+   `input` before each effect, `ignored` for unlisted keys.
+3. Hooks (lock/recruit/healer/win), shops, character screen.
+4. Combat per LR-26..44 (oracle: tests/wl_combat_ref.py).
+Then `src/wlengine/ui.py` (`render_frame`) and `src/wlengine/__main__.py` for M6.
+Diff every step against tests/fixtures-generated/refdump.txt (manual diff only).
+Note: `tests/fixtures-generated/dd/` is a compiled data dir usable for local runs.
+
+[harness] iter 30 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 38->38/82; M6 0->0/55; no file changes
+
+### iter 31 note (2026-10-22T10:53:52-05:00)
+## Iter 31 (M5 focus) — exploration only, NO code written yet
+
+### What I did
+Read SPEC-06 (full), SPEC-04 (full), SPEC-03 §9, SPEC-05 §5.5/§7/§9/§14.2, SPEC-07,
+tests/test_m5_rules.py (engine section lines 435-834), tests/wl_support.py,
+tests/conftest.py (Runner fixture), tests/wl_combat_ref.py, and the reference log
+tests/fixtures-generated/refdump.txt (1022 lines). Probed the compiled data dir
+tests/fixtures-generated/dd/ with the existing src/ modules.
+
+### Key confirmations (all verified by running python3 against dd/)
+- `containers.read_tables(dd/LABTABLES.BIN)` works; savegame payload at
+  `savegameOffsets[0]+4`, 0x800 bytes, rotating-XOR whole decode.
+- Start savegame payload: group0 order [1,2,3,4,0,0,0], x=15 y=20 map=1, prev 0/0/0,
+  viewport 15/20, currentMembers 4, currentParty 0, currentMap 1, totalMembers 4,
+  minute 0 hour 8, serial 0. Matches SPEC-05 start (loc 1, 15,20, hour 8, day 1, para 1).
+- `maps.load_map(dd,1)`: size 32, borderImage 35, timePerStep 256 (=0 min, 1 s per step
+  → Saltwell steps cost 1 minute each; overworld map0 timePerStep 2560 = 10 min/step).
+  Cell (15,20) class 0 action 0 image 28. Map strings[1]="Read paragraph 2." etc.
+- refdump.txt is the exact diff target: `IN <key>` lines are inputs, `CP <name>` are
+  checkpoints, all other lines are events with `seq` stripped. src/ must never open it.
+
+### Event-order facts extracted from refdump (must match exactly)
+- new game: `new_game{seed}` then `paragraph{n:1}`.
+- step: `input` → `move{location,x,y,steps}` → clock events (`natural_heal{members}`,
+  `day{day}`) → class effect (paragraph/message/shop_open/cell_change/encounter).
+- bump: `input` → `bump{x,y,action_class,action}` → record message → tail `cell_change`
+  → hook events. Bump does NOT increment steps and takes no time.
+- transition: `input` → `move` (step counted on the cell left) → `map_change{location,x,y}`
+  (arrival is not a step). Paragraphs on the way are emitted between.
+- Shop: `B`→`prompt{buy_item,items:[ids]}`; item letter→`prompt{member}`; digit→
+  `money{member,delta:-price,total}` then `buy{member,item,price,slot,status}`;
+  `S`→`prompt{member}`→digit→`prompt{item_slot}`→letter→`sell{...}` then `money`;
+  `X`→`shop_close`. `C`→`prompt{member}`→digit→`char_open{member}`; `E`→
+  `prompt{item_slot}`→letter→`equip{member,slot,item,ac}`; `X`→`char_close`.
+- Lock (class 4 impassable + hook): bump → `message` (record msg) → `check{member,skill,
+  level,need,roll,success}`; success: `unlock{x,y}`, `cell_change` (tail, image unchanged),
+  `cell_change` (record tile), `xp{member,delta:10,total}`, `paragraph`; failure: `message`.
+  Key path: `message` → `key_used{member,item}` → `unlock` → 2× `cell_change` → `paragraph`.
+- Recruit: bump → `paragraph` → `prompt{recruit}` → `Y` → `cell_change` (class 0, action 0,
+  cleared_image) then `recruit{location,npc,slot}`.
+- Healer: bump → `prompt{heal,price}` → `Y` → `money{member:1,delta:-price,total}` →
+  `heal_all{price}`.
+- Win: bump → `paragraph{not_yet}` w/o item; with item `paragraph{win_para}` then
+  `win{steps,day,minutes}` (minutes = time of day).
+- Combat: `encounter_start{groups:[{monster,count,band,hp}]}` → record `paragraph` →
+  `check{member,skill:18,...}` → `surprised{}` on failure → `round_start{round:0}` →
+  monster phase 1 → `group_closes`. Then `A` → `round_orders{round:N,orders:{"1":["fire",1],...}}`
+  → `round_start{round:N}` → party phase 1 in slot order (`attack`/`click`/`jam`/`reload`/
+  `unjammed`/`monster_dies`) → monster phase 1 → phase 2 speed order → `group_closes`.
+  Victory: `combat_end{result:victory,rounds:N}`, then per member in slot order `xp` +
+  `promote{member,level,max_hp,rank}` on a rise, then record tail `cell_change` (class 5),
+  loot `money{member:1,delta:75,total:195}`, then `cell_change` back to class 0.
+- Save: `S` → `save{serial:1}`; `O` → `prompt{load}` → `Y` → `load{serial:1}`.
+- Unlisted key → `ignored{key}`.
+
+### API contract (SPEC-07 §2.10 / SPEC-06 §5)
+`headless.run(data_dir: str, script: dict, seed: int = None) -> list[dict]`.
+Script = `{"seed": N, "start": "new"|"create", "script": [token | {"repeat_until": COND,
+"keys": [...], "max": N} | {"checkpoint": NAME}]}`. Tokens: "UP","DOWN","LEFT","RIGHT",
+"ESC","ENTER", or one printable char (case-sensitive). `seed` arg overrides script seed.
+Errors: RepeatLimitError (exit 2), FormatError/ChecksumError (3), ScriptError (4).
+Every event has `seq` (0,1,2,...) and `type`; tests strip `seq`. `checkpoint` events carry
+`name` + `state` (SPEC-06 §6.4) and consume no input. A save writes GAME1's savegame block
+AND LABSTATE.BIN in data_dir.
+
+### Checkpoint state keys (SPEC-06 §6.4)
+location, x, y, steps, day, hour, minute, mode, cell_changes (sorted by location,x,y; each
+[loc,x,y,class,action,image]), party (list of {slot,name,npc,level,xp,max_hp,hp,cond,money,
+ac,rank,skill_points,items (non-empty slots in slot order, [id,status]),weapon_slot,
+armour_slot}), rng_state.
+
+### Existing helpers to build on
+maps.record_at/is_passable/apply_tail/resolve_transition/image_at; rules.* (all formulas
+incl. Rng, skill_check, pick_checker, advance_clock, pay, build_groups, monster_hp,
+monster_damage, ranged_need, melee_need, monster_need, flee_need, jam_chance,
+unarmed_attacks, melee_damage_bonus, damage_member, speed_order, xp_threshold, level_after,
+buy_price, sell_price); containers.encode_savegame/encode_character/decode_shop_list/
+decode_savegame/read_tables/resolve_location; labstate.encode_labstate/decode_labstate;
+errors.{FormatError,ChecksumError,ScriptError,RepeatLimitError}; strings.read_labstr
+(table 1 = UI strings, 2 = skill/item names, 3 = ranks).
+
+### Next step (unchanged plan — write src/wlengine/headless.py in chunks)
+1. Engine init + `new_game(seed)` + checkpoint snapshots → gets test_new_game,
+   test_seed_override, test_steps_clock_and_transition, test_bump_is_not_a_step,
+   test_rest, test_win_hook_without_item.
+2. Map mode: movement/bump/transition/paragraph/message/look/rest/save/load, `input`
+   before each effect, `ignored` for unlisted keys.
+3. Hooks (lock/recruit/healer/win), shops, character screen.
+4. Combat per LR-26..44 (oracle: tests/wl_combat_ref.py).
+Then `src/wlengine/ui.py` (`render_frame`) and `src/wlengine/__main__.py` for M6.
+Diff every step against tests/fixtures-generated/refdump.txt (manual diff only).
+`tests/fixtures-generated/dd/` is a compiled data dir usable for local runs.
+Note: M1-M4 all pass, so M5 needs ONLY `src/wlengine/headless.py`.
+
+[harness] iter 31 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 76->76/76; M5 38->38/82; M6 0->0/55; no file changes
+
+### iter 32 note (2026-10-22T11:33:43-05:00)
+## Iter 32 (M5 focus) — reconnaissance only, no code written yet
+
+Budget went to reading SPEC-04/06/07, tests/test_m5_rules.py, tests/wl_combat_ref.py,
+tests/conftest.py and the compiled fixture data. Nothing was written to src/ this
+iteration, so M5 is still 38/82. Next iteration must WRITE src/wlengine/headless.py.
+
+### Confirmed API (SPEC-06 §5, SPEC-07 §2.10)
+`headless.run(data_dir: str, script: dict, seed: int|None=None) -> list[dict]`.
+Script keys: `seed`, `start` ("new"|"create"), `script` = list of token |
+`{"repeat_until": COND, "keys": [...], "max": N}` | `{"checkpoint": NAME}`.
+COND = `mode:NAME` or `cell:L,X,Y` (cell has an entry in the cell-change table).
+Every event gets `seq` (0,1,2,...). `checkpoint` events carry `name` + `state`
+(SPEC-06 §6.4) and consume no input. Errors: RepeatLimitError(2),
+FormatError/ChecksumError(3), ScriptError(4). Tests call it via `W.call`, so
+raising the right exception type matters (test_load_bad_labstate expects
+FormatError from `headless.run` on a corrupt LABSTATE.BIN).
+
+### Checkpoint state keys (SPEC-06 §6.4) — exact
+location, x, y, steps, day, hour, minute, mode, cell_changes (sorted by
+location,x,y; each [loc,x,y,class,action,image]), party (list of {slot,name,npc,
+level,xp,max_hp,hp,cond,money,ac,rank,skill_points,items (non-empty slots in slot
+order, [id,status]),weapon_slot,armour_slot}), rng_state.
+`hour`/`minute` are derived from the clock: minute-of-day = clock minute; hour =
+minute//60. `advance_clock` in rules.py returns {"day","minute","second"} and a
+list of hours crossed; hour = minute//60.
+
+### Compiled fixture data facts (tests/fixtures-generated/dd, usable for local runs)
+- LABTABLES: mapOffsets [0,7874,10280,13128,...], tileMapOffsets [6816,2151,2593,2518],
+  locationMapping [128,129,130,131], mapSizes [64,32,32,32],
+  savegameOffsets [15810, 0xFFFFFFFF], shopListRelOffsets [0,766,1532,2298],
+  mapCounts [4,0], shopListCounts [3,0].
+- Shop lists live in GAME1 at savegameOffset + shopListRelOffsets[i]? (verify:
+  shop block size 766; decode with containers.decode_shop_list(game, off)).
+- Map info: loc0 size64 border18 timePerStep 2560 (10 min/step); loc1 size32
+  border35 tps 256 (1 min/step); loc2 size32 border26 tps 256; loc3 size32
+  border38 tps 512 (2 min/step).
+- Map strings loc1: [0]="" [1]="Read paragraph 2." [2]="Read paragraph 3."
+  [3]="Read paragraph 5." [4]="The trough is green..." [5]="Saltwell Dry Goods."
+  [6]="Read paragraph 6." [7]="Orla shrugs. Some other time, then."
+- Records per location (from maps.load_map(...)['actions']):
+  loc0: class1 a1..a5 (messages 1..5); class10 a1->(loc1,15,30) a2->(loc2,1,16)
+    a3->(loc3,3,2); class3 a1 msg6 groups[[1,F,3]] tail(5,1); a2 msg7 [[2,T,4]]
+    tail(0,0); a3 msg8 [[3,F,2]] tail(0,0); a4 msg9 [[4,F,2],[1,F,1]] tail(5,2);
+    class4 a1 tile16 passable; a2 msg10 impassable tile17 tail(4,1);
+    class5 a1 cash [True,75] tail(0,0); a2 cash [False,40] tail(0,0).
+  loc1: class1 a1..a4 (msgs 1..4); class10 a1,a2 -> (loc0,10,41);
+    class11 a1 msg6; class6 a1 shop0 msg5.
+  loc2: class1 a1..a4; class10 a1..a3 -> (loc0,43,28); class11 a1 msg10, a2 msg12;
+    class4 a1 tile29 passable; a2 msg7 impassable tile30 tail(4,1);
+    class5 a1 items[[11,T,0]] tail(0,0); a2 items[[10,T,0]] tail(0,0);
+    class6 a1 shop1 msg5; a2 shop2 msg6.
+  loc3: class1 a1..a3; class10 a1 -> (loc0,44,48); class11 a1 msg16;
+    class3 a1 msg4 [[1,F,4]] tail(5,1); a2 msg5 [[2,T,2]] tail(0,0);
+    class4 a1 tile37 passable; a2 msg6 impassable tile39; a3 msg7 impassable
+    tile40 tail(11,0); a4 tile37 passable; a5 msg10 impassable tile39 tail(4,4);
+    a6 tile37 passable; a7 msg13 impassable tile25 tail(4,6);
+    class5 a1 items[[9,T,3]]; a2 items[[12,T,0]]; a3 items[[9,T,3]].
+- LABHOOKS.JSON (dd/LABHOOKS.JSON, {"hooks":[...]}): lock loc2(26,14) skill14 diff30
+  key0 tool0 succ8 fail9; lock loc0(31,55) skill17 diff25; lock loc3(26,11) skill29
+  diff30 remote{x:14,y:12,new_class:4,new_action:1}; lock loc3(16,6) skill23 diff60
+  key_item 11 succ11 fail12; lock loc3(4,20) skill16 diff35 tool_item 10 succ14
+  fail15; recruit loc1(8,17) npc0 min_cha0 refuse7 cleared28; recruit loc2(18,17)
+  npc0 min_cha10 refuse11 cleared28; recruit loc2(20,4) npc1 min_cha17 refuse13
+  cleared27; recruit loc3(14,14) npc0 min_cha0 refuse17 cleared37; healer loc1(22,4)
+  price30; healer loc2(25,21) price40; win loc1(15,11) item12 win_para24 not_yet4.
+- PARAGRAPHS.JSON = {"paragraphs":[{"n":..,"words":..,"text":..},...]}.
+- items.json: id->{price,class,type_byte,capacity,skill,damage,ammo}. Item type =
+  type_byte>>3 (1 melee,2 ranged,3 ammo,4 armour,5 medical,6 tool,7 quest,8 burst).
+  Item 3 Ranch pistol cap6 skill4 damage 0x18=1d8 ammo4; item 5 Lever rifle cap8
+  skill5 damage 0x26=2d6 ammo6; item 4 pistol rounds price8; item 6 rifle rounds
+  price14; item 7 Hide vest price30 damage1 (AC1); item 8 Plate jacket price110
+  damage3; item 9 Field kit cap3 damage 0x24=2d4; item 10 Rope coil tool skill16;
+  item 11 Gate card quest; item 12 Governor valve quest.
+- party.json: 4 premade PCs (Hessa Brand STR14 IQ13 LCK11 SPD12 AGL14 CHA15 money120
+  skills[[4,2],[20,1],[21,1],[18,1]] items[[3,6],[4,2],[7,0]] weapon_slot1 armour_slot3
+  xp90 lvl1; Tobin Ash STR16 IQ10 LCK12 SPD11 AGL12 CHA9 money60 skills[[5,2],[1,1],
+  [17,1],[3,1]] items[[5,8],[6,1],[1,0]] wslot1 aslot0; Maro Quill STR11 IQ16 LCK13
+  SPD13 AGL15 CHA10 money80 skills[[14,2],[23,1],[22,1],[4,1],[12,1]] items[[3,6],[4,1]]
+  wslot1; Dell Ostrow STR12 IQ15 LCK12 SPD12 AGL13 CHA12 money70 skills[[12,2],[13,1],
+  [4,1],[29,1],[18,1]] items[[3,6],[4,1],[9,3]] wslot1). DEX byte 0.
+- scenario.json start: l
[truncated: showing 60000 of 2683801 chars]
```