# SPEC-03: maps

Status: frozen for PREREG-W1 build, version 1, 21 Oct 2026.
Scope: the map block inside GAME1 and GAME2, as far as public sources document
it, plus the lab's own non-parity rules for everything they leave open.
Codecs are in SPEC-01, containers and tables in SPEC-02.

`map.md` itself is marked work in progress and incomplete. This file keeps a
strict line between three kinds of statement:

- documented: cited to `map.md` or another wastelib doc;
- source-only: present in wastelib or wllib code but not in any doc, cited to
  the file ([WL-SRC] = wastelib commit `eb4ed4d`, `src/main/game/...`;
  [WLL] = badvassal/wllib `decode/...`); layouts are usable, runtime meaning is
  UNKNOWN unless stated;
- lab rule: section 9 only, labelled L-xx, non-parity.

## 1. Engine column

As in SPEC-02: READ = must decode and expose; IGNORE = may skip, must not fail;
UNKNOWN = meaning undocumented, preserve bytes, do not interpret, do not fail.

## 2. Locating a map

Maps are found only through tables (`map.md`, `game.md`, `exe.md`):
`mapOffsets`, `mapSizes` (32 or 64) and `tileMapOffsets`, the last two indexed
by location index. Resolution from a location index is SPEC-02 section 3.4.
For lab data the tables come from LABTABLES.BIN (SPEC-02 section 12.2).

Inputs to the map reader: the GAME file bytes, `offset`, `mapSize`,
`tileMapOffset`.

## 3. Block layout

Source: `map.md`.

| Block offset | Size | Meaning | Engine |
| --- | --- | --- | --- |
| 0x00 | 4 | `msq0` (GAME1) or `msq1` (GAME2) | READ, validate |
| 0x04 | 1 | xor1 | READ |
| 0x05 | 1 | xor2 | READ |
| 0x06 | tileMapOffset - 7 | map-data body (encrypted prefix + plain suffix) | READ |
| tileMapOffset - 1 | 1 | unknown byte before the tile-map section | UNKNOWN |
| tileMapOffset | 4 | u32 tileMapDecodedSize, must equal mapSize x mapSize | READ, validate |
| tileMapOffset + 4 | 4 | u32 unknown | UNKNOWN |
| tileMapOffset + 8 | variable | Huffman bitstream of the tile map | READ |

`bodySize = tileMapOffset - 7`. All offsets inside the body (central directory,
action tables, NPC pointers) are absolute offsets from the first body byte,
that is from block offset 0x06 (`map.md`). [WLL] calls the decrypted part the
"secure section" and measures its pointers from the same byte.

The block length is not stored; the block ends at the byte boundary after the
last tile-map byte (`huffman.md`). The engine must not depend on the block
length.

## 4. Decryption

Prefix mode of SPEC-01 section 2.6 over the `bodySize` body bytes (`map.md`,
`rotating-xor.md`): decrypt until the running checksum first equals
`xor1 | xor2 << 8`, the rest of the body is plain.

In shipped maps the encrypted prefix ends exactly at `stringsOffset`
([WL-SRC] `GameMap.ts` comment: the strings section "is not encrypted but the
decrypt algorithm automatically stops right before it"). wllib relies on the
same fact: it only accepts a checksum match followed by the raw bytes `20 65`,
the first two bytes of the string dictionary ([WLL] `msq/read.go`, and
`decode/carve.go` reads the strings area from the start of the plain part).

Engine: decrypt with the wastelib rule, then validate
`prefixLength == stringsOffset`; a mismatch is reported as a warning for
parity data and as an error for lab data (L-EN2).

## 5. Map-data body, fixed part

### 5.1 Layout

Source: `map.md`.

| Body offset | Size | Section |
| --- | --- | --- |
| 0 | S x S / 2 | action-class map |
| S x S / 2 | S x S | action map |
| 3 x S x S / 2 | 42 | central directory |
| 3 x S x S / 2 + 42 | 50 | map-info block |
| 3 x S x S / 2 + 92 | variable | variable sections (section 6) |

`S` = mapSize. The map-info block starts at 0x062A for S = 32 and 0x182A for
S = 64 (`map.md`); the variable area starts at 0x065C and 0x185C.

### 5.2 Action-class map

One 4-bit action class per cell, two horizontally adjacent cells per byte,
row-major (`map.md`):

```text
byte  = body[(y * S + x) >> 1]
class = (x even) ? byte >> 4 : byte & 0x0F
```

High nibble = even x, low nibble = odd x (`map.md`; [WL-SRC] `GameMap.ts`
does the same). wllib does the opposite: low nibble = even x ([WLL]
`decode/mapdata.go`). Engine rule: follow `map.md`. See section 10.

### 5.3 Action map

One byte per cell, row-major, `body[S*S/2 + y*S + x]`: the action parameter
for the cell's class (`map.md`). How the parameter is used is source-only
(section 8.1).

### 5.4 Central directory (42 bytes)

Source: `map.md`; identical field order in [WLL] `decode/centraldir.go`.

| Offset | Type | Field | Engine |
| --- | --- | --- | --- |
| +0x00 | u16 | stringsOffset | READ |
| +0x02 | u16 | mobNamesOffset | READ |
| +0x04 | u16 | mobDataOffset | READ |
| +0x06 | u16[16] | actionClassOffsets, one per class 0 to 15 | READ (layout source-only, section 8) |
| +0x26 | u16 | specialsOffset | READ offset; table meaning UNKNOWN |
| +0x28 | u16 | npcOffset | READ |

All values are absolute body offsets and must point inside the body
(`map.md`). An offset of 0 means "absent" for action tables and specials
([WL-SRC] `GameMap.ts` skips class tables with offset 0; [WLL] treats
specials offset 0 as empty).

### 5.5 Map-info block (50 bytes)

Source: `map.md`, matching [WL-SRC] `MapInfo.ts`.

| Offset | Type | Meaning | Engine |
| --- | --- | --- | --- |
| +0x00 | u8 | unknown, observed 0 in all shipped maps | UNKNOWN |
| +0x01 | u8 | unknown, observed 0 in all shipped maps | UNKNOWN |
| +0x02 | u8 | map size, 32 or 64; must equal the table value | READ, validate |
| +0x03 | u8 | unknown | UNKNOWN |
| +0x04 | u8 | unknown | UNKNOWN |
| +0x05 | u8 | random encounter frequency | READ |
| +0x06 | u8 | tileset index (global tileset id, SPEC-02 section 6) | READ |
| +0x07 | u8 | number of random monster types | READ |
| +0x08 | u8 | maximum concurrent random encounters | READ |
| +0x09 | u8 | border-tile image index | READ |
| +0x0A | u16 | time per step | READ (unit UNKNOWN) |
| +0x0C | u8 | heal rate | READ (unit UNKNOWN) |
| +0x0D | u8[37] | combat string ids | READ raw (grouping UNKNOWN) |

wllib reads +0x0A and +0x0B as two bytes "SecRate" and "MinRate", +0x0D as
18 u16 string ids followed by one padding byte, and calls bytes +0x00, +0x01,
+0x03, +0x04 padding ([WLL] `decode/mapinfo.go`). See section 10. The
frequency, heal rate and time units, and how combat string ids select strings,
are UNKNOWN.

## 6. Variable sections

### 6.1 Order

The order of sections after the map info is not documented. wllib assigns its
central-directory pointers a priority list, used to decide which section owns a
pointer when two share a value: action tables 0 to 7, table 15, NPC table,
tables 8 to 14, specials, monster names, monster data, strings ([WLL]
`decode/centraldir.go`, constants `CDPtrIdx...`). That list reads as the
physical order in shipped files, but neither source says so: physical order is
UNKNOWN for parity data. `map.md` does fix two adjacencies: monster data ends
where strings begin (`numMobs = (stringsOffset - mobDataOffset) / 8`) and
strings are the last body section before the unknown byte. The engine must
locate every section by its offset, never by order. Lab data uses the wllib
order (L-EN1).

### 6.2 Action-class tables (source-only layout)

Not in `map.md` ("detailed substructure is currently unknown"). Layout from
[WL-SRC] `Actions.ts` and [WLL] `gen/table.go`:

```text
at actionClassOffsets[c]:
    u16 pointer[0], pointer[1], ...      absolute body offsets; 0 = no record
    records ...
```

The pointer list has no count. wastelib reads pointers until its read position
reaches the smallest non-zero pointer read so far. wllib reads until the first
non-zero pointer `p` and takes `(p - tableStart) / 2` pointers, which assumes
pointers ascend. Records are variable length and parsed per class
(section 8). wastelib clears the class 15 offset when map info byte +0x08
(maximum random encounters) is 0, because shipped maps can carry a stale
pointer there ([WL-SRC] `GameMap.ts`).

### 6.3 Special-action table

At `specialsOffset`. wastelib reads 128 u16 values ([WL-SRC] `GameMap.ts`)
and passes them to the class readers without using them; wllib keeps the
bytes raw and labels class 6 "special actions" in one comment and "shop" in
another ([WLL] `decode/specialactions.go`, `decode/action/action.go`).
Meaning, length and format are UNKNOWN. Engine: IGNORE for parity; lab data
has none (L-EN3).

### 6.4 NPC section

Source: `map.md`.

- If the u16 at `npcOffset` is not 0x0000, the map has no NPCs.
- Otherwise a pointer table follows the 0x0000: `npcPointer[0],
  npcPointer[1], ...`, absolute body offsets, no count; the table ends when the
  read position reaches the smallest pointer.
- Each pointer addresses a 0x100-byte character record (SPEC-02 section 4.4).

wllib treats `npcOffset == 0`, or an `npcOffset` equal to a higher-priority
section's offset, as "no NPCs" ([WLL] `decode/decode.go`, `carve.go`). How the
game links an NPC to a map cell or encounter is UNKNOWN (encounter records
carry a 4-bit `npc` field, section 8.5).

Engine: READ.

### 6.5 Monster names

At `mobNamesOffset`: `numMobs` NUL-terminated names, where
`numMobs = (stringsOffset - mobDataOffset) / 8` (`map.md`). Names use the 0x0A
two-way selector of SPEC-02 section 9.2 for singular and plural, for example
`rad rat<0A><0A>s<0A>` = "rad rat" / "rad rats" ([WLL]
`decode/monsternames.go` splits names on 0x0A into start, singular, plural,
end).

Engine: READ.

### 6.6 Monster data

At `mobDataOffset`: `numMobs` records of 8 bytes (`map.md`; same fields in
[WLL] `decode/monsterdata.go`):

| Offset | Bits | Meaning | Engine |
| --- | --- | --- | --- |
| +0 | u16 | sturdiness (HP and XP seed) | READ |
| +2 | u8 | combat rating | READ |
| +3 | u8 | random damage in D6 | READ |
| +4 | high nibble | maximum group size | READ |
| +4 | low nibble | armor class (also the XP multiplier offset) | READ |
| +5 | high nibble | fixed damage | READ |
| +5 | low nibble | weapon type | READ |
| +6 | u8 | monster type (1 animal, 2 mutant, 3 humanoid, 4 cyborg, 5 robot: `exe.md`, [WL-SRC] `MobType.ts`) | READ |
| +7 | u8 | portrait index (raw portrait id, SPEC-02 section 7.1) | READ |

Documented derived values (`map.md`):

```text
hitPoints  = floor(sturdiness / 4) + ((rnd(sturdiness >> 8) << 8) | rnd(sturdiness & 0xFF))
rnd(0) = 0, rnd(1) = 1, rnd(n >= 2) = uniform integer in 1..n
experience = sturdiness * (armorClass + 1)
```

`map.md` writes the roll as `rnd(highByte)` and `rnd(lowByte)` without naming
the operand; [WL-SRC] `Mob.ts` takes them as the high and low byte of
sturdiness, as written above. Weapon-type values and the use of combat rating
are UNKNOWN.

### 6.7 Strings

At `stringsOffset`: one compressed string table (SPEC-02 section 9.1), plain
(not encrypted). String indices are group x 4 + slot. How action records
number their message indices (0-based, 1-based, or offset) is UNKNOWN for
parity data (L-MS1 for lab data).

Engine: READ.

## 7. Tile map

Source: `map.md`, `huffman.md`.

- At `tileMapOffset`: u32 decoded size (must be S x S), u32 unknown, then a
  Huffman bitstream decoding to exactly S x S bytes.
- Not vertical-XOR coded.
- Byte `y * S + x` is the image index of cell (x, y).
- Image 0 to 9: sprite from IC0_9.WLF (with MASKS.WLF). Image 10 and up: tile
  `image - 10` of the tileset named in map info +0x06.

Final cell record (`map.md`): `{actionClass (5.2), action (5.3), image (7)}`.

Engine: READ.

## 8. Action records (source-only layouts)

Class names and record layouts below come from code, not from docs. They are
listed so the lab encoding can stay compatible and a parity loader can reuse
them. Runtime semantics are UNKNOWN unless a lab rule (section 9) defines them
for lab data.

### 8.1 Action byte

wastelib stores the tile's action byte (`MapTile.getAction`) and each class's
records as a list addressed by index (`Actions.getAction(index)`) ([WL-SRC]).
Using the action byte as the 0-based index into the class's pointer list is the
evident link, but no source states it: UNKNOWN for parity data, adopted by
L-AC2 for lab data.

### 8.2 Class numbers

| Class | wastelib name ([WL-SRC] `ActionClass.ts`) | wllib | Record layout known |
| --- | --- | --- | --- |
| 0 | NONE | | no table |
| 1 | PRINT | | yes (8.4) |
| 2 | CHECK | | yes (8.6) |
| 3 | FIXED_ENCOUNTER | | yes (8.5) |
| 4 | MASK | | yes (8.7) |
| 5 | LOOT | loot table ([WLL] `action/loot.go`) | yes, wllib only (8.8) |
| 6 | SPECIAL | "shop" (`action.go` `IDShop = 6`) and "special actions" (`specialactions.go`) | no: UNKNOWN |
| 7 | UNKNOWN$07 | | no: UNKNOWN |
| 8 | DIALOG | | no: UNKNOWN |
| 9 | RAD | | no: UNKNOWN |
| 10 | TRANSITION | transition table ([WLL] `action/transition.go`) | yes (8.9) |
| 11 | BLOCKED | | yes (8.10) |
| 12 | ALTER | | no: UNKNOWN |
| 13 | UNKNOWN$0D | | no: UNKNOWN |
| 14 | UNKNOWN$0E | | no: UNKNOWN |
| 15 | RANDOM_ENCOUNTER | | yes, same as class 3 (8.5) |

### 8.3 Common tail

Most records end with a replacement for the cell ([WL-SRC], all action
readers; [WLL] `transition.go`):

```text
u8 newActionClass
u8 newAction          present only if newActionClass < 253
```

`newActionClass == 255` means "no replacement" ([WL-SRC] maps it to null).
Values 253 and 254 carry no newAction byte; their meaning is UNKNOWN. When the
replacement is applied (before or after the action, once or every time) is
UNKNOWN.

### 8.4 PRINT (class 1)

```text
u8 message[]      bit 7 set on the last entry; low 7 bits = message index
tail (8.3)
```

[WL-SRC] `actions/PrintAction.ts`.

### 8.5 FIXED_ENCOUNTER (class 3) and RANDOM_ENCOUNTER (class 15)

| Offset | Meaning |
| --- | --- |
| +0 | visible distance |
| +1 | hit distance |
| +2 | message index |
| +3 | monster index 1 |
| +4 | bit 7 = random group size flag 1; bits 0 to 6 = maximum group size 1 |
| +5, +6 | monster index 2, flags and size 2 |
| +7, +8 | monster index 3, flags and size 3 |
| +9 | bit 0 proper name, bit 1 friendly, bit 2 immobile, bit 3 UNKNOWN, bits 4 to 7 NPC number |
| +10 | tail (8.3) |

[WL-SRC] `actions/EncounterAction.ts`. Base of the monster index and of the
NPC number is UNKNOWN.

### 8.6 CHECK (class 2)

| Offset | Meaning |
| --- | --- |
| +0 | flags: 0x80 passable, 0x40 auto check, 0x20 party, 0x10 damage all, 0x08 per-check replacements follow, 0x04 pass all, 0x02 UNKNOWN, 0x01 bypass armor |
| +1 | start message index |
| +2 | pass message index |
| +3 | fail message index |
| +4, +5 | pass newActionClass, newAction (both always present) |
| +6, +7 | fail newActionClass, newAction (both always present) |
| +8 | bit 7 fixed modifier; bits 0 to 6 modifier target |
| +9 | modifier, sign and magnitude: bit 7 = negative, bits 0 to 6 = value |
| +10 | checks: `(type << 5 | difficulty, value)` pairs until a byte 0xFF; type 0 skill, 1 item, 2 attribute, 3 members, 4 money ([WL-SRC] `CheckType.ts`) |
| after 0xFF | if flag 0x08: one `(newActionClass, newAction)` pair per check |

[WL-SRC] `actions/CheckAction.ts`, `Check.ts`. Check resolution rules (roll,
difficulty scale) are UNKNOWN.

### 8.7 MASK (class 4)

```text
u8 message index
u8 bit 7 = impassable; bits 0 to 6 = tile
tail (8.3)
```

[WL-SRC] `actions/MaskAction.ts`. What "tile" refers to (image index, tileset
index, offset) is UNKNOWN.

### 8.8 LOOT (class 5), wllib only

```text
u8 newActionClass      always present
u8 newAction           always present
entries until a byte 0xFF:
    0xDE u16 amount    fixed cash
    0x5E u16 amount    random cash
    otherwise u8 (bit 7 = fixed, bits 0 to 6 = item id), u8 amount
```

At most one cash entry ([WLL] `action/loot.go`). wastelib has no reader for
class 5 ([WL-SRC] `Actions.ts` logs "unhandled action class").

### 8.9 TRANSITION (class 10)

| Offset | Meaning |
| --- | --- |
| +0 | bit 7 relative, bit 6 confirm, bits 0 to 5 message index |
| +1 | target X |
| +2 | target Y |
| +3 | target location; 255 = previous location |
| +4 | tail (8.3) |

[WL-SRC] `actions/TransitionAction.ts` (X and Y signed bytes; 255 returned as
null, "previous map"); [WLL] `action/transition.go` (X and Y unsigned;
`LocationPrevious = 255` in `defs/defs.go`; targets of 128 and above other than
255 are "derelict buildings", consistent with the shared-location table in
SPEC-02 section 3.3).

### 8.10 BLOCKED (class 11)

```text
u8 message index
tail (8.3)
```

[WL-SRC] `actions/BlockedAction.ts`.

## 9. Lab rules v1 (non-parity)

Everything in this section is a lab decision. It is valid only for lab data
(files listed in SPEC-02 section 12.1). It never contradicts sections 3 to 8:
the lab uses the documented block layout, the documented 4-bit class map and
1-byte action map, the documented central directory, and, where a
source-only record layout exists, that layout byte for byte. A future parity
loader replaces the semantics below, not the decoders.

### 9.1 Lab action classes

| Class | Lab name | Record | Passable |
| --- | --- | --- | --- |
| 0 | WALKABLE | none; action byte must be 0 | yes |
| 1 | PARAGRAPH / MESSAGE trigger | PRINT layout (8.4) | yes |
| 3 | ENCOUNTER trigger | encounter layout (8.5) | yes |
| 4 | DOOR | MASK layout (8.7) | if not impassable |
| 5 | LOOT | wllib loot layout (8.8) | yes |
| 6 | SHOP | lab layout (9.4) | yes |
| 10 | TRANSITION | transition layout (8.9) | yes |
| 11 | BLOCKED | BLOCKED layout (8.10) | no |
| 2, 7, 8, 9, 12, 13, 14, 15 | reserved | none in lab data | yes, no effect |

- L-AC1: lab encoders never write the reserved classes. If the engine meets one
  in lab data it treats the cell as WALKABLE and logs a warning naming the
  class, map and cell.
- The classes keep their wastelib numbers so a parity loader can reuse the
  same records (class 6 is the one exception: wllib's "shop" naming supports
  it, wastelib calls it SPECIAL).

### 9.2 Action byte and tables

- L-AC2: the action byte is the 0-based index into the class's pointer list at
  `actionClassOffsets[class]` (section 6.2).
- L-AC3: in lab tables pointer 0 is always 0x0000. Action byte 0 therefore
  means "no record": the class default applies (WALKABLE moves, BLOCKED blocks
  silently). Records use slots 1, 2, 3, ...
- L-AC4: non-zero pointers ascend and records are stored in pointer order right
  after the pointer list, so both the wastelib and the wllib pointer-list rules
  (section 6.2) find the same list length.
- L-AC5: an action byte at or beyond the pointer-list length, or a null pointer
  for a class that needs a record (1, 3, 5, 6, 10), is a data error in lab data.
- L-AC6: a class with no records has `actionClassOffsets[class] = 0`.

### 9.3 Tail

- L-TL1: `newActionClass` 0 to 15 replaces the cell's class and action byte with
  `(newActionClass, newAction)` after the action has fired once; 255 changes
  nothing; lab encoders never write 16 to 254. The engine treats 16 to 254 in
  lab data as 255 and logs a warning.
- L-TL2: replacements are part of the game state and are saved with it; the
  base map files are never modified.

### 9.4 SHOP record (class 6, lab layout)

```text
u8 shop list number (SPEC-02 rule L-SH3)
u8 message index
tail (8.3)
```

### 9.5 Messages and monsters

- L-MS1: a message index `m` selects map string `m` (0-based, group x 4 +
  slot). Lab maps keep string 0 empty, so `m = 0` shows nothing.
- L-MS2: messages are shown in order; a 0x06 control byte waits for a key.
  PRINT records may hold the text "Read paragraph N."; the paragraph book is a
  separate lab document, outside these formats. This is the lab's paragraph
  trigger.
- L-MB1: in encounter records, monster index 0 = empty slot, `n >= 1` = map
  monster `n - 1`.
- L-MB2: group size: if the random flag is set, `rnd(size)` with `rnd` from
  section 6.6; otherwise exactly `size`; if `size` is 0 in a used slot, use the
  monster's own maximum group size nibble.
- L-MB3: lab encoders write the encounter NPC number and bit 3 of the flag
  byte as 0. Visible distance, hit distance, proper name and immobile are
  written as data; the lab v1 engine exposes them and ignores them.

### 9.6 Movement and triggers

The party occupies one cell. A move targets the adjacent cell `(nx, ny)`.

1. Out of bounds (`nx` or `ny` outside 0 to S-1): blocked, no message (L-MV1).
2. Look up the target cell's class `c` and action byte `a`, and record `r`
   (null if `a = 0`).
3. Act by class:

| Class | Effect |
| --- | --- |
| 0 | move |
| 11 | do not move; if `r` and `r.message != 0`, show it; apply tail |
| 4 | if `r.impassable`: do not move, show `r.message`. Else: set the cell image to `r.tile`, move, show `r.message` if non-zero, apply tail |
| 1 | move; show every message of `r`; apply tail |
| 3 | move; raise an encounter event with the resolved groups (9.5) and `r.friendly`; when the engine reports the event resolved (combat won, or friendly), apply tail |
| 5 | move; give each item to the first party member with a free item slot (fixed: `amount` as the status byte; random: `rnd(amount)`); add cash (fixed: `amount`; random: `rnd(amount)`) to the active character's money; apply tail |
| 6 | move; show `r.message`; open shop list `r.shop` |
| 10 | see 9.7 |
| reserved | move; warning (L-AC1) |

- L-MV2: passability depends only on the class and the DOOR flag, never on the
  tile image.
- L-MV3: combat, item use, skills and checks are outside this spec. The engine
  exposes the encounter event and a call to resolve it.

### 9.7 Transitions and locations

- L-TR1: entering a TRANSITION cell: if `confirm` is set, show the message and
  ask yes or no; on no, the party stays where it was before the move. If
  `confirm` is clear and the message is non-zero, show it.
- L-TR2: target location `t`:
  - `t = 255`: previous location: go to the active party group's previous
    location, X and Y (savegame group bytes +0x0D, +0x0B, +0x0C); the record's
    X and Y are ignored.
  - `128 <= t <= 252`: replace `t` with `sharedLocations[t - 128]`
    (SPEC-02 section 3.3), then continue.
  - otherwise `t` is a location index resolved by SPEC-02 section 3.4; a
    location code of 0 is a data error.
- L-TR3: absolute (`relative` clear): the target cell is `(x, y)` read as
  unsigned bytes. Relative: the target cell is the transition cell's own
  coordinates plus `(x, y)` read as signed bytes, on the target location.
- L-TR4: before a transition to any `t != 255`, the engine stores the current
  location and the cell the party occupied before stepping onto the
  transition cell in the group's previous fields, so a return does not land on
  the exit cell.
- L-TR5: the target cell must be inside the target map, else data error.
  Arriving on the target cell does not fire that cell's own action.
- L-TR6: transitions within one location (target location equals the current
  one) move the party without reloading the map.

### 9.8 Map info, images and drawing

- L-MI1: lab maps write map-info bytes +0x00, +0x01, +0x03, +0x04 and all 37
  combat string bytes as 0.
- L-MI2: time per step: low byte = seconds, high byte = minutes added to the
  game clock per step. (This reading agrees with wllib's two-byte view and with
  wastelib's u16 view of the same bytes.)
- L-MI3: lab v1 has no random encounters: frequency, random monster types and
  maximum random encounters are 0, and class 15 is absent.
- L-MI4: heal rate is read and exposed but not used by lab v1.
- L-MI5: cells outside the map are drawn with the border image index from map
  info +0x09.
- L-IM1: images 0 to 9 draw IC0_9 sprites; transparent pixels show palette
  color 0. Images 10 and up draw tileset tile `image - 10`; an image beyond
  the tileset is drawn as color 0 with a warning.
- L-IM2: while a class 3 cell keeps its encounter record and the record's first
  monster slot is used, the engine draws IC0_9 sprite
  `mobSpriteMap[monster type]` (SPEC-02 section 3.3) over the cell image.

### 9.9 Encoder rules for lab map blocks

- L-EN1: body order: action-class map, action map, central directory, map info,
  action tables 0 to 7, table 15, NPC section, tables 8 to 14, specials,
  monster names, monster data, strings (the wllib order of section 6.1).
- L-EN2: the encrypted prefix is exactly `body[0 : stringsOffset]`; strings and
  anything after them are plain. The prefix must pass the ambiguity check of
  SPEC-01 section 2.7. The fixture generator nudges monster sturdiness until it
  passes.
- L-EN3: `specialsOffset = 0` (no special-action table).
- L-EN4: a map with no NPCs sets `npcOffset = stringsOffset`. The u16 there
  (`20 65`, read as 0x6520) is non-zero, so the `map.md` rule reads "no NPCs",
  and wllib sees a zero-length section because strings outrank the NPC table.
- L-EN5: string dictionaries start with `20 65` (SPEC-02 L-ST3), so wllib's
  `20 65` guard accepts the same prefix end as the wastelib rule.
- L-EN6: strings fill the body to its end, with no padding; string 0 is empty
  (L-MS1); groups hold exactly 4 strings (SPEC-02 L-ST1).
- L-EN7: the unknown byte before the tile-map section and the unknown u32 after
  `tileMapDecodedSize` are 0.
- L-EN8: no map block contains the bytes `msq` after its 4-byte header (keeps
  wllib's scanning reader working; the generator checks and fails otherwise).
- L-EN9: every map has at least one monster, so `mobNamesOffset <
  mobDataOffset < stringsOffset`.

### 9.10 Replacing lab rules with parity

A parity loader keeps sections 3 to 8 and the decoders unchanged and swaps in:
the WL.EXE table source (SPEC-02 section 3.3) for LABTABLES.BIN; the real
semantics of classes 1 to 15 for 9.1 to 9.7; real map-info units for L-MI2 to
L-MI4. Every lab rule is named (L-xx) so the parity milestone can list which
ones it overrides.

## 10. Disagreements between wastelib and wllib (maps)

| Topic | wastelib | wllib | Engine rule |
| --- | --- | --- | --- |
| Action-class nibble order | high nibble = even x (`map.md`, `GameMap.ts`) | low nibble = even x (`decode/mapdata.go`) | wastelib; wllib's `EncodeMapData` also steps x by 1 inside a 2-cell loop and would overrun its buffer, so its writer is not a reliable witness |
| Map info +0x0A, +0x0B | u16 time per step | u8 seconds rate, u8 minutes rate | read u16, expose both bytes; lab rule L-MI2 |
| Map info +0x0D | u8[37] combat string ids | u16[18] string ids + 1 padding byte | read 37 raw bytes |
| Map info +0x00, +0x01, +0x03, +0x04 | unknown | padding | UNKNOWN |
| End of encrypted prefix | first checksum match | match plus raw `20 65` next | wastelib; lab data satisfies both |
| No-NPC marker | first u16 at npcOffset non-zero | npcOffset 0 or shared with a higher-priority section | read with the `map.md` rule; lab data satisfies both |
| Class 6 | SPECIAL | "shop" (`IDShop`) and "special actions" | UNKNOWN for parity; lab SHOP |
| Transition X and Y | signed bytes | unsigned bytes | lab: unsigned when absolute, signed when relative (L-TR3) |
| Pointer-list length | until the smallest non-zero pointer | from the first non-zero pointer | lab data keeps pointers ascending so both agree |
| Last string group pointer | used if inside the data | "garbage", dropped | do not fail on it |
| Tile map | Huffman decoded | not decoded (opaque) | wastelib |

## 11. Validation checklist

For every map (`map.md` validation notes plus the rules above):

1. Header `msq0` or `msq1` matches the file.
2. Prefix decryption finds a checksum match inside the body.
3. `tileMapDecodedSize == S x S`; map info +0x02 equals the table size.
4. Every non-zero central-directory offset is inside the body.
5. `prefixLength == stringsOffset` (warning for parity data, error for lab
   data).
6. `(stringsOffset - mobDataOffset)` is a multiple of 8.
7. NPC pointers point at 0x100-byte records inside the body.
8. Action pointer lists end inside the body and every record parses inside the
   body.
9. Lab data only: rules L-AC1 to L-AC6, L-EN1 to L-EN9.

## 12. Fixture maps

`SPEC/reference/fixtures_gen.py` (seed 19880101) writes three lab maps into
GAME1. Their decoded cells, records, monsters, NPCs and strings are in
`manifest.json` under `maps`.

| Map | Location | Size | Block offset | tileMapOffset | Body | Encrypted prefix | Content |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 32 | 0 | 2179 | 2172 | 2005 | blocked border; open door (5,5); locked door (6,5); transition to location 1 with confirm (10,10); shop 0 (12,10); loot (14,10); paragraph trigger (16,10); encounter (18,10); blocked with message (20,10); 1 NPC; 2 monsters |
| 1 | 1 | 32 | 2663 | 1779 | 1772 | 1674 | transition to location 0 (10,21); transition to shared location 130, resolved to location 2 (20,20); relative transition +2,0 (5,8); 1 monster |
| 2 | 2 | 64 | 4918 | 6451 | 6444 | 6350 | transition to previous location (32,33); two encounters (40,40), (50,12); loot (20,50); 3 monsters |

wastelib's own `GameMap` reader (run under Node 25) decodes all three maps to
the same cells, strings, monsters, NPC names, map info and transition records
as the manifest. wllib could not be run (no Go toolchain on the build host);
its prefix rule is emulated in `fixtures_gen.py` (`wllibPrefixLength`) and
agrees for all three maps.
