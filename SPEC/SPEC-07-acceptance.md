# SPEC-07: acceptance tests and milestones

Status: draft for freeze with PREREG-W1, version 1, 21 Oct 2026.
Scope: the public API the acceptance tests call, the milestone groups M1 to M6,
how the tests are run and read, and the rules that make a test result count.
The tests in `tests/` are the definition of done. This file tells the builder
what to implement so that they can run; SPEC-01 to SPEC-06 say how it must
behave.

## 1. Package and import contract

- The engine is the Python package `wlengine` in `src/wlengine/`. The tests put
  `src/` first on `sys.path` (in `tests/conftest.py`) and import `wlengine`.
- Python 3.11 or later, standard library only. No network.
- Every module and function in section 2 must exist under exactly that name.
  Extra modules and functions are allowed.
- `python3 -m wlengine` is the command line of SPEC-06 (section 2.10).
- Value conventions used by every test:
  - Integers are Python `int`; byte strings are `bytes`.
  - Text in decoded structures (names, ranks, map strings, monster names,
    LABSTR strings) is `str`, decoded as latin-1, one character per byte.
    Codec-level string functions (section 2.3) work on `bytes`.
  - Tuples and lists are interchangeable; integer dictionary keys are
    accepted where the schema says string keys; `True` and `1` compare equal.
  - Coordinates are (x, y); 2-D arrays are indexed `[y][x]`.
  - Slots, members, groups and monsters are numbered from 1 where SPEC-06
    says so; map monster indexes in records follow SPEC-03 L-MB1.

## 2. API

### 2.1 `wlengine.codecs` (SPEC-01 sections 2 and 4)

| Function | Returns | Notes |
| --- | --- | --- |
| `rotating_xor_encode(plain: bytes)` | `bytes` | xor1, xor2, ciphertext (SPEC-01 2.4; exact bytes are tested) |
| `rotating_xor_decode(data: bytes, mode: str, length: int)` | `bytes` | `mode` is `"whole"` or `"prefix"`. Whole: decode exactly `length` bytes after the two header bytes, `ChecksumError` on a checksum mismatch, `FormatError` on short input. Prefix: `length` is the body size B; return all B body bytes (decrypted prefix, then the plain rest); `FormatError` when the checksum never matches inside the body |
| `rotating_xor_prefix_length(data: bytes, length: int)` | `int` | prefix length found by prefix mode for body size `length` |
| `vertical_xor_decode(data: bytes, stride: int)` | `bytes` | SPEC-01 4.1 |
| `vertical_xor_encode(data: bytes, stride: int)` | `bytes` | SPEC-01 4.1 |

### 2.2 `wlengine.huffman` (SPEC-01 section 3, SPEC-02 section 2.2)

| Function | Returns | Notes |
| --- | --- | --- |
| `decode(data: bytes, out_size: int, offset: int = 0)` | `(bytes, int)` | decoded bytes and the byte offset after syncing to the next byte boundary; `FormatError` on reading past the end or a tree deeper than 256 |
| `encode(data: bytes)` | `bytes` | any prefix-free tree; zero padding to a whole byte only (the reference decoder must end exactly at the last byte) |
| `decode_msq(data: bytes, offset: int = 0, signature: bytes = b"msq")` | `(payload, disk, next_offset)` | Huffman msq block; `FormatError` on a wrong signature |
| `encode_msq(payload: bytes, disk: int = 0, signature: bytes = b"msq")` | `bytes` | |

### 2.3 `wlengine.strings` (SPEC-02 sections 9 and 12.3)

| Function | Returns | Notes |
| --- | --- | --- |
| `decode_table(data: bytes, offset: int = 0, end: int = None)` | `list[bytes]` | strings in index order (group x 4 + slot); must not fail on an out-of-range last group pointer |
| `encode_table(dictionary: bytes, strings: list[bytes])` | `bytes` | 60-byte dictionary first; groups of exactly 4 (L-ST1) |
| `read_labstr(path: str)` | `list[list[str]]` | every table of LABSTR.BIN, each padded to a multiple of 4 as decoded |

### 2.4 `wlengine.containers` (SPEC-02 sections 3 to 5 and 12)

| Function | Returns | Notes |
| --- | --- | --- |
| `read_tables(path: str)` | `dict` | LABTABLES.BIN; keys are the 17 field names of SPEC-02 12.2 (`mapOffsets` ... `portraitIndices2`); `savegameSize` is an `int`, every other value a list; `FormatError` on a wrong magic or size |
| `resolve_location(tables: dict, location: int)` | `(location, disk_code, map_index)` | SPEC-02 3.4 after the shared-location step; the returned location is the one after that step; `FormatError` for a location code of 0 |
| `decode_savegame(game: bytes, offset: int)` | `dict` | savegame schema below; `ChecksumError`, `FormatError` |
| `encode_savegame(savegame: dict, disk: int)` | `bytes` | the full 0x1206-byte block (L-SG2) |
| `decode_character(record: bytes)` | `dict` | character schema below |
| `encode_character(character: dict)` | `bytes` | 0x100 bytes |
| `decode_shop_list(game: bytes, offset: int)` | `dict` | `{"header": bytes (8), "items": [94 item dicts]}`; `ChecksumError`, `FormatError` |
| `encode_shop_list(items: list[dict], disk: int)` | `bytes` | 766 bytes; missing records are eight zero bytes |

Savegame dict keys: `groups` (4 dicts with `order` (7 ints), `x`, `y`,
`map`, `prevX`, `prevY`, `prevMap`), `viewportX`, `viewportY`,
`currentMembers`, `currentParty`, `currentMap`, `totalMembers`,
`extraGroups`, `minute`, `hour`, `combatScrollSpeed`, `serial`,
`characters` (7 character dicts).

Character dict keys: `name`, `strength`, `intelligence`, `luck`, `speed`,
`agility`, `dexterity`, `charisma`, `money`, `gender`, `nationality`,
`armorClass`, `maxCon`, `curCon`, `weaponSlot`, `skillPoints`, `experience`,
`level`, `armorSlot`, `lastCon`, `afflictions`, `npc`, `itemRefuse`,
`skillRefuse`, `attribRefuse`, `tradeRefuse`, `joinString`, `willingness`,
`rank`, `gameWon`, `specialPromotion`, `skills`, `items`. `skills` and
`items` list `[id, value]` for the non-zero ids, in slot order.

Shop item dict keys: `price`, `stock`, `type` (byte >> 3), `lowFlags`
(byte & 7), `capacity`, `skill`, `damage`, `ammo`.

These schemas are the ones `SPEC/reference/fixtures_gen.py` writes into its
`manifest.json`; the names agree field for field.

### 2.5 `wlengine.graphics` (SPEC-02 sections 6 to 8, 12.6, 12.7)

| Function | Returns |
| --- | --- |
| `read_tilesets(path)` | list of tilesets; a tileset is a list of tiles; a tile is 16 rows of 16 colour indexes |
| `read_portrait(path, offset)` | `{"base": bytes (4032, packed 4 bpp after vertical XOR), "scripts": [[[delay, update_index], ...], ...], "updates": [[[offset, bytes], ...], ...]}` |
| `portrait_offset(tables, raw_id, disk=1)` | `int`, or `None` when the index table holds 0x80 |
| `apply_portrait_update(image: bytes, update)` | `bytes`; `update` is a list of `[offset, bytes]` patches, XOR-applied |
| `read_sprites(ic_path, mask_path)` | list of `{"pixels": 16x16, "transparent": 16x16 of 0/1}`; `FormatError` when the counts differ |
| `read_font(path)` | list of glyphs, each 8 rows of 8 colour indexes |
| `glyph_index(code, glyph_count)` | `int` (L-FN1) |
| `read_cursors(path)` | list of `{"pixels": 16x16, "visible": 16x16 of 0/1}` (blue-plane mask) |
| `read_title(path)` | `bytes` (18432, packed 4 bpp after vertical XOR) |
| `read_ending(path)` | `{"base": bytes (18432), "updates": [[delay, [[offset, bytes (4)], ...]], ...]}` |
| `apply_ending_update(image: bytes, patches)` | `bytes` (patches replace 4 bytes, SPEC-02 8.5) |

### 2.6 `wlengine.maps` (SPEC-03)

| Function | Returns | Notes |
| --- | --- | --- |
| `decode_map(game: bytes, offset: int, map_size: int, tile_map_offset: int)` | map dict | `FormatError` for a bad header, a size mismatch, a prefix that does not end at `stringsOffset` (L-EN2), or any offset outside the body |
| `load_map(data_dir: str, location: int)` | map dict | through LABTABLES.BIN and GAME1 (SPEC-02 3.4) |
| `record_at(map, x, y)` | record dict or `None` | L-AC2, L-AC3; `FormatError` under L-AC5 (an action byte beyond the pointer list, or a null pointer for class 1, 3, 5, 6 or 10) |
| `is_passable(map, x, y)` | `bool` | SPEC-03 9.1, 9.6, L-MV1, L-MV2 |
| `apply_tail(record)` | `(class, action)` or `None` | L-TL1 (16 to 254 count as 255) |
| `resolve_transition(tables, record, x, y, previous)` | `(location, x, y)` | `(x, y)` is the transition cell; `previous` is `(location, x, y)` of the group's previous fields; L-TR2, L-TR3, L-TR5; `FormatError` for a location code of 0 or a target outside the map |
| `image_at(map, x, y)` | `int` | the cell image; the border image outside the map (L-MI5) |

The functions that take a map accept the dict `decode_map` returns. Map dict
keys:

- `size`, `bodySize`, `encryptedPrefixLength`;
- `centralDirectory`: `stringsOffset`, `mobNamesOffset`, `mobDataOffset`,
  `actionClassOffsets` (16), `specialsOffset`, `npcOffset`;
- `info`: `unknown00`, `unknown01`, `mapSize`, `unknown03`, `unknown04`,
  `encounterFrequency`, `tileset`, `randomMonsterTypes`,
  `maxRandomEncounters`, `borderImage`, `timePerStep` (u16), `healRate`,
  `combatStringIds` (37 ints);
- `cells`: `actionClass`, `action`, `image`, each `[y][x]`;
- `actions`: string class number to the class's pointer list in order, `None`
  for a null pointer and a record dict otherwise (so slot 0 is `None` in lab
  data);
- `npcs`: character dicts; `mobs`: `name` (the full stored string, selectors
  included), `sturdiness`, `combatRating`, `randomDamage`, `maxGroup`,
  `armorClass`, `fixedDamage`, `weaponType`, `type`, `portrait`;
- `strings`: every string of the map string table, as `str`.

Record dicts, by class (`newAction` is 0 when `newClass` is 253 or more):

| Class | Keys |
| --- | --- |
| 1 | `messages`, `newClass`, `newAction` |
| 3 | `visibleDistance`, `hitDistance`, `message`, `groups` (3 x `[monster, random_flag, size]`), `properName`, `friendly`, `immobile`, `npc`, `newClass`, `newAction` |
| 4 | `message`, `impassable`, `tile`, `newClass`, `newAction` |
| 5 | `newClass`, `newAction`, `items` (`[item, fixed, amount]` each), `cash` (`None` or `[fixed, amount]`) |
| 6 | `shop`, `message`, `newClass`, `newAction` |
| 10 | `relative`, `confirm`, `message`, `x`, `y` (signed bytes, -128 to 127), `location`, `newClass`, `newAction` |
| 11 | `message`, `newClass`, `newAction` |

`resolve_transition` reads `x` and `y` as unsigned (`& 0xFF`) when `relative`
is false (L-TR3).

### 2.7 `wlengine.rules` (SPEC-04)

`Rng(seed)` is the generator of LR-1 and LR-2: methods `next()`, `roll(n)`,
`rnd(n)`, `dice(n, sides)`, `d100()`, and the attribute or property `state`
(the 32-bit state, equal to the seed after seeding, or 0x6D2B79F5 for seed 0).
Functions that take `rng` take an `Rng` and must draw exactly the calls the
rule names, in order; the tests compare `rng.state` afterwards.

| Function | Returns | Rule |
| --- | --- | --- |
| `roll_attributes(rng)` | `[STR, IQ, LCK, SPD, AGL, CHA]` | LR-7 |
| `max_hp(strength, level)` | `int` | LR-8, LR-46 |
| `armour_class(agility, armour_bonus, evasion_level)` | `int` | LR-8 |
| `starting_money(luck)` | `int` | LR-9 |
| `read_skill_table(path)` | 36 x `[minimum_iq, cost, attribute_offset]` | LR-6 |
| `check_need(level, attribute, difficulty, tool=False)` | `int`, unclamped | LR-13 |
| `skill_check(rng, level, attribute, difficulty, tool=False)` | `{"need", "roll", "success"}`; `roll` is `None` when no draw is made | LR-13 |
| `pick_checker(candidates)` | slot or `None`; candidates are `{"slot", "cond", "level", "attribute"}` | LR-14 |
| `advance_clock(clock, minutes, seconds)` | `(clock, hours)`; `clock` is `{"day", "minute" (0 to 1439), "second"}`; `hours` lists the hours (0 to 23) whose minute 0 was reached, in order | LR-16, LR-17 |
| `xp_threshold(level)` | `int` | LR-45 |
| `level_after(level, xp)` | `int` | LR-45 |
| `buy_price(price, haggling)`, `sell_price(price, haggling)` | `int`; `haggling` is the best level, the function applies `min(5, ...)` | LR-53 |
| `pay(moneys, first_slot, price)` | new list of money per slot, or `None` when the party cannot pay | LR-20 |
| `monster_values(mob)` | `{"to_hit_base", "speed", "ac", "ranged", "xp"}`; `mob` is a map mob dict | LR-27 |
| `monster_hp(rng, sturdiness)` | `int` | SPEC-03 6.6, LR-26 |
| `monster_damage(rng, mob)` | `int` | LR-27 |
| `build_groups(rng, mobs, record)` | list of `{"monster" (1-based map monster index), "count", "band", "hp": [...]}` for groups with a count above 0 | LR-26, LR-28 |
| `ranged_need(level, agility, target_ac, band)` | `int` | LR-34 |
| `melee_need(level, agility, target_ac)` | `int` | LR-35 |
| `monster_need(combat_rating, member_ac, band)` | `int` (band 1 for melee) | LR-34, LR-35 |
| `flee_need(best_member_speed, best_monster_speed, command_level)` | `int` | LR-43 |
| `jam_chance(gunsmithing_level)` | `int` | LR-34 |
| `unarmed_attacks(grappling_level)` | `int` | LR-35 |
| `melee_damage_bonus(strength)` | `int` | LR-35 |
| `damage_member(hp, damage)` | `{"hp", "cond", "last_hp"}`; `last_hp` is `None` unless the member dropped | LR-40 |
| `speed_order(actors)` | the same actor dicts in acting order; members are `{"side": "party", "speed", "slot"}`, monsters `{"side": "monsters", "speed", "group", "index"}` | LR-35 |

The tests read "crosses a full hour" in LR-17 as "reaches minute 0 of an
hour". The reference log agrees: the step that reaches 23:00 before CP9
emits `natural_heal`.

### 2.8 `wlengine.labstate` (SPEC-04 LR-57)

| Function | Returns |
| --- | --- |
| `encode_labstate(state)` | `bytes`; cell changes written sorted by (location, y, x) |
| `decode_labstate(data)` | `state`; `FormatError` on a wrong magic or sum |

`state` keys: `steps`, `day`, `seconds`, `rng_state`, `cell_changes`
(`[location, x, y, class, action, image]` each).

### 2.9 `wlengine.scenario` (SPEC-05 section 13)

`compile(scenario_dir: str, out_dir: str) -> None` reads
`scenario_dir/scenario.json` and the files it lists and writes into the
existing directory `out_dir`: GAME1, LABTABLES.BIN, LABSTR.BIN, LABSKILL.BIN,
LABHOOKS.JSON, PARAGRAPHS.JSON, ALLHTDS1, ALLPICS1, IC0_9.WLF (10 sprites),
MASKS.WLF, COLORF.FNT, CURS, TITLE.PIC and END.CPA.

### 2.10 `wlengine.headless` and the command line (SPEC-06 sections 5 and 6)

`run(data_dir: str, script: dict, seed: int = None) -> list[dict]` runs a
script (the JSON object of SPEC-06 5.2) on a new game and returns the event
log: one dict per event with `seq`, `type` and the fields of SPEC-06 section 6.
`seed` overrides the script's seed. A save writes the GAME1 savegame block and
LABSTATE.BIN in `data_dir`; a load reads them. The exit codes of SPEC-06 5.1
map to exceptions from `wlengine.errors`:

| Exit code | Exception |
| --- | --- |
| 2: a `repeat_until` exceeded its `max` | `RepeatLimitError` |
| 3: a data error or a load failure | `FormatError` (or `ChecksumError`) |
| 4: a malformed script | `ScriptError` |

`python3 -m wlengine --headless --data DIR --script FILE [--seed N] --log OUT`
writes the same events as JSON Lines and exits with those codes.
`python3 -m wlengine --data DIR --render-frame` prints the first frame
(25 lines) and exits 0.

### 2.11 `wlengine.ui` (SPEC-06 sections 2 and 7)

`render_frame(data_dir: str) -> list[str]` starts a new game and returns the
first frame after the paragraph pop-up is closed: 25 strings of exactly 80
characters. It must not need a terminal or import `curses`.

### 2.12 `wlengine.errors`

| Class | Base |
| --- | --- |
| `FormatError` | `ValueError` |
| `ChecksumError` | `FormatError` |
| `ScriptError` | `Exception` |
| `RepeatLimitError` | `ScriptError` |

Every decoder and loader raises `FormatError` (or `ChecksumError`) for
malformed input, never another exception type.

## 3. Milestones

A test belongs to exactly one milestone group through the marker
`@pytest.mark.milestone("Mn")` (set per file as `pytestmark`).

| Group | File | Tests | Content | Oracle |
| --- | --- | --- | --- | --- |
| M1 | `test_m1_codecs.py` | 89 | rotating XOR (both modes), Huffman, vertical XOR | SPEC-01 vectors from `codecs_ref.py`, seeded random round trips through `codecs_ref.py` |
| M2 | `test_m2_containers.py` | 107 | LABTABLES, location resolution, savegame and character records, shop lists, msq blocks, tilesets, portraits and animation, sprites, font, cursors, title, ending, string tables, LABSTR | fixtures from `fixtures_gen.py` (seeds 19880101 and 20261022) and their manifests |
| M3 | `test_m3_maps.py` | 94 | map decoding field by field, loading through the tables, validation errors, lab-rule semantics of SPEC-03 section 9 | fixture maps and manifests |
| M4 | `test_m4_scenario.py` | 76 | scenario compiler output read back through the engine's loaders and through the reference readers | the scenario JSON |
| M5 | `test_m5_rules.py` | 82 | SPEC-04 rules: 38 rule tables (generator, characters, checks, time, experience, prices, payments, monsters, combat formulas, LABSTATE) and 44 engine behaviours (new game, steps and clock, bumps, rest, hooks, shop, recruit, the first fight for several seeds, locks, healer, save and load) | SPEC-04 formulas and worked examples, `rng-vectors.json`, SPEC-05 data |
| M6 | `test_m6_playable.py` | 55 | the walkthrough against the reference log (11 checkpoints, 11 log segments, the full log), the `expected` blocks for seeds 20261021 and 1 to 20, driver behaviour, the command line, the first frame | `walkthrough.json`, `walkthrough-reference-log.json`, SPEC-06 |
| | | 503 | | |

The milestones are cumulative in practice: M4 to M6 use the engine's own
compiled scenario, so they cannot pass before the compiler works, and the
M5 and M6 runs use the containers and maps of M2 and M3.

A milestone is passed when 100 % of its group passes in one run of the test
command. A skipped test counts as not passed. There are no expected failures.

## 4. How to run

From the project directory (the one holding `SPEC/`, `tests/`, `src/`):

```text
python3 -m pytest tests -q -p no:cacheprovider --junitxml=OUT.xml               all groups
python3 -m pytest tests -q -p no:cacheprovider --junitxml=OUT.xml --group M3    one group
```

`--group` accepts M1 to M6. The harness configuration uses one milestone entry
per group:

```toml
[project]
test_command = "{python} -m pytest -q -p no:cacheprovider --junitxml={junit} {select}"

[[milestones]]
name = "M1"
select = "tests --group M1"
# ... and the same for M2 to M6
```

Each failure message names the case and says what was expected and what came
back, for that case only: the first differing field, byte or event. The full
suite runs in under a second against an engine that implements nothing; with
a working engine, the M6 group replays the walkthrough 21 times.

The tests write only to the temporary directory pytest provides (the harness
scratch directory). Fixtures are generated at session start by running
`SPEC/reference/fixtures_gen.py` in a separate process; its manifest is kept
in a directory apart from the data files. The reference readers used by M4 run
in a separate process too (`tests/oracle_tool.py`).

## 5. What each oracle checks

- M1: every SPEC-01 vector (RX, RP, RP-N, RX-C, HU, HU-S, VX), the over-read
  offset, the error cases, and 8 seeded random cases per codec drawn from the
  sizes and alphabets of the `codecs_ref.py` self test. The encoders are
  checked by the reference decoder; rotating XOR encoding is checked byte for
  byte because SPEC-01 2.4 leaves the encoder no freedom.
- M2 and M3: each manifest field is compared on its own, so partial progress
  shows. A second fixture set (seed 20261022, same generator, different
  content) is compared as whole structures, so a single manifest copied into
  `src/` does not pass.
- M4: the expected structures are built from the scenario JSON with the SPEC-03
  lab encoder's own normalisation (`fixtures_gen.py`), NPC and party records per
  LR-8 and LR-55. These expected maps reproduce the block sizes and prefix
  lengths that SPEC-05 section 5.6 states.
- M5: rule tables compare with independent restatements of the SPEC-04 formulas
  in `tests/wl_support.py`. The first-fight tests (`tests/wl_combat_ref.py`)
  restate LR-26 to LR-30, LR-34 and LR-40 for the party at CP3; for seed
  20261021 they reproduce the reference log's encounter, surprise check and
  round 1 exactly. A consistency checker applies LR-33 to LR-46 to every event of
  the raider fight for seeds 1 to 5.
- M6: the checkpoint tests compare the whole snapshot with the reference log;
  the segment tests compare the events between checkpoints, ignoring `seq`, so
  one extra event early does not fail every later segment; the full-log test
  compares every event including `seq`. The seed tests check the `expected`
  blocks, which SPEC-05 states hold for any seed.

## 6. Rules

### 6.1 Integrity

- `tests/` and `SPEC/` are frozen at registration. A change is a dated
  PREREG-W1 addendum and resets the affected milestone's clock.
- The engine must compute its answers. While a test calls the engine, the
  engine must not open any file under `SPEC/reference/`, the reference log
  `SPEC/scenario/walkthrough-reference-log.json`, or the fixture manifest, and
  must not load a module from `SPEC/`. Source files under `src/` must not
  contain the names `codecs_ref`, `fixtures_gen`, `oracle_tool`, `wl_support`,
  `wl_combat_ref`, `_wl_oracle` or `reference-log` (also in comments). The
  tests enforce this with a source scan, an audit hook on `open`, and a check of
  `sys.modules`; a violation fails the test with a message naming the file.
- Reading the reference code as documentation is allowed, and porting its
  algorithms into `src/` is allowed (it is part of the spec). Section 8
  explains how porting is measured.

### 6.2 Definition of passed

A milestone is passed on the first test run in which every test of its group
passes. The PREREG-W1 readings use the junit XML of the harness runs.

## 7. Defects and open points found while writing the tests

- D1 (blocking, needs a fix before freeze). SPEC-05 section 11 and
  `scenario.json` put the string "A lab scenario for the clean-room engine." in
  LABSTR table 0 and require dictionary D for every LABSTR table, but D has no
  hyphen (0x2D). No compiler can satisfy both. Suggested fix: change the
  string to "A lab scenario for the clean room engine." in `scenario.json` and
  SPEC-05. The tests take their expected strings from `scenario.json`, so no
  test changes.
- Not tested, because the spec text leaves the outcome open: whether an `input`
  event precedes each `ignored` event after `won` or `gameover` (SPEC-06 5.1);
  which variant a 0x0A, 0x0C or 0x0E selector renders (SPEC-02 9.2 leaves it
  to the caller); the party panel's exact column layout (SPEC-06 2.4); the
  placeholder portrait colours (SPEC-05 section 4 names the colour as `4 + p`
  without saying whether `p` is the raw id); the fourth shop-list offset,
  `sharedLocations` and `mobSpriteMap` in the compiled Dry Fork tables.
- Read one way by the tests, stated here so the builder is not left guessing:
  a class 1, 3, 5, 6 or 10 cell with action byte 0 is an L-AC5 data error;
  reaching minute 0 of an hour counts as crossing it (LR-17); unknown savegame
  bytes are zero in every fixture, so both "preserve" (SPEC-02 4.5) and "write
  zero" (L-SG2) pass.

## 8. Adversarial review (PREREG-W1 section 7, questions 1 to 3)

### 8.1 Can a test be passed by memorising wastelib rather than by building?

Yes, for the decoding half, and even more directly by porting the lab's own
reference code. wastelib (MIT) decodes rotating XOR, Huffman, vertical XOR,
string tables, savegames, shop lists, tilesets, portraits, sprites, font,
cursors, title, ending and maps, so a faithful port covers most of M1, M2 and
the decoding tests of M3. `SPEC/reference/codecs_ref.py` and
`fixtures_gen.py` are closer still: while writing these tests, a throwaway
adapter outside the repository that wrapped those two files passed all of M1,
M2 and M3, and with the lab encoders behind a small compiler, all of M4. The
source scan rejected the adapter at once, because it imported the oracle;
a port that copies the code under other names would not be rejected.

wastelib has nothing for LABTABLES, LABSTR, LABSKILL, the lab hooks, the lab
rules, the scenario compiler, the headless driver or the front end, and the
reference files have no game logic. The lab-rule tests of M3, the compiler
checks of M4 against SPEC-05, all of M5 and all of M6 therefore need building.
Porting is permitted (MIT, and the reference code is part of the spec), so the
study does not forbid it; it measures it:

1. Transcript evidence. `runs/<id>/iterations.jsonl` logs every tool call with
   its path. Count `read_file` and `read_spec` calls on `SPEC/reference/*.py`
   per milestone, and the iteration at which each group first passes relative
   to those reads. The worklog entries around the first M1 to M3 passes say
   whether the builder derived or transcribed.
2. Code similarity. At each milestone pass, compare `src/` with
   `SPEC/reference/*.py` and with wastelib at commit `eb4ed4d` using a
   winnowing fingerprint (as MOSS does) over normalised tokens, and report the
   fraction of `src/` lines inside matched regions. Tell-tale identifiers:
   `rxor_decode_prefix`, `huff_decode`, `_huff_read_tree`, `BitReaderMSB`,
   `msqh_decode`, `strtab_decode` (lab reference); `decodeHuffman`,
   `BinaryReader`, `readUint8`, `GameMap`, `MapInfo`, `getAction` (wastelib,
   TypeScript idioms carried into Python).
3. Memory, not lookup. The sandbox denies network access, so wastelib can
   only arrive from the model's training data. Comments or worklog lines that
   cite wastelib file names or behaviour the spec does not state are counted
   as memory use.

The paper should read P1 and P2 (M1 to M3 inside two days) with this in mind:
those milestones measure how well the builder turns provided reference code
and prose into a package, not discovery of the formats.

### 8.2 Are the lab rules complete enough that a failure is unambiguous?

Mostly yes, after the points of section 7. Every M5 and M6 expectation was
derived from SPEC-04 to SPEC-06 and the scenario data, and where the reference
log covers the same ground (seed 20261021) the derived values match it: the
encounter hit points, the surprise check, round 1 of the first fight, the shop
prices, ammunition stacking, the sale, the equip, the recruit, the lock check
and its events, the healer, the key lock, the save and load. Points that
remain open are listed in section 7 and are not tested. One blocking defect
(D1) must be fixed before freeze. The tests that no adapter could exercise
without a real engine (custom scripts, seeds other than 20261021, the save
files, the driver errors, the command line and the frame) were checked by hand
against the map data and the rules.

### 8.3 Does the fixtures generator leak answers into test names or messages?

No. Test ids are vector names (RX-1, HU-3), map numbers, field names, seeds
and checkpoint names. Messages give the case and the first differing element
only; for bytes, the first differing offset and the two byte values; for logs,
one event. The manifest is written to its own directory, which the engine is
not allowed to open. The residual route is outside the tests: the builder can
run `fixtures_gen.py` itself and copy its output into `src/`. The second
fixture set (seed 20261022) makes a single copied manifest fail M2 and M3.
Copying both manifests is possible, since both seeds are visible in the tests,
and it is what the code-similarity measure of 8.1 is for: large literal tables
in `src/` stand out.
