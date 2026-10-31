# Review request, iteration 2

Run w1-2026-10-21; model deepseek-v41-flash-exl3; trigger: milestone passed: M3.

Reply by writing `review-reply-2.md` in /Users/dtinholt/wasteland-build/runs/w1-2026-10-21. The run is not paused; a reply is injected into the next iteration that starts after it appears.

## Test summary

- M1: 89/89 passed, 0 failed, 0 errors [PASS]
- M2: 107/107 passed, 0 failed, 0 errors [PASS]
- M3: 94/94 passed, 0 failed, 0 errors [PASS]
- M4: 0/76 passed, 76 failed, 0 errors [open]
- M5: 0/82 passed, 82 failed, 0 errors [open]
- M6: 0/55 passed, 55 failed, 0 errors [open]

First 10 of 213 failing tests:
* [M4] tests.test_m4_scenario::test_compiled_file_set
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-size]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-info]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-cells.image]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-cells.actionClass]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-cells.action]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-actions]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-npcs]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-mobs]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
* [M4] tests.test_m4_scenario::test_map_round_trip[0-strings]
    Failed: scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'
    scenario compile failed, so this check cannot run: cannot import wlengine.scenario (SPEC-07 API): ModuleNotFoundError: No module named 'wlengine.scenario'

## Worklog tail

[earlier entries omitted]
  3x(mob,flags),flags byte,tail), 4 MASK (msg, byte, tail), 5 LOOT (newClass+
  newAction always, then entries until 0xFF; 0xDE/0x5E u16 cash), 6 SHOP (shop,
  msg, tail), 10 TRANSITION (flags,x i8,y i8,location,tail), 11 BLOCKED (msg,tail).
  Tail: u8 newClass; if <253 read newAction else 0.
- NPCs: at npcOffset, only if u16 there == 0; pointers until pos >= smallest;
  each -> `containers.decode_character(body[p:p+0x100])`.
- mobs: `numMobs = (stringsOffset - mobDataOffset)//8`, NUL-terminated names from
  mobNamesOffset, 8-byte records; name is the full stored string (latin-1).
- strings: `strings.decode_table(body, stringsOffset)` -> latin-1 str list.
- `load_map(data_dir, location)`: `containers.read_tables(LABTABLES.BIN)`,
  `containers.resolve_location` -> (loc, disk, index); disk 2 -> GAME1 with
  `mapOffsets[index]`, disk 1 -> GAME2 with `mapOffsets[20+index]`; size =
  `mapSizes[loc]`, tmo = `tileMapOffsets[loc]`.
- `record_at`: a==0 -> None unless class in (1,3,5,6,10) -> FormatError; no table
  -> None; a >= len(table) -> FormatError; table[a] None for NEEDS_RECORD ->
  FormatError.
- `is_passable`: OOB False; 0 True; 11 False; 4 -> not record.impassable (None ->
  True); 1,3,5,6,10 True; reserved True.
- `apply_tail`: nc >= 253 -> None; nc >= 16 -> None; else [nc, newAction].
- `resolve_transition`: t==255 -> previous tuple; 128..252 -> sharedLocations[t-128];
  `containers.resolve_location` (FormatError on code 0); relative -> x+rec.x, y+rec.y
  (signed), absolute -> rec.x & 0xFF, rec.y & 0xFF; validate against
  `tables["mapSizes"][loc]` -> FormatError (L-TR5). Returns a list [loc, tx, ty].
- `image_at`: OOB -> `info["borderImage"]`, else cells.image[y][x].

### Next step: M4 (scenario compiler) — 0/76, the big one
`wlengine.scenario.compile(scenario_dir, out_dir)` must write GAME1 (4 maps,
savegame, 3 shop lists), LABTABLES.BIN, LABSTR.BIN, LABSKILL.BIN, LABHOOKS.JSON,
PARAGRAPHS.JSON, ALLHTDS1, ALLPICS1 + placeholder IC0_9.WLF, MASKS.WLF,
COLORF.FNT, CURS, TITLE.PIC, END.CPA.

Facts gathered this iteration (do not re-read):
- `tests/oracle_tool.py::expected_from_json` is the exact expected-value oracle;
  read it again when implementing (it shows how each JSON maps to bytes).
- scenario.json: locations 0..3 sizes [64,32,32,32], location_code 128..131,
  map_index 0..3, all GAME1; start {location 1, x 15, y 20, hour 8, seed 20261021}.
- LABTABLES expected: mapCounts [4,0], shopListCounts [3,0], savegameSize 0x1206,
  locationMapping [0x80,0x81,0x82,0x83,0,0], mapSizes [64,32,32,32,0,0],
  savegameOffsets[1] = 0xFFFFFFFF. GAME1 length = savegameOffset + 0x1206 + 3*766.
- Map JSONs already contain `action_class`, `action_value`, `tiles` (tile ids,
  image = id+10), `records` (per class, slot i+1), `strings`, `mobs`, `npcs`,
  `info`. So the compiler mostly re-encodes these with the SPEC-03 lab encoder
  (mirror `fixtures_gen.build_map`): body order L-EN1 = class map, action map,
  central dir, map info, tables 0-7, table 15, NPC section, tables 8-14, specials
  (0), monster names, monster data, strings; prefix = body[:stringsOffset]
  encrypted, must pass `codecs.rotating_xor_prefix_is_unambiguous`; tile map =
  u32(S*S) + u32(0) + `huffman.encode(tiles)`; block = b"msq0" + data + tsec.
  Every monster portrait byte is 1 (keeps the prefix's last byte non-zero).
- LABSTR.BIN: magic "WLLABST1", u16 tableCount, u16 zero, u32 tableOffset[n],
  u32 tableSize[n], then tables. 6 tables; table 1 = UI strings by id with
  {name}->0x0B, {num}->0x0F; table 2 = [""] + skill names by id + item names by
  id; tables 0,3,4,5 straight from scenario.json labstr_tables. Pad each to a
  multiple of 4 with "" (L-ST1). Use `strings.encode_table(DICT, ...)`.
- LABSKILL.BIN: 36 entries of 2 bytes: entry0 = (iq_req<<3)|cost, attr_offset;
  then each skill's `labskill_bytes`.
- LABHOOKS.JSON / PARAGRAPHS.JSON: verbatim copies of hooks.json / paragraphs.json.
- ALLHTDS1: one tileset, 32 tiles, each 16x16 4bpp: `codecs.vertical_xor_encode(
  graphics.pack4(tile), 8)` per tile, wrapped in `huffman.encode_msq(raw, 0)`.
  Placeholder art: tile t filled with color t%16, 1px border (t+8)%16.
- ALLPICS1: 4 portraits, raw ids 1..4, 96x84 4bpp; placeholder fill 4+p with a
  centred 48x42 rect of 15; one update XORs 8 bytes at offset 2000 with 0xFF;
  script [(20,0),(20,0)]. Each portrait = msq(vxor(base,48)) + msq(anim).
  portraitIndices1 = [1,2,3,4] + [0x80]*76; portraitOffsets1 cumulative.
- Savegame: build from party.json + start (see oracle_tool expected_from_json
  lines ~140-160): groups[0] order 1..n, x/y/map = start, prev 0; viewport = start
  x/y; currentMembers = n; currentParty 0; currentMap = start location;
  totalMembers n; extraGroups 0; minute 0; hour = start hour; combatScrollSpeed 0;
  serial 0; characters = party + empty*3. Use `containers.encode_savegame`.
- Shops: 3 lists of 94 records; record i = item id i+1 from items.json (price,
  stock from shops.json stock map, type = type_byte>>3, lowFlags = type_byte&7,
  capacity, skill, damage, ammo), else 8 zero bytes. Header constant
  `containers.SHOP_HEADER`. Use `containers.encode_shop_list`.
- Also needed for M4: `rules.read_skill_table(path)` -> [[b0>>3, b0&7, b1], ...]
  (36 entries) — a tiny function in a new `src/wlengine/rules.py`.
- `graphics.read_tilesets`, `graphics.read_portrait`, `graphics.portrait_offset`,
  `graphics.read_sprites`, `graphics.read_font`, `graphics.read_cursors`,
  `graphics.read_title`, `graphics.read_ending` already exist from M2.
- `strings.read_labstr` already exists from M2.
- Reminder: src/ must never contain the strings codecs_ref, fixtures_gen,
  oracle_tool, wl_support, wl_combat_ref, _wl_oracle, reference-log.
- After M4: M5 needs `wlengine.rules` (SPEC-04) and M6 needs `wlengine.headless`
  + `wlengine.ui` (SPEC-06).

[harness] iter 2 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 0->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; files changed: src/wlengine/maps.py


## Diff since last review (27d2a77fd0..0f1d6d7f8b)

```diff
 WORKLOG.md           | 104 ++++++++++++
 src/wlengine/maps.py | 445 +++++++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 549 insertions(+)

diff --git a/WORKLOG.md b/WORKLOG.md
index e8535e6..646d1c7 100644
--- a/WORKLOG.md
+++ b/WORKLOG.md
@@ -133,3 +133,107 @@ Then run `run_tests M3` and fix. After M3, M4 needs the scenario compiler
 (SPEC-05 section 13) — much bigger; M5/M6 need rules/headless/ui.
 
 [harness] iter 1 ended (end_iteration); tests: M1 0->89/89; M2 0->107/107; M3 0->0/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; files changed: src/wlengine/__init__.py, src/wlengine/codecs.py, src/wlengine/containers.py, src/wlengine/errors.py, src/wlengine/graphics.py, src/wlengine/huffman.py, src/wlengine/strings.py
+
+### iter 2 note (2026-10-21T17:30:16-05:00)
+### Iter 2 result: M3 done (94/94 PASS)
+
+Implemented `src/wlengine/maps.py` (446 lines) and M3 went 0/94 -> 94/94.
+Files changed: src/wlengine/maps.py (new).
+
+What worked (port of SPEC/reference/fixtures_gen.py `map_decode` under new names):
+- `decode_map(game, offset, map_size, tile_map_offset)`: validate `msq`+0x30/0x31
+  header, `body_size = tmo - 7`, `codecs.rotating_xor_decode_prefix(game,
+  body_size, offset+4)`, u32 at `offset+tmo` must == size*size, `huffman.decode(
+  game, tsize, t+8)`. Body layout: class map `body[:n//2]` (high nibble = even x),
+  action map `body[n//2:n//2+n]`, central directory 42 bytes at `n//2+n`
+  (stringsOffset/mobNamesOffset/mobDataOffset u16, actionClassOffsets u16[16],
+  specialsOffset @0x26, npcOffset @0x28), map info 50 bytes at cd+42.
+- L-EN2 check: `plen != stringsOffset` -> FormatError. Also validate map-info
+  +0x02 == map_size (this is what makes `test_decode_map_wrong_size` pass).
+- Pointer tables: read u16 until pos >= smallest non-zero pointer seen; 0 -> None,
+  else `decode_record(cls, body, p)`. Keys are `str(c)`.
+- Records: 1 PRINT (msgs until bit7, then tail), 3/15 ENCOUNTER (vis,hit,msg,
+  3x(mob,flags),flags byte,tail), 4 MASK (msg, byte, tail), 5 LOOT (newClass+
+  newAction always, then entries until 0xFF; 0xDE/0x5E u16 cash), 6 SHOP (shop,
+  msg, tail), 10 TRANSITION (flags,x i8,y i8,location,tail), 11 BLOCKED (msg,tail).
+  Tail: u8 newClass; if <253 read newAction else 0.
+- NPCs: at npcOffset, only if u16 there == 0; pointers until pos >= smallest;
+  each -> `containers.decode_character(body[p:p+0x100])`.
+- mobs: `numMobs = (stringsOffset - mobDataOffset)//8`, NUL-terminated names from
+  mobNamesOffset, 8-byte records; name is the full stored string (latin-1).
+- strings: `strings.decode_table(body, stringsOffset)` -> latin-1 str list.
+- `load_map(data_dir, location)`: `containers.read_tables(LABTABLES.BIN)`,
+  `containers.resolve_location` -> (loc, disk, index); disk 2 -> GAME1 with
+  `mapOffsets[index]`, disk 1 -> GAME2 with `mapOffsets[20+index]`; size =
+  `mapSizes[loc]`, tmo = `tileMapOffsets[loc]`.
+- `record_at`: a==0 -> None unless class in (1,3,5,6,10) -> FormatError; no table
+  -> None; a >= len(table) -> FormatError; table[a] None for NEEDS_RECORD ->
+  FormatError.
+- `is_passable`: OOB False; 0 True; 11 False; 4 -> not record.impassable (None ->
+  True); 1,3,5,6,10 True; reserved True.
+- `apply_tail`: nc >= 253 -> None; nc >= 16 -> None; else [nc, newAction].
+- `resolve_transition`: t==255 -> previous tuple; 128..252 -> sharedLocations[t-128];
+  `containers.resolve_location` (FormatError on code 0); relative -> x+rec.x, y+rec.y
+  (signed), absolute -> rec.x & 0xFF, rec.y & 0xFF; validate against
+  `tables["mapSizes"][loc]` -> FormatError (L-TR5). Returns a list [loc, tx, ty].
+- `image_at`: OOB -> `info["borderImage"]`, else cells.image[y][x].
+
+### Next step: M4 (scenario compiler) — 0/76, the big one
+`wlengine.scenario.compile(scenario_dir, out_dir)` must write GAME1 (4 maps,
+savegame, 3 shop lists), LABTABLES.BIN, LABSTR.BIN, LABSKILL.BIN, LABHOOKS.JSON,
+PARAGRAPHS.JSON, ALLHTDS1, ALLPICS1 + placeholder IC0_9.WLF, MASKS.WLF,
+COLORF.FNT, CURS, TITLE.PIC, END.CPA.
+
+Facts gathered this iteration (do not re-read):
+- `tests/oracle_tool.py::expected_from_json` is the exact expected-value oracle;
+  read it again when implementing (it shows how each JSON maps to bytes).
+- scenario.json: locations 0..3 sizes [64,32,32,32], location_code 128..131,
+  map_index 0..3, all GAME1; start {location 1, x 15, y 20, hour 8, seed 20261021}.
+- LABTABLES expected: mapCounts [4,0], shopListCounts [3,0], savegameSize 0x1206,
+  locationMapping [0x80,0x81,0x82,0x83,0,0], mapSizes [64,32,32,32,0,0],
+  savegameOffsets[1] = 0xFFFFFFFF. GAME1 length = savegameOffset + 0x1206 + 3*766.
+- Map JSONs already contain `action_class`, `action_value`, `tiles` (tile ids,
+  image = id+10), `records` (per class, slot i+1), `strings`, `mobs`, `npcs`,
+  `info`. So the compiler mostly re-encodes these with the SPEC-03 lab encoder
+  (mirror `fixtures_gen.build_map`): body order L-EN1 = class map, action map,
+  central dir, map info, tables 0-7, table 15, NPC section, tables 8-14, specials
+  (0), monster names, monster data, strings; prefix = body[:stringsOffset]
+  encrypted, must pass `codecs.rotating_xor_prefix_is_unambiguous`; tile map =
+  u32(S*S) + u32(0) + `huffman.encode(tiles)`; block = b"msq0" + data + tsec.
+  Every monster portrait byte is 1 (keeps the prefix's last byte non-zero).
+- LABSTR.BIN: magic "WLLABST1", u16 tableCount, u16 zero, u32 tableOffset[n],
+  u32 tableSize[n], then tables. 6 tables; table 1 = UI strings by id with
+  {name}->0x0B, {num}->0x0F; table 2 = [""] + skill names by id + item names by
+  id; tables 0,3,4,5 straight from scenario.json labstr_tables. Pad each to a
+  multiple of 4 with "" (L-ST1). Use `strings.encode_table(DICT, ...)`.
+- LABSKILL.BIN: 36 entries of 2 bytes: entry0 = (iq_req<<3)|cost, attr_offset;
+  then each skill's `labskill_bytes`.
+- LABHOOKS.JSON / PARAGRAPHS.JSON: verbatim copies of hooks.json / paragraphs.json.
+- ALLHTDS1: one tileset, 32 tiles, each 16x16 4bpp: `codecs.vertical_xor_encode(
+  graphics.pack4(tile), 8)` per tile, wrapped in `huffman.encode_msq(raw, 0)`.
+  Placeholder art: tile t filled with color t%16, 1px border (t+8)%16.
+- ALLPICS1: 4 portraits, raw ids 1..4, 96x84 4bpp; placeholder fill 4+p with a
+  centred 48x42 rect of 15; one update XORs 8 bytes at offset 2000 with 0xFF;
+  script [(20,0),(20,0)]. Each portrait = msq(vxor(base,48)) + msq(anim).
+  portraitIndices1 = [1,2,3,4] + [0x80]*76; portraitOffsets1 cumulative.
+- Savegame: build from party.json + start (see oracle_tool expected_from_json
+  lines ~140-160): groups[0] order 1..n, x/y/map = start, prev 0; viewport = start
+  x/y; currentMembers = n; currentParty 0; currentMap = start location;
+  totalMembers n; extraGroups 0; minute 0; hour = start hour; combatScrollSpeed 0;
+  serial 0; characters = party + empty*3. Use `containers.encode_savegame`.
+- Shops: 3 lists of 94 records; record i = item id i+1 from items.json (price,
+  stock from shops.json stock map, type = type_byte>>3, lowFlags = type_byte&7,
+  capacity, skill, damage, ammo), else 8 zero bytes. Header constant
+  `containers.SHOP_HEADER`. Use `containers.encode_shop_list`.
+- Also needed for M4: `rules.read_skill_table(path)` -> [[b0>>3, b0&7, b1], ...]
+  (36 entries) — a tiny function in a new `src/wlengine/rules.py`.
+- `graphics.read_tilesets`, `graphics.read_portrait`, `graphics.portrait_offset`,
+  `graphics.read_sprites`, `graphics.read_font`, `graphics.read_cursors`,
+  `graphics.read_title`, `graphics.read_ending` already exist from M2.
+- `strings.read_labstr` already exists from M2.
+- Reminder: src/ must never contain the strings codecs_ref, fixtures_gen,
+  oracle_tool, wl_support, wl_combat_ref, _wl_oracle, reference-log.
+- After M4: M5 needs `wlengine.rules` (SPEC-04) and M6 needs `wlengine.headless`
+  + `wlengine.ui` (SPEC-06).
+
+[harness] iter 2 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 0->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; files changed: src/wlengine/maps.py
diff --git a/src/wlengine/maps.py b/src/wlengine/maps.py
new file mode 100644
index 0000000..cb361be
--- /dev/null
+++ b/src/wlengine/maps.py
@@ -0,0 +1,445 @@
+"""Map blocks (SPEC-03).
+
+A map block lives inside GAME1 or GAME2: an ``msq`` header, a rotating-XOR
+encrypted prefix followed by plain bytes (the map-data body), then the Huffman
+coded tile map.  ``decode_map`` reads one block; ``load_map`` finds one through
+LABTABLES.BIN (SPEC-02 section 3.4).
+
+The rest of the module implements the lab rules of SPEC-03 section 9 on the
+decoded dict: ``record_at``, ``is_passable``, ``apply_tail``,
+``resolve_transition`` and ``image_at``.
+"""
+
+from __future__ import annotations
+
+from . import codecs, containers, huffman, strings
+from .errors import FormatError
+
+# Classes that need a record: a null pointer or an out-of-range action byte is
+# a data error for these (L-AC5).
+NEEDS_RECORD = (1, 3, 5, 6, 10)
+
+# Classes the lab defines; everything else is reserved (L-AC1).
+LAB_CLASSES = (0, 1, 3, 4, 5, 6, 10, 11)
+
+# Map-info field order after the five leading bytes (SPEC-03 5.5).
+MAPINFO_FIELDS = ("encounterFrequency", "tileset", "randomMonsterTypes",
+                  "maxRandomEncounters", "borderImage")
+
+CD_SIZE = 42
+MAPINFO_SIZE = 50
+
+
+def _r16(b: bytes, o: int) -> int:
+    if o < 0 or o + 2 > len(b):
+        raise FormatError("map: u16 at offset %d runs past the body" % o)
+    return int.from_bytes(b[o:o + 2], "little")
+
+
+def _r32(b: bytes, o: int) -> int:
+    if o < 0 or o + 4 > len(b):
+        raise FormatError("map: u32 at offset %d runs past the input" % o)
+    return int.from_bytes(b[o:o + 4], "little")
+
+
+def _i8(v: int) -> int:
+    return v - 256 if v >= 128 else v
+
+
+# ---------------------------------------------------------------------------
+# Record decoding (SPEC-03 section 8)
+# ---------------------------------------------------------------------------
+
+def _read_tail(b: bytes, o: int, r: dict) -> int:
+    """Common tail (8.3): u8 newActionClass, u8 newAction when < 253."""
+    if o >= len(b):
+        raise FormatError("map: record tail runs past the body")
+    nc = b[o]
+    o += 1
+    if nc < 253:
+        if o >= len(b):
+            raise FormatError("map: record tail runs past the body")
+        r["newClass"], r["newAction"] = nc, b[o]
+        o += 1
+    else:
+        r["newClass"], r["newAction"] = nc, 0
+    return o
+
+
+def decode_record(cls: int, b: bytes, o: int) -> dict:
+    """Decode one action record of class ``cls`` at body offset ``o``."""
+    if o < 0 or o >= len(b):
+        raise FormatError("map: record offset %d outside the body" % o)
+    r: dict = {}
+    if cls == 1:  # PRINT (8.4)
+        msgs = []
+        while True:
+            if o >= len(b):
+                raise FormatError("map: PRINT record runs past the body")
+            m = b[o]
+            o += 1
+            msgs.append(m & 0x7F)
+            if m & 0x80:
+                break
+        r["messages"] = msgs
+        _read_tail(b, o, r)
+    elif cls == 3 or cls == 15:  # FIXED_ENCOUNTER / RANDOM_ENCOUNTER (8.5)
+        if o + 10 > len(b):
+            raise FormatError("map: encounter record runs past the body")
+        r["visibleDistance"], r["hitDistance"], r["message"] = b[o], b[o + 1], b[o + 2]
+        o += 3
+        groups = []
+        for _ in range(3):
+            groups.append([b[o], bool(b[o + 1] & 0x80), b[o + 1] & 0x7F])
+            o += 2
+        r["groups"] = groups
+        f = b[o]
+        o += 1
+        r.update({"properName": f & 1, "friendly": (f >> 1) & 1,
+                  "immobile": (f >> 2) & 1, "npc": f >> 4})
+        _read_tail(b, o, r)
+    elif cls == 4:  # MASK (8.7)
+        if o + 2 > len(b):
+            raise FormatError("map: MASK record runs past the body")
+        r["message"], r["impassable"], r["tile"] = b[o], bool(b[o + 1] & 0x80), b[o + 1] & 0x7F
+        _read_tail(b, o + 2, r)
+    elif cls == 5:  # LOOT (8.8, wllib layout)
+        if o + 2 > len(b):
+            raise FormatError("map: LOOT record runs past the body")
+        r["newClass"], r["newAction"] = b[o], b[o + 1]
+        o += 2
+        r["items"], r["cash"] = [], None
+        while True:
+            if o >= len(b):
+                raise FormatError("map: LOOT record has no 0xFF terminator")
+            v = b[o]
+            if v == 0xFF:
+                break
+            if v in (0xDE, 0x5E):
+                if o + 3 > len(b):
+                    raise FormatError("map: LOOT cash entry runs past the body")
+                r["cash"] = [v == 0xDE, _r16(b, o + 1)]
+                o += 3
+            else:
+                if o + 2 > len(b):
+                    raise FormatError("map: LOOT item entry runs past the body")
+                r["items"].append([v & 0x7F, bool(v & 0x80), b[o + 1]])
+                o += 2
+    elif cls == 6:  # SHOP (lab layout, 9.4)
+        if o + 2 > len(b):
+            raise FormatError("map: SHOP record runs past the body")
+        r["shop"], r["message"] = b[o], b[o + 1]
+        _read_tail(b, o + 2, r)
+    elif cls == 10:  # TRANSITION (8.9)
+        if o + 4 > len(b):
+            raise FormatError("map: TRANSITION record runs past the body")
+        f = b[o]
+        r.update({"relative": bool(f & 0x80), "confirm": bool(f & 0x40),
+                  "message": f & 0x3F, "x": _i8(b[o + 1]), "y": _i8(b[o + 2]),
+                  "location": b[o + 3]})
+        _read_tail(b, o + 4, r)
+    elif cls == 11:  # BLOCKED (8.10)
+        if o + 1 > len(b):
+            raise FormatError("map: BLOCKED record runs past the body")
+        r["message"] = b[o]
+        _read_tail(b, o + 1, r)
+    else:
+        raise FormatError("map: class %d has no record layout" % cls)
+    return r
+
+
+# ---------------------------------------------------------------------------
+# Block decoding (SPEC-03 sections 3 to 7)
+# ---------------------------------------------------------------------------
+
+def _decode_pointer_table(body: bytes, start: int, cls: int) -> list:
+    """Pointer list at ``start`` (SPEC-03 6.2), records decoded per class.
+
+    Pointers are read until the read position reaches the smallest non-zero
+    pointer seen so far (the wastelib rule); lab data keeps pointers ascending
+    so the wllib rule agrees.
+    """
+    ptrs = []
+    pos = start
+    end_ptr = None
+    while end_ptr is None or pos < end_ptr:
+        p = _r16(body, pos)
+        ptrs.append(p)
+        pos += 2
+        if p and (end_ptr is None or p < end_ptr):
+            end_ptr = p
+    out = []
+    for p in ptrs:
+        if p == 0:
+            out.append(None)
+        else:
+            if p >= len(body):
+                raise FormatError("map: action pointer %d outside the body" % p)
+            out.append(decode_record(cls, body, p))
+    return out
+
+
+def decode_map(game: bytes, offset: int, map_size: int, tile_map_offset: int) -> dict:
+    """Decode the map block at ``offset`` (SPEC-03 sections 3 to 7)."""
+    if offset < 0 or offset + 4 > len(game):
+        raise FormatError("map: block header runs past the end of the file")
+    if game[offset:offset + 3] != b"msq" or game[offset + 3] not in (0x30, 0x31):
+        raise FormatError("map: bad block header %s"
+                          % bytes(game[offset:offset + 4]).hex(" ").upper())
+    if map_size not in (32, 64):
+        raise FormatError("map: unsupported map size %d" % map_size)
+    if tile_map_offset < 7:
+        raise FormatError("map: tile-map offset %d is too small" % tile_map_offset)
+
+    body_size = tile_map_offset - 7
+    body, plen = codecs.rotating_xor_decode_prefix(game, body_size, offset + 4)
+
+    t = offset + tile_map_offset
+    tsize = _r32(game, t)
+    if tsize != map_size * map_size:
+        raise FormatError("map: tile-map size %d != %d" % (tsize, map_size * map_size))
+    tiles, _end = huffman.decode(game, tsize, t + 8)
+
+    n = map_size * map_size
+    cm = body[:n // 2]
+    am = body[n // 2:n // 2 + n]
+    if len(cm) < n // 2 or len(am) < n:
+        raise FormatError("map: body is too short for a %d x %d map" % (map_size, map_size))
+    cdo = n // 2 + n
+    if cdo + CD_SIZE + MAPINFO_SIZE > len(body):
+        raise FormatError("map: central directory or map info runs past the body")
+    cd = body[cdo:cdo + CD_SIZE]
+    sd = {
+        "stringsOffset": _r16(cd, 0),
+        "mobNamesOffset": _r16(cd, 2),
+        "mobDataOffset": _r16(cd, 4),
+        "actionClassOffsets": [_r16(cd, 6 + 2 * i) for i in range(16)],
+        "specialsOffset": _r16(cd, 0x26),
+        "npcOffset": _r16(cd, 0x28),
+    }
+    for name in ("stringsOffset", "mobNamesOffset", "mobDataOffset", "specialsOffset", "npcOffset"):
+        v = sd[name]
+        if v and v >= len(body):
+            raise FormatError("map: central-directory %s %d outside the body" % (name, v))
+    for c, v in enumerate(sd["actionClassOffsets"]):
+        if v and v >= len(body):
+            raise FormatError("map: action-class offset %d (class %d) outside the body" % (v, c))
+
+    info = _decode_mapinfo(body[cdo + CD_SIZE:cdo + CD_SIZE + MAPINFO_SIZE])
+    if info["mapSize"] != map_size:
+        raise FormatError("map: map info size %d != %d" % (info["mapSize"], map_size))
+
+    # L-EN2: in lab data the encrypted prefix ends exactly at stringsOffset.
+    if plen != sd["stringsOffset"]:
+        raise FormatError("map: encrypted prefix ends at %d, stringsOffset is %d (L-EN2)"
+                          % (plen, sd["stringsOffset"]))
+
+    cls = [[(cm[(y * map_size + x) >> 1] >> 4) if x % 2 == 0
+            else (cm[(y * map_size + x) >> 1] & 0x0F)
+            for x in range(map_size)] for y in range(map_size)]
+    act = [list(am[y * map_size:(y + 1) * map_size]) for y in range(map_size)]
+    img = [list(tiles[y * map_size:(y + 1) * map_size]) for y in range(map_size)]
+
+    actions = {}
+    for c in range(16):
+        o = sd["actionClassOffsets"][c]
+        if o == 0:
+            continue
+        actions[str(c)] = _decode_pointer_table(body, o, c)
+
+    npcs = []
+    o = sd["npcOffset"]
+    if o and _r16(body, o) == 0:
+        pos, lo, ptrs = o + 2, None, []
+        while lo is None or pos < lo:
+            p = _r16(body, pos)
+            ptrs.append(p)
+            pos += 2
+            lo = p if lo is None or p < lo else lo
+        for p in ptrs:
+            if p + 0x100 > len(body):
+                raise FormatError("map: NPC pointer %d outside the body" % p)
+            npcs.append(containers.decode_character(body[p:p + 0x100]))
+
+    nm = (sd["stringsOffset"] - sd["mobDataOffset"]) // 8
+    names = []
+    p = sd["mobNamesOffset"]
+    for _ in range(nm):
+        e = body.find(b"\x00", p)
+        if e < 0:
+            raise FormatError("map: monster name %d is not NUL-terminated" % len(names))
+        names.append(body[p:e])
+        p = e + 1
+    mobs = []
+    for i in range(nm):
+        o = sd["mobDataOffset"] + 8 * i
+        if o + 8 > len(body):
+            raise FormatError("map: monster data runs past the body")
+        mobs.append(_decode_mob(body[o:o + 8], names[i]))
+
+    decoded = strings.decode_table(body, sd["stringsOffset"])
+    return {
+        "size": map_size,
+        "bodySize": body_size,
+        "encryptedPrefixLength": plen,
+        "centralDirectory": sd,
+        "info": info,
+        "cells": {"actionClass": cls, "action": act, "image": img},
+        "actions": actions,
+        "npcs": npcs,
+        "mobs": mobs,
+        "strings": [s.decode("latin-1") for s in decoded],
+    }
+
+
+def _decode_mapinfo(b: bytes) -> dict:
+    if len(b) < MAPINFO_SIZE:
+        raise FormatError("map: map-info block is shorter than 50 bytes")
+    d = {"unknown00": b[0], "unknown01": b[1], "mapSize": b[2],
+         "unknown03": b[3], "unknown04": b[4]}
+    for i, k in enumerate(MAPINFO_FIELDS):
+        d[k] = b[5 + i]
+    d["timePerStep"] = _r16(b, 0x0A)
+    d["healRate"] = b[0x0C]
+    d["combatStringIds"] = list(b[0x0D:0x32])
+    return d
+
+
+def _decode_mob(b: bytes, name: bytes) -> dict:
+    return {"name": name.decode("latin-1"), "sturdiness": _r16(b, 0),
+            "combatRating": b[2], "randomDamage": b[3], "maxGroup": b[4] >> 4,
+            "armorClass": b[4] & 15, "fixedDamage": b[5] >> 4,
+            "weaponType": b[5] & 15, "type": b[6], "portrait": b[7]}
+
+
+# ---------------------------------------------------------------------------
+# Loading through the tables (SPEC-02 3.4)
+# ---------------------------------------------------------------------------
+
+def load_map(data_dir: str, location: int) -> dict:
+    """Load the map for ``location`` through LABTABLES.BIN and GAME1/GAME2."""
+    import os
+
+    tables = containers.read_tables(os.path.join(data_dir, "LABTABLES.BIN"))
+    loc, disk, index = containers.resolve_location(tables, location)
+    if disk == 2:
+        name, off_index = "GAME1", index
+    elif disk == 1:
+        name, off_index = "GAME2", 20 + index
+    else:
+        raise FormatError("map: location %d has an invalid disk code %d" % (location, disk))
+    with open(os.path.join(data_dir, name), "rb") as fh:
+        game = fh.read()
+    offsets = tables["mapOffsets"]
+    if off_index >= len(offsets):
+        raise FormatError("map: map index %d is outside mapOffsets" % off_index)
+    offset = offsets[off_index]
+    sizes = tables["mapSizes"]
+    if loc >= len(sizes):
+        raise FormatError("map: location %d is outside mapSizes" % loc)
+    size = sizes[loc]
+    tmos = tables["tileMapOffsets"]
+    if loc >= len(tmos):
+        raise FormatError("map: location %d is outside tileMapOffsets" % loc)
+    return decode_map(game, offset, size, tmos[loc])
+
+
+# ---------------------------------------------------------------------------
+# Lab-rule semantics (SPEC-03 section 9)
+# ---------------------------------------------------------------------------
+
+def record_at(map: dict, x: int, y: int):
+    """The record for cell ``(x, y)``, or ``None`` (L-AC2, L-AC3, L-AC5)."""
+    size = map["size"]
+    if not (0 <= x < size and 0 <= y < size):
+        raise FormatError("map: cell (%d, %d) outside the %d x %d map" % (x, y, size, size))
+    cls = map["cells"]["actionClass"][y][x]
+    a = map["cells"]["action"][y][x]
+    if a == 0:
+        if cls in NEEDS_RECORD:
+            raise FormatError("map: class %d cell (%d, %d) has action byte 0 (L-AC5)"
+                              % (cls, x, y))
+        return None
+    table = map["actions"].get(str(cls))
+    if table is None:
+        return None
+    if a >= len(table):
+        raise FormatError("map: class %d cell (%d, %d) has action byte %d beyond the "
+                          "pointer list (%d entries) (L-AC5)" % (cls, x, y, a, len(table)))
+    rec = table[a]
+    if rec is None and cls in NEEDS_RECORD:
+        raise FormatError("map: class %d cell (%d, %d) points at a null record (L-AC5)"
+                          % (cls, x, y))
+    return rec
+
+
+def is_passable(map: dict, x: int, y: int) -> bool:
+    """Whether the party may step onto ``(x, y)`` (9.1, 9.6, L-MV1, L-MV2)."""
+    size = map["size"]
+    if not (0 <= x < size and 0 <= y < size):
+        return False
+    cls = map["cells"]["actionClass"][y][x]
+    if cls == 0:
+        return True
+    if cls == 11:
+        return False
+    if cls == 4:
+        rec = record_at(map, x, y)
+        return True if rec is None else not rec["impassable"]
+    if cls in (1, 3, 5, 6, 10):
+        return True
+    return True  # reserved classes are walkable (L-AC1)
+
+
+def apply_tail(record):
+    """``(newClass, newAction)`` for a record tail, or ``None`` (L-TL1)."""
+    nc = record.get("newClass", 255)
+    if nc >= 253:
+        return None
+    if nc >= 16:
+        return None
+    return [nc, record.get("newAction", 0)]
+
+
+def resolve_transition(tables: dict, record: dict, x: int, y: int, previous):
+    """Resolve a TRANSITION record to ``(location, x, y)`` (L-TR2, L-TR3, L-TR5)."""
+    t = record["location"]
+    if t == 255:
+        return (previous[0], previous[1], previous[2])
+    if 128 <= t <= 252:
+        shared = tables["sharedLocations"]
+        if t - 128 >= len(shared):
+            raise FormatError("map: shared location %d has no entry" % t)
+        t = shared[t - 128]
+    loc, _disk, _index = containers.resolve_location(tables, t)
+    if record.get("relative"):
+        tx = x + record["x"]
+        ty = y + record["y"]
+    else:
+        tx = record["x"] & 0xFF
+        ty = record["y"] & 0xFF
+    size = tables["mapSizes"][loc]
+    if not (0 <= tx < size and 0 <= ty < size):
+        raise FormatError("map: transition target (%d, %d) outside the %d x %d map (L-TR5)"
+                          % (tx, ty, size, size))
+    return [loc, tx, ty]
+
+
+def image_at(map: dict, x: int, y: int) -> int:
+    """The cell image, or the border image outside the map (L-MI5)."""
+    size = map["size"]
+    if not (0 <= x < size and 0 <= y < size):
+        return map["info"]["borderImage"]
+    return map["cells"]["image"][y][x]
+
+
+__all__ = [
+    "decode_map",
+    "load_map",
+    "record_at",
+    "is_passable",
+    "apply_tail",
+    "resolve_transition",
+    "image_at",
+    "decode_record",
+]

```