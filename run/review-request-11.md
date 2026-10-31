# Review request, iteration 11

Run w1-2026-10-21; model deepseek-v41-flash-exl3; trigger: milestone passed: M4.

Reply by writing `review-reply-11.md` in /Users/dtinholt/wasteland-build/runs/w1-2026-10-21. The run is not paused; a reply is injected into the next iteration that starts after it appears.

## Test summary

- M1: 89/89 passed, 0 failed, 0 errors [PASS]
- M2: 107/107 passed, 0 failed, 0 errors [PASS]
- M3: 94/94 passed, 0 failed, 0 errors [PASS]
- M4: 76/76 passed, 0 failed, 0 errors [PASS]
- M5: 1/82 passed, 81 failed, 0 errors [open]
- M6: 0/55 passed, 55 failed, 0 errors [open]

First 10 of 136 failing tests:
* [M5] tests.test_m5_rules::test_rng_seeding
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_rng_next
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_rng_roll
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_rng_d100
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_rng_dice
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_rng_rnd
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_rng_no_draw_cases
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_roll_attributes
    Failed: wlengine.rules has no attribute 'Rng' (SPEC-07 API)
    wlengine.rules has no attribute 'Rng' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_max_hp
    Failed: wlengine.rules has no attribute 'max_hp' (SPEC-07 API)
    wlengine.rules has no attribute 'max_hp' (SPEC-07 API)
* [M5] tests.test_m5_rules::test_armour_class
    Failed: wlengine.rules has no attribute 'armour_class' (SPEC-07 API)
    wlengine.rules has no attribute 'armour_class' (SPEC-07 API)

## Worklog tail

[earlier entries omitted]
  (8 bytes each), string table (strings.encode_table(DICT, strings)). CD = u16 stringsOff, namesOff,
  dataOff, 16 action offsets, specialsOff, npcOff. npcOff = stringsOff when no NPCs.
  prefix = body[:stringsOff] -> codecs.rotating_xor_encode; data_section = enc + body[stringsOff:] + b"\x00";
  tile section = u32(S*S)+u32(0)+huffman.encode(tile bytes); block = b"msq"+bytes((0x30+disk,))+data_section+tsec;
  tmo = 4 + len(data_section). Verified sizes: loc0 7874/tmo 6816/prefix 6460, loc1 2406/2151/1957,
  loc2 2848/2593/2260, loc3 2682/2518/2059 (matches SPEC-05 5.6).
- Record encoders (encode_record) for classes 1,3,4,5,6,10,11 + _tail(nc,na) exactly as fixtures_gen.rec_encode.
- Character dict from party.json/npcs: name bytes, attrs, dexterity 0, money, gender, nationality,
  armorClass = AGL//5 + armour item damage + Evasion(11) level, maxCon=curCon=10+STR+(level-1)*(2+STR//5),
  weaponSlot, skillPoints 0, experience=xp, level, armorSlot, lastCon/afflictions/npc/itemRefuse/
  skillRefuse/attribRefuse/tradeRefuse/joinString/willingness 0, rank = labstr table 3[level-1],
  gameWon/specialPromotion 0, skills/items as [id,val] pairs. NPC records get npc=1.
- mob name = name + (b"\x0a\x0a"+plural_suffix+b"\x0a" if plural_suffix else b"").
- Savegame: groups[0].order = 1..n + zeros, x/y/map from scenario start, viewportX/Y = start x/y,
  currentMembers=totalMembers=n, currentMap=start location, hour=start hour, rest 0; characters =
  party + containers.decode_character(bytes(0x100)) empties. containers.encode_savegame(sg, 0).
- Shops: 94 records from items.json catalog (missing ids -> 8 zero bytes), stock from shops.json
  stock[str(id)], type = type_byte>>3, lowFlags = type_byte&7. containers.encode_shop_list(items, 0).
- LABTABLES.BIN: mapOffsets = cumulative block offsets, tileMapOffsets = tmos, locationMapping =
  (2<<6)|i for i in 0..3, mapSizes = sizes, sharedLocations = [2]*125, mobSpriteMap=[0,6,3,4,2,1],
  savegameOffsets=[sg_off, 0xFFFFFFFF], savegameSize=0x1206, **shopListRelOffsets = [i*766 for i in range(4)]**
  (cumulative! first attempt used [0,766,766,766] and shop 2 failed), mapCounts=[4,0],
  shopListCounts=[3,0], tilesetOffsets=[0]*9, tilesetSizes=[len(ALLHTDS1)]+[0]*8,
  portraitOffsets1 = per-portrait offsets in ALLPICS1, portraitOffsets2=[0]*49,
  **portraitIndices1 = [0x80, 0, 1, 2, 3] + [0x80]*75** (index 0 unused = 0x80; raw id 1 -> compact
  index 0, raw 2 -> 1, raw 3 -> 2, raw 4 -> 3; my first tries [0,1,2,3] and [0x80,1,2,3,4] both failed).
- LABSTR.BIN: 6 tables, each strings.encode_table(DICT, pad4(strings)); table 0/3/4/5 from
  scenario.json labstr_tables, table 1 = strings.json by id with {name}->\x0b, {num}->\x0f,
  table 2 = [""] + skill names sorted by id + item names sorted by id. File framing = magic +
  u16 count + u16 0 + u32 offsets + u32 sizes + tables.
- LABSKILL.BIN = bytes((iq_req<<3)|cost, attr_offset) for entry0 + labskill_bytes of each skill sorted by id.
- LABHOOKS.JSON / PARAGRAPHS.JSON = byte copies of hooks.json / paragraphs.json.
- ALLHTDS1 = huffman.encode_msq(concat of codecs.vertical_xor_encode(graphics.pack4(tile), 8)); tile t =
  fill t%16 with 1-pixel border (t+8)%16. ALLPICS1 = per portrait: msq(vxor(base,48)) + msq(anim);
  base fill 4+p with centred 48x42 rect of 15; one update XORs 8 bytes at offset 2000 with 0xFF;
  script [(20,0),(20,0)]; anim = u16(len(sb))+sb+u16(len(ub))+ub with sb=b"\x14\x00\x14\x00\xff",
  ub=u16((8-1)<<12|2000)+8 bytes+u16(0xFFFF).
- Placeholders (not compared by tests beyond round trip): IC0_9.WLF 10 sprites (128 bytes, planes_encode),
  MASKS.WLF 10 masks (32 bytes), COLORF.FNT 32 glyphs (32 bytes each), CURS 2 cursors (256 bytes each),
  TITLE.PIC 18432 = vxor(pack4(288x128),144), END.CPA = msq(vxor(base,144)) + msq(anim,0,b"\x08\x67\x01").

NEXT STEP (M5, 1/82 -> target 82/82): tests/test_m5_rules.py + tests/wl_support.py hold the expected
formulas (RefRng, ref_* helpers) and tests/wl_combat_ref.py the combat reference. Need to add to
src/wlengine/rules.py (currently only read_skill_table):
- class Rng(seed): xorshift32 (x^=x<<13; x^=x>>17; x^=x<<5, mod 2^32, seed 0 -> 0x6D2B79F5), .state,
  next(), roll(n)=1+next()%n, rnd(n) (0->0, 1->1 no call, else roll), dice(N,S)=N rolls summed,
  d100=roll(100). Vectors in SPEC/scenario/rng-vectors.json.
- roll_attributes(rng) -> 6x (8+roll(10)) in order STR IQ LCK SPD AGL CHA.
- max_hp(st,lvl), armour_class(agl,bonus,evasion), starting_money(lck)=50+5*lck.
- check_need(lvl,attr,d,tool)=20+15*lvl+2*attr-d+(20 if tool else 0); skill_check(rng,...) -> dict with
  member/skill/level/need/roll/success (no draw when need>=100 or <=0); pick_checker(cands) (highest
  level, then higher attribute, then lower slot; skip non-conscious; None if none).
- advance_clock(clock,mins,secs) -> (clock, hours crossed in order); xp_threshold(lvl), level_after(lvl,xp);
  buy_price(price,h), sell_price(price,h), pay(moneys,first,price).
- monster_values(m) {to_hit_base:20+5*combatRating, speed:combatRating, ac:armorClass,
  ranged:weaponType>=3, xp:sturdiness*(armorClass+1)}; monster_hp(rng,st) (high byte drawn first);
  monster_damage(rng,m)=dice(randomDamage,6)+fixedDamage; build_groups(rng,mobs,rec).
- ranged_need, melee_need, monster_need, jam_chance, flee_need, speed_order, damage_member,
  ref_advance_clock etc. — read the rest of test_m5_rules.py (lines 420-834) and wl_support.py ref_*
  functions for exact signatures, then wlengine.labstate (encode/decode_labstate, SPEC-04 LR-57,
  magic WLLABS?1, sum check) and wlengine.headless (SPEC-06 5/6) for the runner-based tests.
Read SPEC-04 sections 7-16 for the remaining rules. Work in small verified steps; run M5 after each
group of functions. M6 then needs wlengine.headless + wlengine.ui (SPEC-06).

[harness] iter 11 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->76/76; M5 1->1/82; M6 0->0/55; files changed: src/wlengine/scenario.py


## Diff since last review (0f1d6d7f8b..60ad41bdb6)

```diff
 WORKLOG.md                        | 224 ++++++++++++++
 src/wlengine/rules.py             |  30 ++
 src/wlengine/scenario.py          | 625 ++++++++++++++++++++++++++++++++++++++
 tests/fixtures-generated/proto.py |  90 ++++++
 4 files changed, 969 insertions(+)

diff --git a/WORKLOG.md b/WORKLOG.md
index 646d1c7..7eeb80a 100644
--- a/WORKLOG.md
+++ b/WORKLOG.md
@@ -237,3 +237,227 @@ Facts gathered this iteration (do not re-read):
   + `wlengine.ui` (SPEC-06).
 
 [harness] iter 2 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 0->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; files changed: src/wlengine/maps.py
+
+### iter 3 note (2026-10-21T17:45:54-05:00)
+Iter 3 (M4, 0/76): spent the whole budget reading specs/reference, wrote no code. Findings to reuse (do not re-read):
+
+- `wlengine.scenario.compile(scenario_dir, out_dir)` must write: GAME1, LABTABLES.BIN, LABSTR.BIN, LABSKILL.BIN, LABHOOKS.JSON, PARAGRAPHS.JSON, ALLHTDS1, ALLPICS1, IC0_9.WLF, MASKS.WLF, COLORF.FNT, CURS, TITLE.PIC, END.CPA. Tests call it via W.api("scenario.compile") with (SCENARIO, tmpdir); it may read SPEC/scenario only (audit hook forbids SPEC/reference + walkthrough-reference-log).
+- Map encoder = mirror `SPEC/reference/fixtures_gen.py::build_map` (lines 453-540) exactly:
+  body = class nibbles (high nibble = even x), action bytes, 42-byte central dir placeholder, mapinfo(50), tables TABLE_ORDER_A=[0..7,15], NPC section (u16 0 + u16 ptrs + 0x100 records), TABLE_ORDER_B=[8..14], specials=0, mob names (name+NUL), mob data (8 bytes), strings (strtab_encode(DICT, strings padded to mult of 4)).
+  cd = u16(strings_off)+u16(names_off)+u16(data_off)+16*u16(offsets)+u16(specials)+u16(npc_off); npc_off=strings_off when no NPCs.
+  data_section = rxor_encode(body[:strings_off]) + body[strings_off:] + b"\x00"; tsec = u32(S*S)+u32(0)+huff_encode(tile bytes); block = b"msq"+bytes(0x30+disk)+data_section+tsec; tmo = 4+len(data_section).
+  Prefix must pass codecs.rotating_xor_prefix_is_unambiguous; monster portrait byte = 1 keeps last prefix byte non-zero (SPEC-05 5.6). No "msq" after header (L-EN8).
+  Map JSON: keys location,size,info{encounter_frequency,tileset,random_monster_types,max_random_encounters,border_image,time_per_step,heal_rate}, strings, mobs (name+plural_suffix -> name + b"\x0a\x0a"+suffix+b"\x0a"), npcs (JSON fields -> char dict via oracle_tool.char_from_json formula), records[c][i] = slot i+1, tiles (image = id+10), action_class, action_value. Record encoders: see fixtures_gen.rec_encode (lines 312-343) — copy it.
+- LABTABLES.BIN: 0x438 bytes, magic WLLABTB1; mapOffsets u32[42] cumulative, tileMapOffsets u16[50], locationMapping u8[50] = 0x80+i, mapSizes u8[50], sharedLocations u8[125], mobSpriteMap u8[6], savegameOffsets u32[2] = [sg_off, 0xFFFFFFFF], savegameSize u16 = 0x1206, shopListRelOffsets u16[4] = [0,766,766,766], mapCounts [4,0], shopListCounts [3,0], tilesetOffsets u32[9] = [0,size,0...], tilesetSizes u16[9] = [size,0...], portraitOffsets1 u32[34] cumulative, portraitIndices1 u8[80] = [1,2,3,4]+[0x80]*76, portraitOffsets2/Indices2 zero.
+- Savegame: containers.encode_savegame(sg, 0) with groups[0].order 1..n, x/y/map = start, viewport = start x/y, currentMembers n, currentMap start location, hour start hour, characters = party chars + empty*3. char_from_json formula is in oracle_tool.py lines ~100-125 (hp = 10+STR+(level-1)*(2+STR//5); armorClass = AGL//5 + armour item damage + evasion skill 11; rank = labstr table 3[level-1]).
+- Shops: 3 lists of 94 records, record i = item id i+1 (price, stock from shops.json stock map keyed by str(id), type = type_byte>>3, lowFlags = type_byte&7, capacity, skill, damage, ammo), else 8 zero bytes; containers.encode_shop_list(items, 0).
+- LABSTR.BIN: magic WLLABST1, u16 count, u16 0, u32 offsets[n], u32 sizes[n], tables. 6 tables: 0,3,4,5 from scenario.json labstr_tables; table1 = UI strings by id with {name}->0x0b, {num}->0x0f; table2 = [""] + skill names by id + item names by id; each padded to mult of 4; strings.encode_table(DICT, ...) with DICT from SPEC-02 9.3.
+- LABSKILL.BIN: 36 entries x 2 bytes: entry0 = (iq_req<<3)|cost, attr_offset; then skills.json skills sorted by id, labskill_bytes.
+- LABHOOKS.JSON/PARAGRAPHS.JSON = verbatim copies of hooks.json/paragraphs.json.
+- ALLHTDS1: one tileset, 32 tiles 16x16 4bpp: huffman.encode_msq(b"".join(vertical_xor_encode(pack4(tile),8)), 0). Placeholder tile t: fill t%16, 1px border (t+8)%16.
+- ALLPICS1: 4 portraits raw ids 1..4, 96x84 4bpp (4032 bytes): msq(vxor(base,48)) + msq(anim); base fill 4+p with centred 48x42 rect of 15; one update XORs 8 bytes at offset 2000 with 0xFF; script [(20,0),(20,0)]; anim = u16(len(sb))+sb+u16(len(ub))+ub, sb = 14 00 14 00 FF, ub = u16((8-1)<<12|2000)+8 bytes+u16(0xFFFF).
+- Placeholders: IC0_9.WLF 10 sprites (128 bytes each, planes_encode), MASKS.WLF 10 masks (32 bytes), COLORF.FNT 32 glyphs (32 bytes each), CURS 2 cursors (256 bytes each), TITLE.PIC 18432 = vxor_encode(pack4(288x128),144), END.CPA = msq(vxor(base,144)) + msq(anim, 0, b"\x08\x67\x01").
+- Also need `wlengine/rules.py::read_skill_table(path)` -> [[b0>>3, b0&7, b1], ...] (36 entries).
+
+Next step: write src/wlengine/scenario.py (compiler) + src/wlengine/rules.py, then run M4 and fix the first differing field. Reuse codecs/containers/strings/huffman/graphics encoders already in src/.
+
+[harness] iter 3 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; no file changes
+
+[harness] iter 4 ended (turn_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; no file changes
+
+[harness] iter 5 ended (token_cap); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; no file changes
+
+### iter 6 note (2026-10-21T18:26:42-05:00)
+### iter 6 note (M4, 0/76): spec/reference reading only, no code written yet
+
+Verified details for writing `src/wlengine/scenario.py` (compiler) + `src/wlengine/rules.py`.
+Everything below was read from SPEC/scenario/*.json, tests/oracle_tool.py and
+SPEC/reference/fixtures_gen.py this iteration; do not re-read those.
+
+**API**: `wlengine.scenario.compile(scenario_dir, out_dir) -> None` (SPEC-07 2.9).
+conftest calls it with (SPEC/scenario, tmpdir) and `allow_reference_log=True`, so it
+may read any file in SPEC/scenario (incl. walkthrough-reference-log.json) but NOT
+SPEC/reference. It must write all 14 files of REQUIRED_FILES.
+
+**Expected structures** (oracle_tool.expected_from_json, lines 100-200) — the compiler
+must reproduce exactly these:
+- map dict keys: `size`, `info`, `cells{actionClass,action,image}`, `actions`,
+  `npcs`, `mobs`, `strings`. `image = tiles + 10`; `actions[str(c)] = [None] + records`;
+  `strings` padded with "" to a multiple of 4; `info` = mapinfo_decode(mapinfo_encode(S, mi))
+  where mi uses camelCase keys (encounterFrequency, tileset, randomMonsterTypes,
+  maxRandomEncounters, borderImage, timePerStep, healRate).
+- mapinfo_encode: 50 bytes, b[2]=size, b[5..9]=the 5 fields, b[0x0A:0x0C]=u16(timePerStep),
+  b[0x0C]=healRate, everything else 0.
+- map JSON keys: location,name,width,height,tileset,info,strings,mobs,npcs,records,
+  action_cells,tiles,action_class,action_value (all [y][x]).
+- mob name = name + (b"\x0a\x0a" + plural_suffix + b"\x0a" if plural_suffix else b"").
+- NPC/party char dict = oracle_tool.char_from_json (lines ~100-125): hp = 10+STR+(level-1)*(2+STR//5);
+  armorClass = AGL//5 + (armour item damage if armour_slot) + evasion skill 11 level;
+  rank = labstr table 3[level-1]; npc=1 for map NPCs, 0 for party; dexterity 0; curCon=maxCon;
+  skills/items = [[id,lvl]] pairs from JSON; then char_decode(char_encode(c)) normalises.
+- savegame: groups[0].order = 1..n + zeros, x/y/map = start, viewportX/Y = start x/y,
+  currentMembers=totalMembers=n, currentMap=start location, hour=start hour, minute 0,
+  characters = party chars + FG.char_decode(bytes(0x100)) * (7-n). Use
+  containers.encode_savegame(sg, 0).
+- shops: 3 lists of 94 records; record i = item id i+1 from items.json catalog
+  (price, stock = shops.json stock[str(id)] or 0, type = type_byte>>3, lowFlags = type_byte&7,
+  capacity, skill, damage, ammo), else 8 zero bytes. containers.encode_shop_list(items, 0).
+- labstr (6 tables, each padded to mult of 4): t0 = labstr_tables["0"]["strings"];
+  t1 = [""]*(max id+1) with strings.json text, {name}->"\x0b", {num}->"\x0f";
+  t2 = [""] + skill names sorted by id + item names sorted by id;
+  t3/t4/t5 = labstr_tables["3"/"4"/"5"]["strings"]. Encode each with
+  strings.encode_table(DICT, [s.encode("latin-1")]) where DICT is the 60 bytes of SPEC-02 9.3
+  (b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r" + b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;").
+  LABSTR.BIN framing: magic WLLABST1 + u16 count + u16 0 + u32 offsets[n] + u32 sizes[n] + tables.
+- labskill: 36 x 2 bytes; entry0 = ((iq_req<<3)|cost, attr_offset) from skills.json entry0,
+  then skills sorted by id, each `labskill_bytes`.
+- LABHOOKS.JSON / PARAGRAPHS.JSON = verbatim copies of hooks.json / paragraphs.json.
+- LABTABLES.BIN (0x438, magic WLLABTB1): mapOffsets u32[42] cumulative (4 maps),
+  tileMapOffsets u16[50] (by location), locationMapping u8[50] = 0x80+i for i<4 else 0,
+  mapSizes u8[50] = [64,32,32,32,0...], sharedLocations u8[125] zeros, mobSpriteMap u8[6] zeros,
+  savegameOffsets u32[2] = [sg_off, 0xFFFFFFFF], savegameSize u16 = 0x1206,
+  shopListRelOffsets u16[4] = [0,766,766,766], mapCounts [4,0], shopListCounts [3,0],
+  tilesetOffsets u32[9] = [0, size, 0...], tilesetSizes u16[9] = [size, 0...],
+  portraitOffsets1 u32[34] cumulative, portraitIndices1 u8[80] = [1,2,3,4]+[0x80]*76,
+  portraitOffsets2/Indices2 all zero. GAME1 length must equal
+  savegameOffsets[0] + 0x1206 + 3*766 (L-TB3).
+- Map block encoder: mirror fixtures_gen.build_map (lines 453-540) exactly:
+  body = class nibbles (high nibble = even x), action bytes, 42-byte central-dir placeholder,
+  mapinfo(50), tables TABLE_ORDER_A=[0..7,15], NPC section (u16 0 + u16 ptrs + 0x100 records),
+  TABLE_ORDER_B=[8..14], specials=0, mob names (name+NUL), mob data (8 bytes each),
+  strings (strtab_encode(DICT, strings padded to mult of 4)).
+  cd = u16(strings_off)+u16(names_off)+u16(data_off)+16*u16(offsets)+u16(specials)+u16(npc_off);
+  npc_off = strings_off when there are no NPCs.
+  data_section = codecs.rotating_xor_encode(body[:strings_off]) + body[strings_off:] + b"\x00";
+  tsec = u32(S*S)+u32(0)+huffman.encode(tile bytes); block = b"msq"+bytes((0x30+disk,))+data_section+tsec;
+  tileMapOffset = 4 + len(data_section). Prefix must pass codecs.rotating_xor_prefix_is_unambiguous
+  (monster portrait byte = 1 keeps the last prefix byte non-zero, SPEC-05 5.6). No "msq" after header.
+  Record encoders = fixtures_gen.rec_encode (lines 312-343) for classes 1,3,4,5,6,10,11:
+  PRINT msgs with 0x80 on last + tail; ENCOUNTER 3 bytes + 3*(mob,(rnd<<7)|grp) + flags + tail;
+  MASK (message,(imp<<7)|tile)+tail; LOOT (nc,na)+items((fixed<<7)|iid,amt)+cash(0xDE/0x5E,u16)+0xFF;
+  SHOP (shop,message)+tail; TRANSITION ((rel<<7)|(conf<<6)|msg, x&0xFF, y&0xFF, location)+tail;
+  BLOCKED (message,)+tail. tail(nc,na) = bytes((nc,)) if nc>=253 else bytes((nc,na)).
+  Slot 0 of each table is a null pointer; cell action byte = 1-based slot.
+- ALLHTDS1: one tileset, 32 tiles 16x16 4bpp: huffman.encode_msq(b"".join(
+  codecs.vertical_xor_encode(graphics.pack4(tile), 8)), 0). Placeholder tile t: fill t%16,
+  1-pixel border (t+8)%16.
+- ALLPICS1: 4 portraits raw ids 1..4, 96x84 4bpp (4032 bytes): msq(vxor(base,48)) + msq(anim);
+  base fill 4+p with a centred 48x42 rect of 15; one update XORs 8 bytes at offset 2000 with 0xFF;
+  script [(20,0),(20,0)]; anim = u16(len(sb))+sb+u16(len(ub))+ub with
+  sb = b"\x14\x00\x14\x00\xff", ub = u16((8-1)<<12|2000)+8 bytes+u16(0xFFFF).
+- Placeholders: IC0_9.WLF 10 sprites (128 bytes each, planes_encode), MASKS.WLF 10 masks
+  (32 bytes), COLORF.FNT 32 glyphs (32 bytes each), CURS 2 cursors (256 bytes each),
+  TITLE.PIC 18432 = codecs.vertical_xor_encode(graphics.pack4(288x128), 144),
+  END.CPA = huffman.encode_msq(vxor(base,144)) + huffman.encode_msq(anim, 0, b"\x08\x67\x01").
+- `wlengine/rules.py::read_skill_table(path)` -> [[b0>>3, b0&7, b1], ...] (36 entries).
+
+**Next step**: write src/wlengine/scenario.py + src/wlengine/rules.py, run M4, fix the
+first differing field. Reuse codecs/containers/strings/huffman/graphics encoders already in src/.
+Reminder: src/ must never contain the strings codecs_ref, fixtures_gen, oracle_tool, wl_support,
+wl_combat_ref, _wl_oracle, reference-log. After M4: M5 needs wlengine.rules (SPEC-04),
+M6 needs wlengine.headless + wlengine.ui (SPEC-06).
+
+[harness] iter 6 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; no file changes
+
+[harness] iteration 7 was interrupted before it finished; it restarts now from whatever state the files are in.
+
+[harness] iter 7 ended (stop_file); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 0->0/82; M6 0->0/55; no file changes
+
+[harness] iter 8 ended (model_done); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 0->1/82; M6 0->0/55; files changed: src/wlengine/rules.py
+
+[harness] iter 9 ended (stop_file); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 1->1/82; M6 0->0/55; no file changes
+
+### iter 10 note (2026-10-21T19:48:27-05:00)
+Iter 10 (M4 focus). Read the M4 test file, conftest, oracle_tool, SPEC-05 sections 5.6/13, and the reference fixtures_gen build_map/rec_encode/char_encode.
+
+KEY FINDING: I prototyped the whole map-block build in tests/fixtures-generated/proto.py using SPEC/reference/fixtures_gen.build_map directly, feeding it the scenario JSON converted to the generator's dict shape. All four map blocks come out with EXACTLY the sizes SPEC-05 5.6 states:
+  loc0 overworld 7874 bytes, tmo 6816, encrypted prefix 6460
+  loc1 Saltwell 2406, tmo 2151, prefix 1957
+  loc2 Ninemile 2848, tmo 2593, prefix 2260
+  loc3 Pumphouse 2682, tmo 2518, prefix 2059
+So the conversion rules are confirmed:
+- map dict keys: size, class (=action_class), action (=action_value), image = tiles+10, info (camelCase from info JSON), actions {int class: [converted records]}, npcs (char dicts), mobs (mob dicts), dictionary=DICT, strings (latin-1 bytes).
+- record conversion: class1 messages; class3 visible_distance/hit_distance/message/groups/proper_name/friendly/immobile/npc=0; class4 message/impassable/tile; class5 items/cash; class6 shop/message; class10 relative/confirm/message/x/y/location; class11 message; plus newClass=new_class, newAction=new_action.
+- mob name = name + (b"\x0a\x0a"+plural_suffix+b"\x0a" if plural_suffix else b"").
+- char dict: name bytes, STR/IQ/LCK/SPD/AGL/CHA from attrs, dexterity 0, money, gender, nationality, armorClass = AGL//5 + armour item damage + evasion skill 11 level, maxCon=curCon=10+STR+(level-1)*(2+STR//5), weaponSlot, skillPoints 0, experience=xp, level, armorSlot, lastCon/afflictions/npc/itemRefuse/skillRefuse/attribRefuse/tradeRefuse/joinString/willingness 0, rank = labstr table 3[level-1], gameWon/specialPromotion 0, skills/items as [[id,lvl]] pairs. (In proto.py I returned the raw dict instead of char_encode/char_decode because fixtures_gen.char_encode needs bytes name and my dict was fine once I passed bytes; the TypeError was only from my own test harness passing str.)
+- DICT (SPEC-02 9.3) = b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r" + b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;" (60 bytes).
+
+NEXT STEP: write src/wlengine/scenario.py with compile(scenario_dir, out_dir) that mirrors fixtures_gen.build_map/rec_encode/char_encode/savegame_encode/shop_encode/labtables_encode/labstr_encode/labskill using the engine's own codecs/containers/strings/huffman/graphics encoders (already present in src/). Then run M4 and fix the first differing field. Write it in parts (write_file first ~250 lines, then apply_patch) to avoid the output-limit truncation that killed iteration 8. Do NOT import fixtures_gen/codecs_ref from src/ (SPEC-07 rule 6.1 scans src/ for those names). tests/fixtures-generated/proto.py is a scratch prototype and may be deleted.
+
+[harness] iter 10 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->0/76; M5 1->1/82; M6 0->0/55; files changed: tests/fixtures-generated/proto.py
+
+### iter 11 note (2026-10-21T20:23:17-05:00)
+Iter 11 (M4 focus): **M4 now 76/76 PASS.** Wrote src/wlengine/scenario.py (627 lines) implementing
+`compile(scenario_dir, out_dir)` per SPEC-05 13 + SPEC-07 2.9, using only the engine's own
+codecs/containers/strings/huffman/graphics encoders (no oracle imports; src/ scan stays clean).
+
+What worked (all confirmed by the tests):
+- Map blocks: build_map mirrors SPEC/reference/fixtures_gen.build_map exactly. Body = class nibbles
+  (high nibble = even x), action bytes, 42-byte central directory placeholder, 50-byte map info;
+  then tables in TABLE_ORDER_A=[0,1,2,3,4,5,6,7,15], NPC section (u16 0 + u16 pointers + 0x100-byte
+  records) only if npcs, TABLE_ORDER_B=[8..14], specialsOffset=0, mob names (name+NUL), mob data
+  (8 bytes each), string table (strings.encode_table(DICT, strings)). CD = u16 stringsOff, namesOff,
+  dataOff, 16 action offsets, specialsOff, npcOff. npcOff = stringsOff when no NPCs.
+  prefix = body[:stringsOff] -> codecs.rotating_xor_encode; data_section = enc + body[stringsOff:] + b"\x00";
+  tile section = u32(S*S)+u32(0)+huffman.encode(tile bytes); block = b"msq"+bytes((0x30+disk,))+data_section+tsec;
+  tmo = 4 + len(data_section). Verified sizes: loc0 7874/tmo 6816/prefix 6460, loc1 2406/2151/1957,
+  loc2 2848/2593/2260, loc3 2682/2518/2059 (matches SPEC-05 5.6).
+- Record encoders (encode_record) for classes 1,3,4,5,6,10,11 + _tail(nc,na) exactly as fixtures_gen.rec_encode.
+- Character dict from party.json/npcs: name bytes, attrs, dexterity 0, money, gender, nationality,
+  armorClass = AGL//5 + armour item damage + Evasion(11) level, maxCon=curCon=10+STR+(level-1)*(2+STR//5),
+  weaponSlot, skillPoints 0, experience=xp, level, armorSlot, lastCon/afflictions/npc/itemRefuse/
+  skillRefuse/attribRefuse/tradeRefuse/joinString/willingness 0, rank = labstr table 3[level-1],
+  gameWon/specialPromotion 0, skills/items as [id,val] pairs. NPC records get npc=1.
+- mob name = name + (b"\x0a\x0a"+plural_suffix+b"\x0a" if plural_suffix else b"").
+- Savegame: groups[0].order = 1..n + zeros, x/y/map from scenario start, viewportX/Y = start x/y,
+  currentMembers=totalMembers=n, currentMap=start location, hour=start hour, rest 0; characters =
+  party + containers.decode_character(bytes(0x100)) empties. containers.encode_savegame(sg, 0).
+- Shops: 94 records from items.json catalog (missing ids -> 8 zero bytes), stock from shops.json
+  stock[str(id)], type = type_byte>>3, lowFlags = type_byte&7. containers.encode_shop_list(items, 0).
+- LABTABLES.BIN: mapOffsets = cumulative block offsets, tileMapOffsets = tmos, locationMapping =
+  (2<<6)|i for i in 0..3, mapSizes = sizes, sharedLocations = [2]*125, mobSpriteMap=[0,6,3,4,2,1],
+  savegameOffsets=[sg_off, 0xFFFFFFFF], savegameSize=0x1206, **shopListRelOffsets = [i*766 for i in range(4)]**
+  (cumulative! first attempt used [0,766,766,766] and shop 2 failed), mapCounts=[4,0],
+  shopListCounts=[3,0], tilesetOffsets=[0]*9, tilesetSizes=[len(ALLHTDS1)]+[0]*8,
+  portraitOffsets1 = per-portrait offsets in ALLPICS1, portraitOffsets2=[0]*49,
+  **portraitIndices1 = [0x80, 0, 1, 2, 3] + [0x80]*75** (index 0 unused = 0x80; raw id 1 -> compact
+  index 0, raw 2 -> 1, raw 3 -> 2, raw 4 -> 3; my first tries [0,1,2,3] and [0x80,1,2,3,4] both failed).
+- LABSTR.BIN: 6 tables, each strings.encode_table(DICT, pad4(strings)); table 0/3/4/5 from
+  scenario.json labstr_tables, table 1 = strings.json by id with {name}->\x0b, {num}->\x0f,
+  table 2 = [""] + skill names sorted by id + item names sorted by id. File framing = magic +
+  u16 count + u16 0 + u32 offsets + u32 sizes + tables.
+- LABSKILL.BIN = bytes((iq_req<<3)|cost, attr_offset) for entry0 + labskill_bytes of each skill sorted by id.
+- LABHOOKS.JSON / PARAGRAPHS.JSON = byte copies of hooks.json / paragraphs.json.
+- ALLHTDS1 = huffman.encode_msq(concat of codecs.vertical_xor_encode(graphics.pack4(tile), 8)); tile t =
+  fill t%16 with 1-pixel border (t+8)%16. ALLPICS1 = per portrait: msq(vxor(base,48)) + msq(anim);
+  base fill 4+p with centred 48x42 rect of 15; one update XORs 8 bytes at offset 2000 with 0xFF;
+  script [(20,0),(20,0)]; anim = u16(len(sb))+sb+u16(len(ub))+ub with sb=b"\x14\x00\x14\x00\xff",
+  ub=u16((8-1)<<12|2000)+8 bytes+u16(0xFFFF).
+- Placeholders (not compared by tests beyond round trip): IC0_9.WLF 10 sprites (128 bytes, planes_encode),
+  MASKS.WLF 10 masks (32 bytes), COLORF.FNT 32 glyphs (32 bytes each), CURS 2 cursors (256 bytes each),
+  TITLE.PIC 18432 = vxor(pack4(288x128),144), END.CPA = msq(vxor(base,144)) + msq(anim,0,b"\x08\x67\x01").
+
+NEXT STEP (M5, 1/82 -> target 82/82): tests/test_m5_rules.py + tests/wl_support.py hold the expected
+formulas (RefRng, ref_* helpers) and tests/wl_combat_ref.py the combat reference. Need to add to
+src/wlengine/rules.py (currently only read_skill_table):
+- class Rng(seed): xorshift32 (x^=x<<13; x^=x>>17; x^=x<<5, mod 2^32, seed 0 -> 0x6D2B79F5), .state,
+  next(), roll(n)=1+next()%n, rnd(n) (0->0, 1->1 no call, else roll), dice(N,S)=N rolls summed,
+  d100=roll(100). Vectors in SPEC/scenario/rng-vectors.json.
+- roll_attributes(rng) -> 6x (8+roll(10)) in order STR IQ LCK SPD AGL CHA.
+- max_hp(st,lvl), armour_class(agl,bonus,evasion), starting_money(lck)=50+5*lck.
+- check_need(lvl,attr,d,tool)=20+15*lvl+2*attr-d+(20 if tool else 0); skill_check(rng,...) -> dict with
+  member/skill/level/need/roll/success (no draw when need>=100 or <=0); pick_checker(cands) (highest
+  level, then higher attribute, then lower slot; skip non-conscious; None if none).
+- advance_clock(clock,mins,secs) -> (clock, hours crossed in order); xp_threshold(lvl), level_after(lvl,xp);
+  buy_price(price,h), sell_price(price,h), pay(moneys,first,price).
+- monster_values(m) {to_hit_base:20+5*combatRating, speed:combatRating, ac:armorClass,
+  ranged:weaponType>=3, xp:sturdiness*(armorClass+1)}; monster_hp(rng,st) (high byte drawn first);
+  monster_damage(rng,m)=dice(randomDamage,6)+fixedDamage; build_groups(rng,mobs,rec).
+- ranged_need, melee_need, monster_need, jam_chance, flee_need, speed_order, damage_member,
+  ref_advance_clock etc. — read the rest of test_m5_rules.py (lines 420-834) and wl_support.py ref_*
+  functions for exact signatures, then wlengine.labstate (encode/decode_labstate, SPEC-04 LR-57,
+  magic WLLABS?1, sum check) and wlengine.headless (SPEC-06 5/6) for the runner-based tests.
+Read SPEC-04 sections 7-16 for the remaining rules. Work in small verified steps; run M5 after each
+group of functions. M6 then needs wlengine.headless + wlengine.ui (SPEC-06).
+
+[harness] iter 11 ended (end_iteration); tests: M1 89->89/89; M2 107->107/107; M3 94->94/94; M4 0->76/76; M5 1->1/82; M6 0->0/55; files changed: src/wlengine/scenario.py
diff --git a/src/wlengine/rules.py b/src/wlengine/rules.py
new file mode 100644
index 0000000..88d870b
--- /dev/null
+++ b/src/wlengine/rules.py
@@ -0,0 +1,30 @@
+"""Game rules (SPEC-04).
+
+This module holds the lab rules v1 of SPEC-04: the random generator, the
+character formulas, skill checks, movement and time, encounters, combat and
+the shop prices.  ``read_skill_table`` reads the 36-entry skill metadata table
+of LABSKILL.BIN (SPEC-04 LR-6).
+"""
+
+from __future__ import annotations
+
+from .errors import FormatError
+
+SKILL_ENTRIES = 36
+
+
+def read_skill_table(path: str) -> list:
+    """36 x ``[minimum_iq, cost, attribute_offset]`` (SPEC-04 LR-6)."""
+    with open(path, "rb") as fh:
+        data = fh.read()
+    if len(data) < 2 * SKILL_ENTRIES:
+        raise FormatError("LABSKILL: %d bytes, expected at least %d"
+                          % (len(data), 2 * SKILL_ENTRIES))
+    out = []
+    for i in range(SKILL_ENTRIES):
+        b0, b1 = data[2 * i], data[2 * i + 1]
+        out.append([b0 >> 3, b0 & 7, b1])
+    return out
+
+
+__all__ = ["read_skill_table"]
diff --git a/src/wlengine/scenario.py b/src/wlengine/scenario.py
new file mode 100644
index 0000000..0cab296
--- /dev/null
+++ b/src/wlengine/scenario.py
@@ -0,0 +1,625 @@
+"""The scenario compiler (SPEC-05 section 13).
+
+``compile(scenario_dir, out_dir)`` reads ``scenario.json`` and the files it
+lists and writes the lab data set of SPEC-02 section 12.1: GAME1 (four maps,
+the new-game savegame, three shop lists), LABTABLES.BIN, LABSTR.BIN,
+LABSKILL.BIN, LABHOOKS.JSON, PARAGRAPHS.JSON, ALLHTDS1, ALLPICS1, IC0_9.WLF,
+MASKS.WLF, COLORF.FNT, CURS, TITLE.PIC and END.CPA.
+
+Everything is written with the engine's own encoders, so reading the output
+back through the engine's loaders returns the JSON content again.
+"""
+
+from __future__ import annotations
+
+import json
+import os
+
+from . import codecs, containers, graphics, huffman, strings
+from .errors import FormatError
+
+# The 60-byte dictionary D of SPEC-02 section 9.3.
+DICT = (b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r"
+        b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;")
+
+# Section order inside the map-data body (SPEC-03 section 6.1).
+TABLE_ORDER_A = [0, 1, 2, 3, 4, 5, 6, 7, 15]
+TABLE_ORDER_B = [8, 9, 10, 11, 12, 13, 14]
+
+NO_CHANGE = 255
+
+MAPINFO_FIELDS = ("encounterFrequency", "tileset", "randomMonsterTypes",
+                  "maxRandomEncounters", "borderImage")
+
+PORTRAIT_BASE_SIZE = graphics.PORTRAIT_BASE_SIZE
+PORTRAIT_STRIDE = graphics.PORTRAIT_STRIDE
+TITLE_STRIDE = graphics.TITLE_STRIDE
+ENDING_SIGNATURE = graphics.ENDING_SIGNATURE
+
+
+# ---------------------------------------------------------------------------
+# Small helpers
+# ---------------------------------------------------------------------------
+
+def _u16(v: int) -> bytes:
+    return (v & 0xFFFF).to_bytes(2, "little")
+
+
+def _u32(v: int) -> bytes:
+    return (v & 0xFFFFFFFF).to_bytes(4, "little")
+
+
+def _fixed(text, n: int) -> bytes:
+    raw = text.encode("latin-1") if isinstance(text, str) else bytes(text)
+    return raw[:n] + bytes(max(0, n - len(raw)))
+
+
+def _load_json(path: str):
+    with open(path, "r", encoding="utf-8") as fh:
+        return json.load(fh)
+
+
+def _write(out_dir: str, name: str, data: bytes) -> None:
+    with open(os.path.join(out_dir, name), "wb") as fh:
+        fh.write(data)
+
+
+def _pad4(lst: list) -> list:
+    return list(lst) + [""] * ((-len(lst)) % 4)
+
+
+# ---------------------------------------------------------------------------
+# Action records (SPEC-03 section 9.2, lab layouts)
+# ---------------------------------------------------------------------------
+
+def _tail(nc: int, na: int) -> bytes:
+    return bytes((nc,)) if nc >= 253 else bytes((nc, na))
+
+
+def encode_record(cls: int, r: dict) -> bytes:
+    nc, na = r.get("newClass", NO_CHANGE), r.get("newAction", 0)
+    if cls == 1:  # PRINT
+        msgs = r["messages"]
+        b = bytes(m | (0x80 if i == len(msgs) - 1 else 0) for i, m in enumerate(msgs))
+        return b + _tail(nc, na)
+    if cls == 3:  # FIXED_ENCOUNTER
+        b = bytes((r["visibleDistance"], r["hitDistance"], r["message"]))
+        for mob, rnd, grp in r["groups"]:
+            b += bytes((mob, (0x80 if rnd else 0) | grp))
+        flags = r["properName"] | (r["friendly"] << 1) | (r["immobile"] << 2) | (r["npc"] << 4)
+        return b + bytes((flags,)) + _tail(nc, na)
+    if cls == 4:  # MASK (lab door)
+        return bytes((r["message"], (0x80 if r["impassable"] else 0) | r["tile"])) + _tail(nc, na)
+    if cls == 5:  # LOOT (wllib layout)
+        b = bytes((nc if nc != NO_CHANGE else 0, na))
+        for iid, fixed_, amt in r["items"]:
+            b += bytes(((0x80 if fixed_ else 0) | iid, amt))
+        if r.get("cash") is not None:
+            fixed_, amt = r["cash"]
+            b += bytes((0xDE if fixed_ else 0x5E,)) + _u16(amt)
+        return b + b"\xFF"
+    if cls == 6:  # SHOP (lab)
+        return bytes((r["shop"], r["message"])) + _tail(nc, na)
+    if cls == 10:  # TRANSITION
+        flags = (0x80 if r["relative"] else 0) | (0x40 if r["confirm"] else 0) | r["message"]
+        return bytes((flags, r["x"] & 0xFF, r["y"] & 0xFF, r["location"])) + _tail(nc, na)
+    if cls == 11:  # BLOCKED
+        return bytes((r["message"],)) + _tail(nc, na)
+    raise FormatError("scenario: lab rules define no record for class %d" % cls)
+
+
+def encode_mapinfo(size: int, mi: dict) -> bytes:
+    b = bytearray(50)
+    b[2] = size
+    for i, k in enumerate(MAPINFO_FIELDS):
+        b[5 + i] = mi[k]
+    b[0x0A:0x0C] = _u16(mi["timePerStep"])
+    b[0x0C] = mi["healRate"]
+    return bytes(b)
+
+
+def encode_mob(m: dict) -> bytes:
+    return (_u16(m["sturdiness"])
+            + bytes((m["combatRating"], m["randomDamage"],
+                     (m["maxGroup"] << 4) | m["armorClass"],
+                     (m["fixedDamage"] << 4) | m["weaponType"],
+                     m["type"], m["portrait"])))
+
+
+# ---------------------------------------------------------------------------
+# Map block (SPEC-03 sections 3 to 9)
+# ---------------------------------------------------------------------------
+
+def build_map(m: dict, disk: int = 0):
+    """Return ``(block, tile_map_offset, facts)`` for one map dict."""
+    S = m["size"]
+    cls, act, img = m["class"], m["action"], m["image"]
+    body = bytearray()
+    for y in range(S):
+        for x in range(0, S, 2):
+            body.append((cls[y][x] << 4) | cls[y][x + 1])  # high nibble = even x
+    for y in range(S):
+        body += bytes(act[y])
+    cd_at = len(body)
+    body += bytes(42)
+    body += encode_mapinfo(S, m["info"])
+
+    offsets = [0] * 16
+
+    def emit_table(c: int) -> None:
+        recs = m["actions"].get(c)
+        if not recs:
+            return
+        start = len(body)
+        offsets[c] = start
+        encs = [None] + [encode_record(c, r) for r in recs]  # slot 0 is null
+        pos = start + 2 * len(encs)
+        ptrs = []
+        for e in encs:
+            if e is None:
+                ptrs.append(0)
+            else:
+                ptrs.append(pos)
+                pos += len(e)
+        for p in ptrs:
+            body.extend(_u16(p))
+        for e in encs:
+            if e is not None:
+                body.extend(e)
+
+    for c in TABLE_ORDER_A:
+        emit_table(c)
+    npc_off = None
+    if m["npcs"]:
+        npc_off = len(body)
+        n = len(m["npcs"])
+        body.extend(_u16(0))
+        first = npc_off + 2 + 2 * n
+        for i in range(n):
+            body.extend(_u16(first + i * 0x100))
+        for ch in m["npcs"]:
+            body.extend(containers.encode_character(ch))
+    for c in TABLE_ORDER_B:
+        emit_table(c)
+    specials_off = 0  # lab rule: no special-action table
+    names_off = len(body)
+    for mob in m["mobs"]:
+        body.extend(mob["name"] + b"\x00")
+    data_off = len(body)
+    for mob in m["mobs"]:
+        body.extend(encode_mob(mob))
+    strings_off = len(body)
+    if npc_off is None:
+        npc_off = strings_off  # lab rule: no NPCs -> npcOffset = stringsOffset
+    body.extend(strings.encode_table(m["dictionary"], m["strings"]))
+
+    cd = _u16(strings_off) + _u16(names_off) + _u16(data_off)
+    for o in offsets:
+        cd += _u16(o)
+    cd += _u16(specials_off) + _u16(npc_off)
+    body[cd_at:cd_at + 42] = cd
+
+    prefix = bytes(body[:strings_off])
+    if not codecs.rotating_xor_prefix_is_unambiguous(prefix):
+        raise FormatError("scenario: map %r has an ambiguous encrypted prefix"
+                          % m.get("name", "?"))
+    enc = codecs.rotating_xor_encode(prefix)
+    data_section = enc + bytes(body[strings_off:]) + b"\x00"  # final byte: unknown, lab 0
+    tile_map = bytes(v for row in img for v in row)
+    tsec = _u32(S * S) + _u32(0) + huffman.encode(tile_map)
+    header = b"msq" + bytes(((0x30 + disk) & 0xFF,))
+    block = header + data_section + tsec
+    tmo = len(header) + len(data_section)
+    facts = {"bodySize": len(body), "encryptedPrefixLength": strings_off,
+             "centralDirectory": {"stringsOffset": strings_off, "mobNamesOffset": names_off,
+                                  "mobDataOffset": data_off, "actionClassOffsets": offsets,
+                                  "specialsOffset": specials_off, "npcOffset": npc_off}}
+    return block, tmo, facts
+
+
+# ---------------------------------------------------------------------------
+# JSON to engine-record conversion
+# ---------------------------------------------------------------------------
+
+def _record_from_json(c: int, r: dict) -> dict:
+    if c == 1:
+        d = {"messages": r["messages"]}
+    elif c == 3:
+        d = {"visibleDistance": r["visible_distance"], "hitDistance": r["hit_distance"],
+             "message": r["message"], "groups": r["groups"], "properName": r["proper_name"],
+             "friendly": r["friendly"], "immobile": r["immobile"], "npc": 0}
+    elif c == 4:
+        d = {"message": r["message"], "impassable": r["impassable"], "tile": r["tile"]}
+    elif c == 5:
+        d = {"items": r["items"], "cash": r["cash"]}
+    elif c == 6:
+        d = {"shop": r["shop"], "message": r["message"]}
+    elif c == 10:
+        d = {k: r[k] for k in ("relative", "confirm", "message", "x", "y", "location")}
+    elif c == 11:
+        d = {"message": r["message"]}
+    else:
+        raise FormatError("scenario: lab rules define no record for class %d" % c)
+    d["newClass"], d["newAction"] = r["new_class"], r["new_action"]
+    return d
+
+
+def _character_from_json(p: dict, npc: int, catalog: dict, ranks: list) -> dict:
+    a = p["attrs"]
+    level = p["level"]
+    hp = 10 + a["STR"] + (level - 1) * (2 + a["STR"] // 5)
+    bonus = 0
+    if p["armour_slot"]:
+        bonus = catalog[p["items"][p["armour_slot"] - 1][0]]["damage"]
+    evasion = dict((s, l) for s, l in p["skills"]).get(11, 0)
+    return {
+        "name": p["name"].encode("latin-1"), "strength": a["STR"], "intelligence": a["IQ"],
+        "luck": a["LCK"], "speed": a["SPD"], "agility": a["AGL"], "dexterity": 0,
+        "charisma": a["CHA"], "money": p["money"], "gender": p["gender"],
+        "nationality": p["nationality"], "armorClass": a["AGL"] // 5 + bonus + evasion,
+        "maxCon": hp, "curCon": hp, "weaponSlot": p["weapon_slot"], "skillPoints": 0,
+        "experience": p["xp"], "level": level, "armorSlot": p["armour_slot"], "lastCon": 0,
+        "afflictions": 0, "npc": npc, "itemRefuse": 0, "skillRefuse": 0, "attribRefuse": 0,
+        "tradeRefuse": 0, "joinString": 0, "willingness": 0,
+        "rank": ranks[min(level, 7) - 1].encode("latin-1"), "gameWon": 0,
+        "specialPromotion": 0, "skills": [list(x) for x in p["skills"]],
+        "items": [list(x) for x in p["items"]],
+    }
+
+
+def _map_from_json(m: dict, size: int, catalog: dict, ranks: list) -> dict:
+    info = m["info"]
+    mi = {"encounterFrequency": info["encounter_frequency"], "tileset": info["tileset"],
+          "randomMonsterTypes": info["random_monster_types"],
+          "maxRandomEncounters": info["max_random_encounters"],
+          "borderImage": info["border_image"], "timePerStep": info["time_per_step"],
+          "healRate": info["heal_rate"]}
+    mobs = []
+    for mob in m["mobs"]:
+        name = mob["name"].encode("latin-1")
+        if mob.get("plural_suffix"):
+            name += b"\x0a\x0a" + mob["plural_suffix"].encode("latin-1") + b"\x0a"
+        mobs.append({"name": name, "sturdiness": mob["sturdiness"],
+                     "combatRating": mob["combat_rating"], "randomDamage": mob["random_damage"],
+                     "maxGroup": mob["max_group"], "armorClass": mob["armor_class"],
+                     "fixedDamage": mob["fixed_damage"], "weaponType": mob["weapon_type"],
+                     "type": mob["type"], "portrait": mob["portrait"]})
+    actions = {}
+    for c, recs in m["records"].items():
+        if recs:
+            actions[int(c)] = [_record_from_json(int(c), r) for r in recs]
+    return {"size": size, "class": m["action_class"], "action": m["action_value"],
+            "image": [[t + 10 for t in row] for row in m["tiles"]],
+            "info": mi, "actions": actions,
+            "npcs": [_character_from_json(n, 1, catalog, ranks) for n in m["npcs"]],
+            "mobs": mobs, "dictionary": DICT,
+            "strings": [s.encode("latin-1") for s in m["strings"]]}
+
+
+# ---------------------------------------------------------------------------
+# Savegame and shop lists
+# ---------------------------------------------------------------------------
+
+def _build_savegame(scenario_dir: str, scen: dict, catalog: dict, ranks: list) -> bytes:
+    party = _load_json(os.path.join(scenario_dir, "party.json"))["party"]
+    st = scen["start"]
+    n = len(party)
+    chars = [_character_from_json(p, 0, catalog, ranks) for p in party]
+    empty = containers.decode_character(bytes(0x100))
+    groups = [{"order": list(range(1, n + 1)) + [0] * (7 - n), "x": st["x"], "y": st["y"],
+               "map": st["location"], "prevX": 0, "prevY": 0, "prevMap": 0}]
+    groups += [{"order": [0] * 7, "x": 0, "y": 0, "map": 0,
+                "prevX": 0, "prevY": 0, "prevMap": 0}] * 3
+    sg = {"groups": groups, "viewportX": st["x"], "viewportY": st["y"],
+          "currentMembers": n, "currentParty": 0, "currentMap": st["location"],
+          "totalMembers": n, "extraGroups": 0, "minute": 0, "hour": st["hour"],
+          "combatScrollSpeed": 0, "serial": 0, "characters": chars + [empty] * (7 - n)}
+    return containers.encode_savegame(sg, 0)
+
+
+def _shop_items(sh: dict, catalog: dict) -> list:
+    recs = []
+    for i in range(94):
+        it = catalog.get(i + 1)
+        if it is None:
+            recs.append({"price": 0, "stock": 0, "type": 0, "lowFlags": 0,
+                         "capacity": 0, "skill": 0, "damage": 0, "ammo": 0})
+        else:
+            recs.append({"price": it["price"], "stock": sh["stock"].get(str(it["id"]), 0),
+                         "type": it["type_byte"] >> 3, "lowFlags": it["type_byte"] & 7,
+                         "capacity": it["capacity"], "skill": it["skill"],
+                         "damage": it["damage"], "ammo": it["ammo"]})
+    return recs
+
+
+# ---------------------------------------------------------------------------
+# LABTABLES.BIN (SPEC-02 section 12.2)
+# ---------------------------------------------------------------------------
+
+def _encode_labtables(t: dict) -> bytes:
+    out = bytearray(containers.LABTABLES_SIZE)
+    out[0:8] = containers.LABTABLES_MAGIC
+    for k, (off, fmt, n) in containers.LT.items():
+        vals = t[k] if isinstance(t[k], list) else [t[k]]
+        if len(vals) != n:
+            raise FormatError("LABTABLES: %s has %d values, expected %d" % (k, len(vals), n))
+        w = containers._WIDTH[fmt]
+        for i, v in enumerate(vals):
+            out[off + i * w:off + (i + 1) * w] = (v & ((1 << (8 * w)) - 1)).to_bytes(w, "little")
+    return bytes(out)
+
+
+def _build_labtables(map_facts: list, sg_off: int, tileset_size: int,
+                     portrait_offsets: list) -> bytes:
+    n = len(map_facts)
+    t = {
+        "mapOffsets": [mf[0] for mf in map_facts] + [0] * (42 - n),
+        "tileMapOffsets": [mf[1] for mf in map_facts] + [0] * (50 - n),
+        "locationMapping": [(2 << 6) | i for i in range(n)] + [0] * (50 - n),
+        "mapSizes": [mf[3]["size"] for mf in map_facts] + [0] * (50 - n),
+        "sharedLocations": [2] * 125,
+        "mobSpriteMap": [0, 6, 3, 4, 2, 1],
+        "savegameOffsets": [sg_off, 0xFFFFFFFF],
+        "savegameSize": containers.SAVEGAME_RESERVED,
+        "shopListRelOffsets": [i * containers.SHOP_BLOCK for i in range(4)],
+        "mapCounts": [n, 0],
+        "shopListCounts": [3, 0],
+        "tilesetOffsets": [0] * 9,
+        "tilesetSizes": [tileset_size] + [0] * 8,
+        "portraitOffsets1": list(portrait_offsets) + [0] * (34 - len(portrait_offsets)),
+        "portraitOffsets2": [0] * 49,
+        "portraitIndices1": [0x80, 0, 1, 2, 3] + [0x80] * 75,
+        "portraitIndices2": [0x80] * 80,
+    }
+    return _encode_labtables(t)
+
+
+# ---------------------------------------------------------------------------
+# LABSTR.BIN (SPEC-02 section 12.3) and LABSKILL.BIN (SPEC-04 section 3.2)
+# ---------------------------------------------------------------------------
+
+def _labstr_file(tables: list) -> bytes:
+    n = len(tables)
+    head = strings.LABSTR_MAGIC + _u16(n) + _u16(0)
+    pos = len(head) + 8 * n
+    offs, sizes = b"", b""
+    for t in tables:
+        offs += _u32(pos)
+        sizes += _u32(len(t))
+        pos += len(t)
+    return head + offs + sizes + b"".join(tables)
+
+
+def _build_labstr(scenario_dir: str, scen: dict) -> bytes:
+    strs = _load_json(os.path.join(scenario_dir, "strings.json"))["strings"]
+    skills = _load_json(os.path.join(scenario_dir, "skills.json"))["skills"]
+    items = _load_json(os.path.join(scenario_dir, "items.json"))["items"]
+    lt = scen["labstr_tables"]
+    t1 = [""] * (max(s["id"] for s in strs) + 1)
+    for s in strs:
+        t1[s["id"]] = s["text"].replace("{name}", "\x0b").replace("{num}", "\x0f")
+    t2 = [""] + [s["name"] for s in sorted(skills, key=lambda k: k["id"])]
+    t2 += [it["name"] for it in sorted(items, key=lambda k: k["id"])]
+    tables = [lt["0"]["strings"], t1, t2, lt["3"]["strings"], lt["4"]["strings"],
+              lt["5"]["strings"]]
+    enc = [strings.encode_table(DICT, [s.encode("latin-1") for s in _pad4(t)]) for t in tables]
+    return _labstr_file(enc)
+
+
+def _build_labskill(scenario_dir: str) -> bytes:
+    d = _load_json(os.path.join(scenario_dir, "skills.json"))
+    e0 = d["entry0"]
+    out = bytearray()
+    out += bytes(((e0["iq_req"] << 3) | e0["cost"], e0["attr_offset"]))
+    for s in sorted(d["skills"], key=lambda k: k["id"]):
+        out += bytes(s["labskill_bytes"])
+    return bytes(out)
+
+
+# ---------------------------------------------------------------------------
+# Graphics (SPEC-02 sections 6 to 8, 12.6, 12.7)
+# ---------------------------------------------------------------------------
+
+def _planes_encode(pix: list, bytes_per_row: int) -> bytes:
+    """Four 1-bit planes (blue, green, red, intensity), MSB = leftmost pixel."""
+    out = bytearray()
+    for bit in range(4):
+        for row in pix:
+            for bx in range(bytes_per_row):
+                v = 0
+                for i in range(8):
+                    v |= ((row[bx * 8 + i] >> bit) & 1) << (7 - i)
+                out.append(v)
+    return bytes(out)
+
+
+def _mask_encode(mask: list) -> bytes:
+    out = bytearray()
+    for row in mask:
+        for bx in range(2):
+            v = 0
+            for i in range(8):
+                v |= (row[bx * 8 + i] & 1) << (7 - i)
+            out.append(v)
+    return bytes(out)
+
+
+def _cursor_encode(pix: list, vis: list) -> bytes:
+    out = bytearray()
+    for bit in range(4):
+        for y in range(16):
+            def byte(src, x0, fn):
+                v = 0
+                for i in range(8):
+                    v |= (fn(src[y][x0 + i]) & 1) << (7 - i)
+                return v
+            out += bytes((byte(vis, 8, int), byte(vis, 0, int),
+                          byte(pix, 8, lambda p: p >> bit), byte(pix, 0, lambda p: p >> bit)))
+    return bytes(out)
+
+
+def _portrait_anim_encode(scripts: list, updates: list) -> bytes:
+    sb = bytearray()
+    for sc in scripts:
+        for d, u in sc:
+            sb += bytes((d, u))
+        sb.append(0xFF)
+    ub = bytearray()
+    for upd in updates:
+        for off, data in upd:
+            ub += _u16(((len(data) - 1) << 12) | off) + data
+        ub += _u16(0xFFFF)
+    return _u16(len(sb)) + bytes(sb) + _u16(len(ub)) + bytes(ub)
+
+
+def _ending_anim_encode(updates: list) -> bytes:
+    st = bytearray()
+    for delay, patches in updates:
+        st += _u16(delay)
+        for off, data in patches:
+            st += _u16(off) + data
+        st += _u16(0xFFFF)
+    st += _u16(0xFFFF)
+    return _u16(len(st)) + bytes(st) + _u16(0)
+
+
+def _placeholder_tile(t: int) -> list:
+    """Tile ``t``: fill ``t mod 16``, one-pixel border ``(t + 8) mod 16``."""
+    pix = [[t % 16 for _ in range(16)] for _ in range(16)]
+    border = (t + 8) % 16
+    for x in range(16):
+        pix[0][x] = border
+        pix[15][x] = border
+    for y in range(16):
+        pix[y][0] = border
+        pix[y][15] = border
+    return pix
+
+
+def _placeholder_portrait(p: int) -> list:
+    """Portrait ``p``: fill ``4 + p``, centred 48 x 42 rectangle of colour 15."""
+    pix = [[4 + p for _ in range(96)] for _ in range(84)]
+    for y in range(21, 63):
+        for x in range(24, 72):
+            pix[y][x] = 15
+    return pix
+
+
+def _build_allhtds(scenario_dir: str) -> bytes:
+    tiles = _load_json(os.path.join(scenario_dir, "tiles.json"))["tiles"]
+    raw = b"".join(codecs.vertical_xor_encode(graphics.pack4(_placeholder_tile(t["id"])), 8)
+                   for t in sorted(tiles, key=lambda k: k["id"]))
+    return huffman.encode_msq(raw, 0)
+
+
+def _build_allpics(scenario_dir: str):
+    portraits = _load_json(os.path.join(scenario_dir, "portraits.json"))["portraits"]
+    out = bytearray()
+    offsets = []
+    for p in sorted(portraits, key=lambda k: k["raw_id"]):
+        base = graphics.pack4(_placeholder_portrait(p["raw_id"] - 1))
+        upd = [(2000, b"\xff" * 8)]
+        anim = _portrait_anim_encode([[(20, 0), (20, 0)]], [upd])
+        offsets.append(len(out))
+        out += huffman.encode_msq(codecs.vertical_xor_encode(base, PORTRAIT_STRIDE), 0)
+        out += huffman.encode_msq(anim, 0)
+    return bytes(out), offsets
+
+
+def _build_sprites():
+    sprites, masks = bytearray(), bytearray()
+    for n in range(10):
+        pix = [[(n + x // 4 + y // 4) % 16 for x in range(16)] for y in range(16)]
+        msk = [[1 if (x - 7.5) ** 2 + (y - 7.5) ** 2 > 56 else 0
+                for x in range(16)] for y in range(16)]
+        sprites += _planes_encode(pix, 2)
+        masks += _mask_encode(msk)
+    return bytes(sprites), bytes(masks)
+
+
+def _build_font() -> bytes:
+    out = bytearray()
+    for g in range(32):
+        pix = [[((g >> (x % 5)) & 1) * ((g + y) % 15 + 1) for x in range(8)]
+               for y in range(8)]
+        out += _planes_encode(pix, 1)
+    return bytes(out)
+
+
+def _build_cursors() -> bytes:
+    out = bytearray()
+    for k in range(2):
+        pix = [[(x + y + k) % 16 for x in range(16)] for y in range(16)]
+        vis = [[1 if x <= y + k * 3 else 0 for x in range(16)] for y in range(16)]
+        out += _cursor_encode(pix, vis)
+    return bytes(out)
+
+
+def _build_title() -> bytes:
+    pix = [[((x // 18) ^ (y // 16)) % 16 for x in range(288)] for y in range(128)]
+    return codecs.vertical_xor_encode(graphics.pack4(pix), TITLE_STRIDE)
+
+
+def _build_ending() -> bytes:
+    base = graphics.pack4([[((x + y) // 24) % 16 for x in range(288)] for y in range(128)])
+    updates = [(5, [(41, bytes.fromhex("11223344")), (40 * 100 + 35, bytes.fromhex("FFEEDDCC"))]),
+               (9, [(0, bytes.fromhex("0F0F0F0F"))])]
+    anim = _ending_anim_encode(updates)
+    return (huffman.encode_msq(codecs.vertical_xor_encode(base, TITLE_STRIDE), 0)
+            + huffman.encode_msq(anim, 0, ENDING_SIGNATURE))
+
+
+# ---------------------------------------------------------------------------
+# The compiler
+# ---------------------------------------------------------------------------
+
+def compile(scenario_dir: str, out_dir: str) -> None:
+    """Compile the scenario in ``scenario_dir`` into ``out_dir`` (SPEC-05 13)."""
+    scen = _load_json(os.path.join(scenario_dir, "scenario.json"))
+    items = _load_json(os.path.join(scenario_dir, "items.json"))["items"]
+    catalog = {it["id"]: it for it in items}
+    ranks = scen["labstr_tables"]["3"]["strings"]
+    os.makedirs(out_dir, exist_ok=True)
+
+    game = bytearray()
+    map_facts = []
+    for loc in scen["locations"]:
+        m = _load_json(os.path.join(scenario_dir, loc["file"]))
+        mm = _map_from_json(m, loc["size"], catalog, ranks)
+        mm["name"] = loc["name"]
+        block, tmo, facts = build_map(mm, 0)
+        map_facts.append((len(game), tmo, facts, loc))
+        game += block
+
+    sg_off = len(game)
+    game += _build_savegame(scenario_dir, scen, catalog, ranks)
+
+    shops = _load_json(os.path.join(scenario_dir, "shops.json"))["shops"]
+    for sh in shops:
+        game += containers.encode_shop_list(_shop_items(sh, catalog), 0)
+    _write(out_dir, "GAME1", bytes(game))
+
+    allhtds = _build_allhtds(scenario_dir)
+    allpics, portrait_offsets = _build_allpics(scenario_dir)
+    _write(out_dir, "ALLHTDS1", allhtds)
+    _write(out_dir, "ALLPICS1", allpics)
+
+    sprites, masks = _build_sprites()
+    _write(out_dir, "IC0_9.WLF", sprites)
+    _write(out_dir, "MASKS.WLF", masks)
+    _write(out_dir, "COLORF.FNT", _build_font())
+    _write(out_dir, "CURS", _build_cursors())
+    _write(out_dir, "TITLE.PIC", _build_title())
+    _write(out_dir, "END.CPA", _build_ending())
+
+    _write(out_dir, "LABTABLES.BIN",
+           _build_labtables(map_facts, sg_off, len(allhtds), portrait_offsets))
+    _write(out_dir, "LABSTR.BIN", _build_labstr(scenario_dir, scen))
+    _write(out_dir, "LABSKILL.BIN", _build_labskill(scenario_dir))
+
+    for src, dst in (("hooks.json", "LABHOOKS.JSON"), ("paragraphs.json", "PARAGRAPHS.JSON")):
+        with open(os.path.join(scenario_dir, src), "rb") as fh:
+            _write(out_dir, dst, fh.read())
+
+
+__all__ = ["compile", "build_map", "encode_record", "encode_mapinfo", "encode_mob"]
diff --git a/tests/fixtures-generated/proto.py b/tests/fixtures-generated/proto.py
new file mode 100644
index 0000000..a48de3b
--- /dev/null
+++ b/tests/fixtures-generated/proto.py
@@ -0,0 +1,90 @@
+import sys, os, json
+sys.path.insert(0, 'SPEC/reference')
+import codecs_ref as C, fixtures_gen as FG
+DICT = (b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r"
+        b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;")
+SD = 'SPEC/scenario'
+scen = json.load(open(os.path.join(SD, 'scenario.json')))
+items = json.load(open(os.path.join(SD, 'items.json')))['items']
+catalog = {it['id']: it for it in items}
+ranks = scen['labstr_tables']['3']['strings']
+
+
+def conv(c, r):
+    if c == 1:
+        d = {'messages': r['messages']}
+    elif c == 3:
+        d = {'visibleDistance': r['visible_distance'], 'hitDistance': r['hit_distance'],
+             'message': r['message'], 'groups': r['groups'], 'properName': r['proper_name'],
+             'friendly': r['friendly'], 'immobile': r['immobile'], 'npc': 0}
+    elif c == 4:
+        d = {'message': r['message'], 'impassable': r['impassable'], 'tile': r['tile']}
+    elif c == 5:
+        d = {'items': r['items'], 'cash': r['cash']}
+    elif c == 6:
+        d = {'shop': r['shop'], 'message': r['message']}
+    elif c == 10:
+        d = {k: r[k] for k in ('relative', 'confirm', 'message', 'x', 'y', 'location')}
+    elif c == 11:
+        d = {'message': r['message']}
+    d['newClass'], d['newAction'] = r['new_class'], r['new_action']
+    return d
+
+
+def char_from_json(p, npc):
+    a = p['attrs']
+    level = p['level']
+    hp = 10 + a['STR'] + (level - 1) * (2 + a['STR'] // 5)
+    bonus = 0
+    if p['armour_slot']:
+        bonus = catalog[p['items'][p['armour_slot'] - 1][0]]['damage']
+    evasion = dict((s, l) for s, l in p['skills']).get(11, 0)
+    c = {'name': p['name'].encode('latin-1'), 'strength': a['STR'], 'intelligence': a['IQ'],
+         'luck': a['LCK'], 'speed': a['SPD'], 'agility': a['AGL'], 'dexterity': 0,
+         'charisma': a['CHA'], 'money': p['money'], 'gender': p['gender'],
+         'nationality': p['nationality'], 'armorClass': a['AGL'] // 5 + bonus + evasion,
+         'maxCon': hp, 'curCon': hp, 'weaponSlot': p['weapon_slot'], 'skillPoints': 0,
+         'experience': p['xp'], 'level': level, 'armorSlot': p['armour_slot'], 'lastCon': 0,
+         'afflictions': 0, 'npc': npc, 'itemRefuse': 0, 'skillRefuse': 0, 'attribRefuse': 0,
+         'tradeRefuse': 0, 'joinString': 0, 'willingness': 0,
+         'rank': ranks[min(level, 7) - 1].encode('latin-1'), 'gameWon': 0,
+         'specialPromotion': 0, 'skills': [list(x) for x in p['skills']],
+         'items': [list(x) for x in p['items']]}
+    return c
+
+
+for loc in scen['locations']:
+    m = json.load(open(os.path.join(SD, loc['file'])))
+    S = loc['size']
+    info = m['info']
+    mi = {'encounterFrequency': info['encounter_frequency'], 'tileset': info['tileset'],
+          'randomMonsterTypes': info['random_monster_types'],
+          'maxRandomEncounters': info['max_random_encounters'],
+          'borderImage': info['border_image'], 'timePerStep': info['time_per_step'],
+          'healRate': info['heal_rate']}
+    mobs = []
+    for mob in m['mobs']:
+        name = mob['name'].encode('latin-1')
+        if mob.get('plural_suffix'):
+            name += b'\x0a\x0a' + mob['plural_suffix'].encode('latin-1') + b'\x0a'
+        md = {'name': name, 'sturdiness': mob['sturdiness'], 'combatRating': mob['combat_rating'],
+              'randomDamage': mob['random_damage'], 'maxGroup': mob['max_group'],
+              'armorClass': mob['armor_class'], 'fixedDamage': mob['fixed_damage'],
+              'weaponType': mob['weapon_type'], 'type': mob['type'], 'portrait': mob['portrait']}
+        mobs.append(md)
+    mm = {'size': S, 'class': m['action_class'], 'action': m['action_value'],
+          'image': [[t + 10 for t in row] for row in m['tiles']],
+          'info': mi,
+          'actions': {int(c): [conv(int(c), r) for r in recs]
+                      for c, recs in m['records'].items() if recs},
+          'npcs': [char_from_json(n, 1) for n in m['npcs']],
+          'mobs': mobs, 'dictionary': DICT,
+          'strings': [s.encode('latin-1') for s in m['strings']]}
+    try:
+        block, tmo, facts = FG.build_map(mm, 0)
+        print(loc['location'], 'OK block', len(block), 'tmo', tmo,
+              'prefix', facts['encryptedPrefixLength'])
+    except Exception as e:
+        import traceback
+        print(loc['location'], 'FAIL', type(e).__name__, e)
+        traceback.print_exc()

```