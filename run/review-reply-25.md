# Review reply 25 (session, 07:0x CDT, 22 Oct 2026)

M1 to M4 are done. M5 has stood at 38 of 82 for twelve iterations, and every one of those
iterations read 40 files and wrote nothing. Your worklog already holds the complete plan for
headless.py, down to the event shapes. You do not need to read anything again.

Do this, in this order, in the next iteration:

1. Turn 1: write_file src/wlengine/headless.py with part 1 only: imports, `Engine.__init__`
   (tables, maps, skill table, hooks, paragraphs, strings, shops, the savegame party),
   `new_game(seed)`, and the `run(data_dir, script, seed)` entry that returns the event list.
   Keep it under 250 lines. Do not read a spec or a file before this write; use the worklog.
2. Turn 2: `python3 -c "import wlengine.headless"`; fix import errors only.
3. Turn 3: run_tests M5. Take the first failing test, read only that test's assertion, fix,
   rerun. Repeat.
4. Append the map-mode handlers (movement, bump, transition, paragraph, look, rest, save,
   load) with apply_patch in blocks of about 100 lines, testing after each block.
5. Only after the map-mode tests pass: hooks and shops, then combat using
   tests/wl_combat_ref.py as the oracle for the raider fight.

Rules for every iteration from now on: at most 5 reads before the first write; a write in
every iteration; one worklog note at the end saying which test is next. Reading the whole
project again is what has cost the last twelve iterations.
