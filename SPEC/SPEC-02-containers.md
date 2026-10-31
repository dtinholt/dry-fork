# SPEC-02: containers

Status: frozen for PREREG-W1 build, version 1, 21 Oct 2026.
Scope: every Wasteland (1988, DOS) file the engine reads, except the inside of
a map block (SPEC-03). Codecs are in SPEC-01.

## 1. Sources and conventions

Sources (MIT), restated in our own words:

- wastelib `doc/formats/`: `game.md`, `exe.md`, `savegame.md`,
  `shopitemlist.md`, `tilesets.md`, `allpics.md`, `sprites.md`,
  `cursors.md`, `font.md`, `title.md`, `ending.md`, `strings.md`,
  `map.md` (string section only here). Cited by file name.
- [WL-SRC] wastelib source, commit `eb4ed4d` (`src/main/...`). Cited only where
  the docs are silent.
- [WLL] badvassal/wllib Go source (`msq/`, `decode/character.go`).
- [LAB] a lab decision, valid for lab data only. All [LAB] container rules are
  collected in section 12.

Conventions: little-endian; offsets in hex with `0x`; sizes exact.

Each structure carries an engine column:

- READ: the engine must decode it and expose it.
- IGNORE: the engine may skip it; it must not fail on any value.
- UNKNOWN: meaning not documented anywhere readable. The engine must preserve
  the bytes if it rewrites the structure, must not interpret them, and must not
  fail on any value.

`paragraphs.md` is out of scope: it describes the 2013 re-release paragraph
images, not the 1988 printed book (BIBLIOGRAPHY.md item 1).

## 2. The msq block family

The string `msq` marks two different block kinds.

### 2.1 Encrypted msq blocks (GAME1, GAME2)

| Offset | Type | Meaning | Engine |
| --- | --- | --- | --- |
| +0x00 | char[4] | `msq0` in GAME1, `msq1` in GAME2 | READ, validate |
| +0x04 | u8 | xor1 | READ |
| +0x05 | u8 | xor2 | READ |
| +0x06 | ... | rotating-XOR data (SPEC-01 section 2) | READ |

Sources: `game.md`, `savegame.md`, `shopitemlist.md`, `map.md`. [WLL]
`msq/msq.go` writes the fourth byte as `0x30 + gameIndex`, the same thing.
These blocks carry no length field and no type field: block type, position and
length all come from external tables (section 3).

### 2.2 Huffman msq blocks (ALLHTDS, ALLPICS, END.CPA)

| Offset | Type | Meaning | Engine |
| --- | --- | --- | --- |
| +0x00 | u32 | decoded payload size in bytes | READ |
| +0x04 | u8[3] | signature, ASCII `msq` (END.CPA animation: `08 67 01`) | READ, validate |
| +0x07 | u8 | disk byte | READ (IGNORE for semantics) |
| +0x08 | bitstream | Huffman payload, decoded to the size at +0x00 | READ |

The compressed length is not stored. The next block starts at the byte
boundary after the last decoded byte (`tilesets.md`, `allpics.md`,
`ending.md`). Observed disk bytes: ALLHTDS1 0, ALLHTDS2 1 (`tilesets.md`);
ALLPICS animation blocks 0, ALLPICS1 image blocks 0, ALLPICS2 image blocks 1
(`allpics.md`); END.CPA both blocks 0 (`ending.md`).

## 3. GAME1 and GAME2

### 3.1 Layout

Container files with no global header, no directory and no entry count
(`game.md`). Contents in file order (`game.md`):

| File | Map blocks | Savegame blocks | Shop list blocks |
| --- | --- | --- | --- |
| GAME1 | 20 | 1 | 3 |
| GAME2 | 22 | 1 | 1 |

Observed block start offsets (`game.md`):

- GAME1 maps: 0, 10958, 16697, 26297, 36394, 44582, 49112, 59252, 66522,
  73455, 83203, 93710, 100598, 105823, 110061, 115498, 122394, 131766,
  139891, 145679. Savegame: 152517. Shop lists: 157131, 157897, 158663.
- GAME2 maps: 0, 4320, 9598, 21955, 29760, 35167, 40852, 46793, 51745,
  58006, 66901, 72935, 84078, 94274, 102058, 109750, 118668, 127156,
  137175, 142703, 151754, 160761. Savegame: 166855. Shop list: 171469.

### 3.2 Why offsets come from WL.EXE

A map block does not expose its length, the tile-map section offset inside it
is external, and the map size is needed before the map-info byte that repeats
it can be reached (`map.md`, `game.md`). The block headers alone cannot
distinguish a map from a savegame or a shop list. The game therefore reads
offsets, sizes and tile-map offsets from tables in the executable, and a
complete reader must do the same (`game.md`, `exe.md`).

wllib instead walks the file block by block, ending each block at the next raw
`msq` signature or at end of file, and is told how many leading blocks are maps
([WLL] `msq/read.go`, `ParseGame`). That approach fails if `msq` occurs inside
encrypted or compressed bytes. The engine must use tables (section 3.3 for
parity data, section 12.2 for lab data).

### 3.3 WL.EXE tables

WL.EXE ships EXEPACK-compressed. All offsets below are absolute file offsets
in the unpacked image, whose size is 169824 bytes (`exe.md`). Unpacking is out
of scope for the lab build (no game files are used); a future parity loader
reads these tables.

| Table | Offset | Format | Index | Source |
| --- | --- | --- | --- | --- |
| Map offsets | 0x18C9A | u32[42] | 0..19 GAME1 maps, 20..41 GAME2 maps | exe.md |
| Tile-map offsets | 0x18D42 | u16[50] | location index | exe.md |
| Location mapping | 0x18EE9 | u8[50] | location index | exe.md |
| Map sizes | 0x18F3C | u8[50] | location index; values 32 or 64 | exe.md |
| Shared locations | 0x18FBC | u8[125] | target location minus 128 | exe.md |
| Encounter mob sprite map | 0x17A37 | u8[6] | mob type 0..5 | exe.md |
| GAME1 savegame offset | 0x880C (low), 0x880F (high) | u16 + u16 | | exe.md |
| GAME2 savegame offset | 0x8819 (low), 0x881C (high) | u16 + u16 | | exe.md |
| Savegame reserved size | 0x8820 | u16 | | exe.md |
| Shop list relative offsets | 0x18E40 | u16[4] | GAME1 shop list | exe.md |
| Tileset cumulative offsets | 0x18E1C | u32[9] | tileset id | tilesets.md |
| Tileset compressed sizes | 0x18E0A | u16[9] | tileset id | tilesets.md |
| Portrait offsets, ALLPICS1 | 0x18AB0 | u32[34] | compact index | allpics.md |
| Portrait offsets, ALLPICS2 | 0x18B38 | u32[49] | compact index | allpics.md |
| Portrait index map, disk 1 | 0x18E4A | u8[80] | raw portrait id | allpics.md |
| Portrait index map, disk 2 | 0x18E9A | u8[80] | raw portrait id | allpics.md |
| Skill metadata | 0x18A40 | 36 x {u8, u8} | skill id | exe.md |

Record and value details:

- Location code (location mapping): bits 0 to 5 = map index, bits 6 to 7 =
  disk code; disk code 2 = GAME1, 1 = GAME2, 0 = unused slot. So
  `code = (diskCode << 6) | mapIndex` (`exe.md`).
- Shared locations: a transition target location `t` with `128 <= t <= 252`
  is first replaced by `sharedLocations[t - 128]`, then resolved through the
  location mapping. Observed: entries 0 to 63 are 5, entries 64 to 124 are 11
  (`exe.md`).
- Savegame offset: `low + (high << 16)`. Observed 0x253C5 (GAME1) and 0x28BC7
  (GAME2); reserved size observed 0x1206 (`exe.md`).
- Shop relative offsets: relative to the end of the GAME1 savegame block
  (savegame offset + reserved size). Observed `0x0000, 0x02FE, 0x05FC, 0x08FA`;
  the fourth points at the end of GAME1 and is not a real block. The GAME2 shop
  list has no table entry; it starts right after the GAME2 savegame block
  (`exe.md`).
- Mob sprite map: observed `[0, 6, 3, 4, 2, 1]`; index 0 is an empty sentinel,
  indices 1 to 5 are mob types (1 animal, 2 mutant, 3 humanoid, 4 cyborg,
  5 robot); the value is a sprite index in IC0_9.WLF used to draw encounter
  actions on the map (`exe.md`).
- Skill metadata entry: byte 0 `iqAndBaseCost` (`>> 3` = minimum IQ,
  `& 0x07` = base skill-point cost); byte 1 = direct offset into the character
  record of the linked attribute (0x0E strength, 0x0F IQ, 0x10 luck, 0x11 speed,
  0x12 agility, 0x13 dexterity, 0x14 charisma). Entry 0 is a dummy; entries 1
  to 35 match skill ids 0x01 to 0x23 and the names in inventory strings 1 to 35
  (`exe.md`).
- Tileset offsets are cumulative across ALLHTDS1 (ids 0 to 3) and ALLHTDS2
  (ids 4 to 8); subtract the cumulative offset of tileset 4 (0x8603) to get a
  local ALLHTDS2 offset (`tilesets.md`).

### 3.4 Locating a map by location index

```text
code    = locationMapping[L]          (after the shared-location step if L >= 128)
disk    = code >> 6                    (2 = GAME1, 1 = GAME2, 0 = invalid)
index   = code & 0x3F
offset  = mapOffsets[index]            if GAME1
        = mapOffsets[20 + index]       if GAME2
size    = mapSizes[L]
tmo     = tileMapOffsets[L]            (offset of the tile-map section in the block)
```

Sources: `exe.md`. The map block itself is SPEC-03.

### 3.5 Engine obligations for GAME files

- READ: block header, validate `msq0` or `msq1` against the file.
- READ: locate every block only through tables.
- Validate: map offsets strictly increasing; savegame after the last map; shop
  lists after the savegame (`game.md`).
- IGNORE: bytes between the end of a decoded structure and the next table
  offset.

## 4. Savegame block

### 4.1 Block

Reserved size 0x1206 in both files (`savegame.md`).

| Offset | Size | Meaning | Engine |
| --- | --- | --- | --- |
| 0x000 | 4 | `msq0` or `msq1` | READ |
| 0x004 | 1 | xor1 | READ |
| 0x005 | 1 | xor2 | READ |
| 0x006 | 0x800 | rotating-XOR payload, whole-block mode, N = 0x800 | READ |
| 0x806 | 0xA00 | reserved tail; all zero in shipped files | UNKNOWN |

### 4.2 Decoded payload (0x800 bytes)

Source: `savegame.md`; matches [WL-SRC] `Savegame.ts`.

| Offset | Size | Meaning | Engine |
| --- | --- | --- | --- |
| 0x000 | 0x038 | four party-group records of 14 bytes | READ |
| 0x038 | 0x040 | unknown | UNKNOWN |
| 0x078 | 1 | viewport X | READ |
| 0x079 | 1 | viewport Y | READ |
| 0x07A | 3 | unknown | UNKNOWN |
| 0x07D | 1 | current member count | READ |
| 0x07E | 1 | current party index | READ |
| 0x07F | 1 | current map/location byte | READ |
| 0x080 | 1 | total member count | READ |
| 0x081 | 1 | extra group count | READ |
| 0x082 | 1 | unknown | UNKNOWN |
| 0x083 | 1 | minute | READ |
| 0x084 | 1 | hour | READ |
| 0x085 | 1 | combat scroll speed | READ |
| 0x086 | 0x06F | unknown | UNKNOWN |
| 0x0F5 | 4 | save serial number (u32) | READ |
| 0x0F9 | 7 | unknown | UNKNOWN |
| 0x100 | 0x700 | seven character records of 0x100 bytes | READ |

Whether "current map/location byte" is a location index (section 3.4) or a
map index is UNKNOWN; the field name in `savegame.md` allows both. Lab rule
L-SG1 (section 12.4) fixes it for lab data.

### 4.3 Party-group record (14 bytes)

| Offset | Type | Meaning | Engine |
| --- | --- | --- | --- |
| +0x00 | u8 | unused / unknown | UNKNOWN |
| +0x01 | u8[7] | party order: 1 to 7 = character slot, 0 = empty | READ |
| +0x08 | u8 | X position | READ |
| +0x09 | u8 | Y position | READ |
| +0x0A | u8 | current map/location byte | READ |
| +0x0B | u8 | previous X | READ |
| +0x0C | u8 | previous Y | READ |
| +0x0D | u8 | previous map/location byte | READ |

Source: `savegame.md`.

### 4.4 Character record (0x100 bytes)

Used for the seven savegame slots and for NPCs inside maps (`savegame.md`,
`map.md`). [WLL] `decode/character.go` gives the same offsets.

| Offset | Type | Meaning | Engine |
| --- | --- | --- | --- |
| 0x00 | char[14] | name, NUL-terminated (at most 13 characters, [WLL]) | READ |
| 0x0E | u8 | strength | READ |
| 0x0F | u8 | intelligence | READ |
| 0x10 | u8 | luck | READ |
| 0x11 | u8 | speed | READ |
| 0x12 | u8 | agility | READ |
| 0x13 | u8 | dexterity | READ |
| 0x14 | u8 | charisma | READ |
| 0x15 | u24 | money | READ |
| 0x18 | u8 | gender: 0 male, 1 female ([WL-SRC] `Gender.ts`, [WLL]) | READ |
| 0x19 | u8 | nationality: 0 US, 1 Russian, 2 Mexican, 3 Indian, 4 Chinese ([WL-SRC] `Nationality.ts`, [WLL]) | READ |
| 0x1A | u8 | armor class | READ |
| 0x1B | u16 | maximum constitution | READ |
| 0x1D | u16 | current constitution | READ |
| 0x1F | u8 | equipped weapon slot, 1-based, 0 = none ([WL-SRC] `Character.ts`, [WLL]) | READ |
| 0x20 | u8 | unspent skill points | READ |
| 0x21 | u24 | experience | READ |
| 0x24 | u8 | level | READ |
| 0x25 | u8 | equipped armor slot, 1-based, 0 = none | READ |
| 0x26 | u16 | last constitution before incapacitation | READ |
| 0x28 | u8 | afflictions bitmap; bit meanings UNKNOWN | READ (raw) |
| 0x29 | u8 | NPC flag (1 = NPC) | READ |
| 0x2A | u8 | unknown | UNKNOWN |
| 0x2B | u8 | item-refusal value | READ |
| 0x2C | u8 | skill-refusal value | READ |
| 0x2D | u8 | attribute-refusal value | READ |
| 0x2E | u8 | trade-refusal value | READ |
| 0x2F | u8 | unknown | UNKNOWN |
| 0x30 | u8 | join-string id | READ |
| 0x31 | u8 | willingness | READ |
| 0x32 | char[25] | rank string, NUL-terminated | READ |
| 0x4B | u8 | game-won flag | READ |
| 0x4C | u8 | special-promotion flag | READ |
| 0x4D | u8[51] | unknown | UNKNOWN |
| 0x80 | u8[60] | 30 skill slots {skill id, level}; id 0 = unused | READ |
| 0xBC | u8 | unknown | UNKNOWN |
| 0xBD | u8[60] | 30 item slots {item id, ammo/status}; id 0 = unused | READ |
| 0xF9 | u8[7] | unknown | UNKNOWN |

Item status byte (`savegame.md`): bit 7 clear means bits 0 to 6 hold the ammo
or load value; bit 7 set means jammed, observed values 0x80 to 0x85 with the low
bits a jam severity 0 to 5. The meaning of the refusal values, willingness and
join-string id at runtime is UNKNOWN (the join-string id presumably indexes map
strings; not confirmed).

### 4.5 Engine obligations

READ every READ field above; verify the checksum; keep UNKNOWN bytes intact
when writing a savegame back. Validation (`savegame.md`): header, 0x806-byte
prefix, checksum, characters at 0x100, each 0x100 bytes.

## 5. Shop item list block

Source: `shopitemlist.md`.

| Offset | Size | Meaning | Engine |
| --- | --- | --- | --- |
| 0x000 | 4 | `msq0` or `msq1` | READ |
| 0x004 | 2 | xor1, xor2 | READ |
| 0x006 | 760 | rotating-XOR payload, whole-block mode, N = 760 | READ |

Block size 766 (0x2FE).

Decoded payload:

| Offset | Size | Meaning | Engine |
| --- | --- | --- | --- |
| 0x000 | 8 | fixed header, observed `60 60 60 00 37 08 F8 39` in every list; purpose unknown | UNKNOWN (validate value) |
| 0x008 | 94 x 8 | item records | READ |

Item record (8 bytes):

| Offset | Type | Meaning | Engine |
| --- | --- | --- | --- |
| +0 | u16 | price | READ |
| +2 | u8 | stock | READ |
| +3 | u8 | `itemType = byte >> 3`; `lowFlags = byte & 7` | READ |
| +4 | u8 | capacity | READ |
| +5 | u8 | skill | READ |
| +6 | u8 | damage | READ |
| +7 | u8 | ammo item id | READ |

`demolition = (lowFlags == 1)`; only 0 and 1 were observed; other low-flag
values are UNKNOWN. Unused records still occupy 8 bytes, and wastelib reads
all 94 records unconditionally ([WL-SRC] `ShopItemList.ts`). How the game
marks a record as unused is UNKNOWN; lab data uses eight zero bytes
(section 12.5).

## 6. Tilesets: ALLHTDS1, ALLHTDS2

Source: `tilesets.md`.

- File: Huffman msq blocks (section 2.2) back to back until end of file; no
  header, no count, no offset table in the file.
- One block = one tileset. Decoded payload = raw tiles, `tileCount =
  decodedSize / 128`; the size must be a multiple of 128.
- Tile: 16 x 16 pixels, 4 bits per pixel, 8 bytes per row, 128 bytes.
- Each 128-byte tile is vertical-XOR decoded on its own with stride 8
  (SPEC-01 section 4.2).
- Pixels: row-major, high nibble = left pixel, low nibble = right pixel.
- Global tileset ids: 0 to 3 in ALLHTDS1, 4 to 8 in ALLHTDS2. The EXE tables
  (section 3.3) allow random access but are not needed to parse.

Engine: READ all of it. The disk byte is IGNORE.

## 7. Portraits and animation: ALLPICS1, ALLPICS2

Source: `allpics.md`.

### 7.1 File and lookup

- File: portrait records back to back until end of file; no header.
- Lookup (EXE tables, section 3.3): choose ALLPICS1 for references from GAME1
  and ALLPICS2 for GAME2; map the raw portrait id through the disk's u8[80]
  index table; value 0x80 = invalid on that disk; otherwise the value is a
  compact index into the disk's u32 offset table; seek and read one record.

### 7.2 Record

Two Huffman msq blocks (section 2.2):

1. Base image: decoded size 4032 (96 x 84 pixels, 4 bpp, 48 bytes per row).
   Vertical-XOR decode with stride 48, then high nibble = left pixel.
2. Animation block, not vertical-XOR coded:

| Offset | Type | Meaning |
| --- | --- | --- |
| +0 | u16 | scriptsSize |
| +2 | u8[scriptsSize] | script section |
| +2+scriptsSize | u16 | updatesSize |
| +4+scriptsSize | u8[updatesSize] | update section |

`animDecodedSize = 4 + scriptsSize + updatesSize`, no padding, no counts.

Script section: scripts back to back. A script is a list of
`(u8 delay, u8 updateIndex)` pairs ended by one byte 0xFF; a byte read where a
delay is expected that equals 0xFF ends the script. `updateIndex` is 0-based.
Example `00 04 03 07 01 02 FF` = lines (0, 4), (3, 7), (1, 2).

Update section: updates back to back. An update is a list of patches ended by
u16 0xFFFF. Patch: u16 header, `size = (header >> 12) + 1` (1 to 16),
`offset = header & 0x0FFF` (byte offset into the 4032-byte packed buffer),
then `size` data bytes. Apply: `image[offset + i] ^= data[i]`. Applying an
update twice restores the bytes.

Timing: the delay is a raw u8; a practical model is
`(delay + 1) * 54.925 ms` (PC timer tick), which `allpics.md` labels a model,
not a stored fact. Exact playback semantics (loop or stop at script end, which
script runs when, how several scripts interleave) are UNKNOWN. [WL-SRC]
`PortraitPlayer.ts` implements one interpretation; the lab rule is L-PT1
(section 12.6).

Validation: script and update parsing must end exactly at their sizes; patch
ranges must stay inside 4032 bytes.

Engine: READ base image, scripts, updates. Disk byte IGNORE.

## 8. Other graphics

### 8.1 Sprites: IC0_9.WLF and MASKS.WLF

Source: `sprites.md`. No header, no compression.

- IC0_9.WLF: 128 bytes per sprite (16 x 16), four 1-bit planes of 32 bytes in
  the order blue, green, red, intensity. Each plane: 16 rows of 2 bytes,
  MSB = leftmost pixel. `colorIndex = blue | green << 1 | red << 2 |
  intensity << 3`.
- MASKS.WLF: 32 bytes per sprite, same geometry; bit 1 = transparent,
  0 = visible.
- Both files must hold the same number of records. Shipped: 1280 and 320
  bytes, 10 sprites.
- Map image indices 0 to 9 draw these sprites (`map.md`).

### 8.2 Font: COLORF.FNT

Source: `font.md`. 32 bytes per 8 x 8 glyph, four planes of 8 bytes (blue,
green, red, intensity), one byte per row, MSB = leftmost. No mask; every pixel
is visible. Shipped: 5504 bytes, 172 glyphs. Which glyph index renders which
character code is UNKNOWN from these sources (lab rule L-FN1, section 12.7).

### 8.3 Cursors: CURS

Source: `cursors.md`. 256 bytes per 16 x 16 cursor: four 64-byte component
blocks (blue, green, red, intensity). Each block has 16 row records of 4
bytes: mask bits for x 8 to 15, mask bits for x 0 to 7, data bits for x 8 to
15, data bits for x 0 to 7 (right half first). MSB first. Mask bit 1 =
visible, 0 = transparent (the opposite of sprites). In shipped data the four
mask planes are identical, so the blue mask can stand for all. Shipped: 2048
bytes, 8 cursors. Whether the original ever used differing per-plane masks is
UNKNOWN; the engine must use the blue-plane mask.

### 8.4 Title: TITLE.PIC

Source: `title.md`. Exactly 18432 bytes, no header: a 288 x 128 image, 4 bpp,
144 bytes per row, vertical-XOR coded over the whole file with stride 144.

### 8.5 Ending: END.CPA

Source: `ending.md`.

1. Base block: Huffman msq (signature `msq`, disk 0), decoded 18432 bytes,
   vertical XOR stride 144, 288 x 128 at 4 bpp.
2. Animation block: Huffman msq whose signature bytes are `08 67 01` and disk
   byte 0. Decoded layout: u16 `contentSize` (= decoded size - 4), the update
   stream, then u16 0x0000.

```text
updateStream := update* 0xFFFF
update       := delay:u16 patch* 0xFFFF
patch        := offset:u16 data:u8[4]
```

Patch data replaces 4 bytes (8 pixels); it is not XORed. The offset counts
8-pixel cells on a 320-pixel-wide logical screen:

```text
cellX = offset % 40
y     = offset / 40          (integer division)
imageByteOffset = y * 144 + cellX * 4
```

Example: offset 41 gives x = 8, y = 1, byte offset 148. Converted positions
must lie inside 288 x 128 (that is, `cellX < 36` and `y < 128`). Delay timing
model `(delay + 1) * 54.925 ms`, as for portraits. The decoded payload ends
`... FF FF FF FF 00 00`.

Engine: READ all of section 8.

## 9. String tables

### 9.1 Compressed table format

Used by the nine WL.EXE string tables and by every map's string section
(`exe.md`, `map.md`). The 5-bit code order and the dictionary split come
from [WL-SRC] `io/string.ts` and `io/BinaryReader.ts`, because the docs do not
state them.

| Field | Meaning |
| --- | --- |
| char[60] | dictionary |
| u16 firstPointer | first group pointer; `numGroups = firstPointer / 2` |
| u16[numGroups - 1] | remaining group pointers |
| bitstream | groups of strings |

- Group pointers are relative to the byte right after the dictionary, so the
  first group starts right after the pointer table (`exe.md`, `map.md`).
- Each group starts at its pointer, byte-aligned, and holds up to 4 strings
  (`exe.md`). Strings inside a group follow each other with no alignment
  ([WL-SRC]).
- Codes are 5 bits, packed least-significant bit first: the first bit read is
  bit 0 of the byte and becomes bit 0 of the code ([WL-SRC], `readBits(5,
  true)`). This is the opposite of the Huffman bit order.
- Code 0x1E: the next character is upper-cased. Code 0x1F: the next character
  comes from the upper half of the dictionary, `dictionary[code + 30]`. Other
  codes: `dictionary[code]`. Both flags reset after each character
  (`exe.md`, [WL-SRC]).
- A decoded NUL character ends the string (`exe.md`), so the dictionary must
  contain byte 0x00.
- String index = group index x 4 + position in group ([WL-SRC] reads 4 strings
  per pointer and numbers them in order).
- wastelib skips a pointer that points at or past the end of the data, and
  drops a string whose bits run out ([WL-SRC]). [WLL] `decode/stringsarea.go`
  notes that the final pointer of a map string section "is garbage" in some
  maps and drops the last group. Whether the last group pointer is meaningful
  is UNKNOWN; the engine must not fail on an out-of-range final pointer.
- Observed table sizes, offsets and string counts in WL.EXE: intro 0x17723
  (527 bytes, 18 strings), messages 0x17B5E (1661, 107), inventory 0x18290
  (1845, 170), character creation 0x19E6B (210, 8), ending 0x1A1AE (661, 10),
  promotion 0x1A642 (1136, 63), library 0x1AAEC (277, 11), shop 0x1AC18 (229,
  10), infirmary 0x1AD0D (369, 25) (`exe.md`).

### 9.2 Control bytes inside decoded strings

Source: `strings.md`.

| Byte | Meaning | Status |
| --- | --- | --- |
| 0x0D | line break (the real newline) | confirmed |
| 0x0A | two-way selector (singular / plural); not a line break | confirmed |
| 0x0B | insert current name | confirmed |
| 0x0C | two-way gender selector | confirmed |
| 0x0E | three-way pronoun selector | confirmed |
| 0x0F | insert current number | confirmed |
| 0x10 | menu option marker | confirmed |
| 0x11 | start of choice list | confirmed |
| 0x06 | hard message break (wait, then continue) | confirmed |
| 0x01 | text attribute on | likely |
| 0x02 | text attribute off | likely |
| 0x03 | inline UI handoff | likely |
| 0x04 | dialog style selector | likely |
| 0x07 | dialog style selector | likely |
| 0x08 | input prompt continuation | likely |
| 0x05, 0x09 | recognised by the interpreter, never seen in EXE tables | UNKNOWN |
| 0x7F | printable glyph from the game font, not a control byte | confirmed |

Selector syntax (`strings.md`):

```text
prefix 0x0A A 0x0A B 0x0A suffix                  A = singular, B = plural
prefix 0x0C M 0x0C F 0x0C suffix                  M = male, F = female
prefix 0x0E P1 0x0E P2 0x0E P3 0x0E suffix         classes 1, 2, 3 (he, she, it)
question 0x0D 0x0D 0x11 0x10 opt1 0x0D 0x10 opt2 0x0D  choice list
```

Selectors nest, for example
`killing 0x0A 0x0E him 0x0E her 0x0E it 0x0E 0x0A 0x0F of them 0x0A`.
Exact visual effect of the "likely" bytes is UNKNOWN; which number or name the
placeholders take depends on the caller and is UNKNOWN per call site.

Engine: READ (decode tables); render 0x0D, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F,
0x10, 0x11, 0x06 as above; for 0x01 to 0x04, 0x07, 0x08 apply lab rule L-ST2
(section 12.3).

### 9.3 Test vectors

Dictionary D (60 bytes) used by all three vectors and by the lab data:

```text
20 65 00 74 61 6E 6F 69 73 72 68 64 6C 75 63 6D 66 77 79 67
70 62 2E 2C 27 76 21 6B 3F 0D 30 31 32 33 34 35 36 37 38 39
78 6A 71 7A 3A 0A 0B 0C 0E 0F 10 11 06 2F 28 29 22 25 2B 3B
```

Each encoded table is D followed by the bytes shown. Decoded lists include the
empty strings that pad the last group to 4. All three decode identically in
wastelib's `readStrings`.

| # | After the dictionary | Decoded strings |
| --- | --- | --- |
| ST-1 | `02 00 5E 1D 21 84 00` | `Hi`, ``, ``, `` |
| ST-2 | `02 00 43 05 90 C8 10 3E 91 32 43 02 FF 08 F1 95 00` | `the rat`, `Ranger 7`, ``, `x` |
| ST-3 | `04 00 18 00 E4 BF FA 9F FB 4F F8 14 C8 02 3F 7C 61 BB 30 25 88 11 8D 00 43 A5 10 84 10 02` | `a<0A>b<0A>c<0A>`, `Read 12.<0D>`, `one`, `two`, `three`, ``, ``, `` |

Worked check of ST-1: codes `1E 0A 07 02 02 02 02` (upper, `h`, `i`, NUL,
then three empty strings). Packed 5 bits each, LSB first, the bytes are
`5E 1D 21 84 00`.

## 10. Engine obligations summary

| Structure | Must read | May ignore | UNKNOWN (preserve, do not interpret) |
| --- | --- | --- | --- |
| GAME msq header | signature, xor bytes | nothing | nothing |
| Savegame | groups, viewport, counts, map byte, time, scroll speed, serial, 7 characters | none | 0x038 (64 bytes), 0x07A (3), 0x082 (1), 0x086 (111), 0x0F9 (7), tail 0xA00, group byte +0, meaning of map byte |
| Character | all named fields | none | 0x2A, 0x2F, 0x4D (51), 0xBC, 0xF9 (7), affliction bits, refusal semantics |
| Shop list | 94 records | none | 8-byte header meaning, low flags other than 0 and 1 |
| ALLHTDS | tiles | disk byte | none |
| ALLPICS | base, scripts, updates | disk byte | playback semantics |
| Sprites, masks | all | none | none |
| Font | glyph pixels | none | glyph to character mapping |
| Cursors | pixels, blue mask | other mask planes | per-plane masks |
| TITLE.PIC, END.CPA | all | none | none |
| String tables | text and control bytes | none | 0x05, 0x09, exact look of 0x01 to 0x04, 0x07, 0x08, last group pointer |

## 11. Disagreements between wastelib and wllib (containers)

| Topic | wastelib | wllib | Engine rule |
| --- | --- | --- | --- |
| Block location | EXE tables (`game.md`, `exe.md`) | scan for the next `msq` ([WLL] `read.go`) | tables |
| Savegame and shop payload length | fixed 0x800 and 760 | checksum-terminated | fixed |
| Character record | `savegame.md` | `decode/character.go` | identical offsets; wllib names 0x4C "radio after won" where wastelib says "special-promotion flag"; same byte |
| Monster names | NUL-terminated strings (`map.md`) | split on 0x0A into start, singular, plural, end ([WLL] `monsternames.go`) | compatible: 0x0A is the selector of section 9.2 |
| String section end | not stated | final pointer sometimes garbage; last string assumed 10 bytes ([WLL] `stringsarea.go`) | do not fail on a bad final pointer |

Map-level disagreements are in SPEC-03 section 10.

## 12. Lab rules v1 for containers (non-parity)

These rules exist because the lab ships no Interplay files and no WL.EXE.
They replace only the table source and fill documented gaps. A parity loader
replaces section 12.2 with the WL.EXE tables of section 3.3 and keeps every
other reader unchanged.

### 12.1 Lab file set

| File | Format | Notes |
| --- | --- | --- |
| GAME1 | section 3 | maps, then savegame, then shop lists; headers `msq0` |
| LABTABLES.BIN | section 12.2 | replaces the WL.EXE tables |
| ALLHTDS1 | section 6 | lab tilesets |
| ALLPICS1 | section 7 | lab portraits |
| IC0_9.WLF, MASKS.WLF | section 8.1 | 10 lab sprites |
| COLORF.FNT | section 8.2 | lab font |
| CURS | section 8.3 | lab cursors |
| TITLE.PIC | section 8.4 | lab title |
| END.CPA | section 8.5 | lab ending |
| LABSTR.BIN | section 12.3 | replaces the WL.EXE string tables |

GAME2, ALLHTDS2 and ALLPICS2 are optional; when absent, every table entry
pointing into them is zero and their counts are zero.

### 12.2 LABTABLES.BIN

Fixed size 0x438 (1080) bytes, little-endian. Every table has the same element
type and count as its WL.EXE counterpart, so the decoding code is shared.

| Offset | Format | Field | WL.EXE counterpart |
| --- | --- | --- | --- |
| 0x000 | char[8] | magic `WLLABTB1` | none |
| 0x008 | u32[42] | mapOffsets | 0x18C9A |
| 0x0B0 | u16[50] | tileMapOffsets (by location) | 0x18D42 |
| 0x114 | u8[50] | locationMapping | 0x18EE9 |
| 0x146 | u8[50] | mapSizes (by location) | 0x18F3C |
| 0x178 | u8[125] | sharedLocations | 0x18FBC |
| 0x1F5 | u8[6] | mobSpriteMap | 0x17A37 |
| 0x1FB | u8 | zero | none |
| 0x1FC | u32[2] | savegameOffsets (GAME1, GAME2; 0xFFFFFFFF = absent) | 0x880C/0x880F, 0x8819/0x881C |
| 0x204 | u16 | savegameSize (0x1206) | 0x8820 |
| 0x206 | u16[4] | shopListRelOffsets | 0x18E40 |
| 0x20E | u8[2] | mapCounts (GAME1, GAME2) | none (20 and 22 in shipped data) |
| 0x210 | u8[2] | shopListCounts (GAME1, GAME2) | none (3 and 1 in shipped data) |
| 0x212 | u8[2] | zero | none |
| 0x214 | u32[9] | tilesetOffsets (cumulative) | 0x18E1C |
| 0x238 | u16[9] | tilesetSizes | 0x18E0A |
| 0x24A | u8[2] | zero | none |
| 0x24C | u32[34] | portraitOffsets1 | 0x18AB0 |
| 0x2D4 | u32[49] | portraitOffsets2 | 0x18B38 |
| 0x398 | u8[80] | portraitIndices1 | 0x18E4A |
| 0x3E8 | u8[80] | portraitIndices2 | 0x18E9A |

Lab rules on values:

- L-TB1: mapCounts and shopListCounts are explicit, so the engine never infers
  a count from offsets. Shop list `i` of GAME1 is at
  `savegameOffsets[0] + savegameSize + shopListRelOffsets[i]` for
  `i < shopListCounts[0]`. A GAME2 shop list, if present, starts right after
  the GAME2 savegame block (as in `exe.md`).
- L-TB2: unused entries are zero, unused portrait indices are 0x80, unused
  location codes are 0.
- L-TB3: the GAME file ends exactly after its last shop list.

### 12.3 LABSTR.BIN and string rules

```text
char[8]  magic "WLLABST1"
u16      tableCount
u16      zero
u32      tableOffset[tableCount]    absolute file offsets
u32      tableSize[tableCount]
...      tables, each in the format of section 9.1
```

- L-ST1: every lab string table has exactly 4 strings per group; the encoder
  pads the last group with empty strings. String index = group x 4 + slot.
- L-ST2: the engine renders 0x01 and 0x02 as inverse video on and off, drops
  0x03, 0x04, 0x07 and 0x08 from the output (they may change dialog layout
  only), and treats 0x05 and 0x09 as no-ops.
- L-ST3: lab dictionaries start with the bytes `20 65` and contain 0x00 in
  their first 30 entries. The `20 65` start keeps lab maps readable by wllib
  (SPEC-03 section 9.9).
- L-ST4: table 0 = intro and title text, table 1 = general messages. Further
  tables are assigned by the scenario.

### 12.4 Savegame rules

- L-SG1: every "map/location byte" in lab savegames (0x07F and group bytes
  +0x0A, +0x0D) holds a location index (section 3.4).
- L-SG2: UNKNOWN regions and the 0xA00 tail are written as zero.
- L-SG3: one savegame per GAME file, at `savegameOffsets[disk]`.

### 12.5 Shop rules

- L-SH1: the 8-byte header is written as the observed constant
  `60 60 60 00 37 08 F8 39`.
- L-SH2: an unused record is eight zero bytes; the engine hides records whose
  price, stock and type byte are all zero.
- L-SH3: shop lists are numbered from 0 in table order; SPEC-03 shop actions
  use this number.

### 12.6 Portrait rule

- L-PT1: the engine plays script 0 of a portrait in a loop: for each line, wait
  `(delay + 1) * 54.925 ms`, then XOR-apply update `updateIndex`. Lab
  portraits have one script whose updates net to zero over one pass (each
  update appears an even number of times), so looping is seamless.

### 12.7 Font rule

- L-FN1: lab glyph `n` renders character code `n + 0x20` for
  `0 <= n < glyphCount`; codes without a glyph render as glyph 0.

### 12.8 Lab fixtures

`SPEC/reference/fixtures_gen.py` writes a complete lab data set in these
formats with a JSON manifest of decoded ground truth. Contents (seed
19880101):

| File | Size (bytes) | Content |
| --- | --- | --- |
| GAME1 | 18485 | maps at 0, 2663, 4918 (32x32, 32x32, 64x64); savegame at 13105; shop list at 17719 |
| LABTABLES.BIN | 1080 | tables for the above |
| ALLHTDS1 | 2516 | one tileset, 32 tiles |
| ALLPICS1 | 4814 | four portraits, each with one script and one update (two frames) |
| IC0_9.WLF, MASKS.WLF | 1280, 320 | 10 sprites |
| COLORF.FNT | 1024 | 32 glyphs |
| CURS | 512 | 2 cursors |
| TITLE.PIC | 18432 | title |
| END.CPA | 3050 | ending with 2 updates |
| LABSTR.BIN | 258 | 2 string tables |

Every decoded fixture value was also checked with wastelib's own TypeScript
readers (Node 25): maps (cells, strings, monsters, NPCs, map info,
transitions), savegame, shop list, tiles, portrait base images, title and
ending base image all agree with the manifest.
