# SPEC-01: codecs

Status: frozen for PREREG-W1 build, version 1, 21 Oct 2026.
Scope: the three byte-level transforms that every Wasteland (1988, DOS) data
file is built from: rotating XOR, Huffman, vertical XOR. Containers are in
SPEC-02, maps in SPEC-03.

## 1. Sources and conventions

Sources, restated in our own words with attribution (both MIT-licensed):

- [WL-RX] wastelib `doc/formats/rotating-xor.md` (Klaus Reimer).
- [WL-HU] wastelib `doc/formats/huffman.md`.
- [WL-VX] wastelib `doc/formats/vertical-xor.md`.
- [WL-SRC] wastelib source, commit `eb4ed4d`, files `src/main/io/xor.ts`,
  `huffman.ts`, `vxor.ts`, `BinaryReader.ts`, `game/GameMap.ts`. Cited only
  where the docs are silent.
- [WLL] badvassal/wllib Go source, files `msq/encrypt.go`, `msq/msq.go`,
  `msq/read.go`.
- [LAB] a lab decision with no external source. Every [LAB] item is a choice
  the engine may rely on for lab data only.

Conventions:

- All multi-byte integers are little-endian unless a section says otherwise.
- "Must" is a hard requirement for the engine decoder. "Encoder" items apply to
  the lab's own tools (fixture generator, scenario compiler).
- Hex bytes are written as two upper-case digits separated by spaces.
- The oracle for every section is `SPEC/reference/codecs_ref.py`. Run
  `python3 codecs_ref.py --selftest`; it must print `codecs_ref selftest: OK`.

## 2. Rotating XOR

Used by the GAME1 and GAME2 msq blocks: savegame and shop lists in whole-block
mode, map blocks in prefix mode [WL-RX].

### 2.1 Header

Two plain bytes precede the encrypted bytes [WL-RX]:

| Offset | Type | Name |
| --- | --- | --- |
| +0 | u8 | xor1 |
| +1 | u8 | xor2 |

Initial state [WL-RX]:

```text
key         = xor1 XOR xor2            (8 bits)
endChecksum = xor1 | (xor2 << 8)       (16 bits)
checksum    = 0                        (16 bits)
```

[WLL] names the same bytes Xor0 and Xor1 and builds the end value as
`Xor1 << 8 + Xor0`, which is the same number.

### 2.2 Byte transform

For each encrypted byte `e`, in order [WL-RX]:

```text
d        = e XOR key
checksum = (checksum - d) AND 0xFFFF
key      = (key + 0x1F) AND 0xFF
```

The checksum runs over the decoded bytes `d`, never the encrypted bytes
[WL-RX]. The key for byte `i` (0-based) is therefore
`(xor1 XOR xor2) + 31*i mod 256`.

### 2.3 Exact checksum arithmetic

The checksum after `n` decoded bytes is

```text
checksum(n) = (0 - (d[0] + d[1] + ... + d[n-1])) mod 65536
```

computed as an unsigned 16-bit value. Example: decoded bytes `00 01 02 03`
sum to 6, so the checksum is `0x10000 - 6 = 0xFFFA`. This follows directly
from the transform in [WL-RX] and matches `CalcChecksum` in [WLL]
(`msq/encrypt.go`), which subtracts each byte from a uint16.

### 2.4 Encoder rule: the header is the checksum

Because the decoder compares its final checksum with `endChecksum`, an encoder
has no freedom in choosing the header bytes. For plaintext `P`:

```text
c    = (0 - sum(P)) mod 65536
xor1 = c AND 0xFF
xor2 = c >> 8
key  = xor1 XOR xor2
```

[WLL] `EncodeMsqBlock` does exactly this (`Xor0 = csum & 0xff`,
`Xor1 = csum >> 8`). `codecs_ref.rxor_encode` implements it.

### 2.5 Whole-block mode

The surrounding format gives the encrypted length `N` [WL-RX].

1. Read xor1, xor2.
2. Decode exactly `N` bytes with section 2.2.
3. The final checksum must equal `endChecksum`. If not, the block is corrupt:
   the engine must reject it with an error (wastelib throws a checksum error,
   [WL-SRC] `xor.ts`).

Users and their `N` [WL-RX, SPEC-02]:

| Block | N |
| --- | --- |
| Savegame payload | 0x800 (2048) |
| Shop item list payload | 760 |

### 2.6 Prefix mode

Used inside map blocks [WL-RX]. The surrounding format gives the total body
size `B`; only a leading prefix of the body is encrypted, and the prefix length
is not stored.

1. Read xor1, xor2.
2. Set `i = 0`.
3. Loop: if `checksum == endChecksum`, stop; the prefix length is `i`.
   Otherwise decode body byte `i` with section 2.2 and increment `i`.
4. Body bytes `i .. B-1` are plain and are copied unchanged.

The comparison happens before each byte, including before the first one
([WL-SRC] `GameMap.ts`, a `while (checksum !== endChecksum)` loop). The engine
must also stop with an error if `i` reaches `B` without a match; wastelib has
no such bound, so this bound is [LAB] defensive behaviour.

In shipped maps the prefix ends exactly where the map's string section begins
([WL-SRC] `GameMap.ts` comment: the strings section "is not encrypted but the
decrypt algorithm automatically stops right before it"). SPEC-03 section 4
uses this.

wllib variant [WLL] (`msq/read.go`): wllib applies the same checksum test but,
for map blocks, only accepts a match when the next two raw bytes are
`20 65`, to skip false matches. For non-map blocks wllib also uses the
checksum test instead of a fixed length (it stops when the checksum matches
and the next decoded byte would break the match). The engine must use the
wastelib rule (stop at the first match, fixed `N` in whole-block mode). Lab
data is built so both rules give the same answer (section 2.7, SPEC-03
section 9.9).

### 2.7 Edge cases

- Empty prefix: if `endChecksum == 0` the prefix-mode loop stops before the
  first byte and the whole body is plain. A plaintext whose byte sum is a
  multiple of 65536 (for example all zeros) has `endChecksum == 0`.
- Early stop: in prefix mode the running checksum after `k` bytes equals the
  final checksum exactly when `sum(P[k:]) mod 65536 == 0`. So a prefix ending in
  one or more zero bytes stops early, and the trailing zeros are then misread as
  plain bytes (they are still encrypted). Encoder rule [LAB]: an encrypted
  prefix is valid only if no suffix `P[k:]` (`0 <= k < len(P)`) sums to a
  multiple of 65536. `codecs_ref.rxor_prefix_is_unambiguous` checks this;
  the fixture generator refuses to emit a map that fails it.
- Key wrap: the key is 8 bits and wraps every 256 / gcd(31, 256) = 256 bytes.
- Checksum wrap: 16 bits, wraps silently.
- Whole-block mode with a wrong length: the checksum test will almost always
  fail; the engine must not guess a length.

### 2.8 Test vectors

Generated by `codecs_ref.py` and independently decoded by wastelib's own
decoder (`xor.ts`, and the `GameMap.ts` loop for prefix mode) under Node 25:
all agree.

Whole-block mode (parameter: `N` = length of plaintext):

| # | N | Plain (decoded) | Encoded (xor1 xor2 then ciphertext) |
| --- | --- | --- | --- |
| RX-1 | 4 | `00 01 02 03` | `FA FF 05 25 41 61` |
| RX-2 | 8 | `FF FF FF FF FF FF FF FF` | `08 F8 0F F0 D1 B2 93 74 55 36` |
| RX-3 | 4 | `00 00 00 00` | `00 00 00 1F 3E 5D` |
| RX-4 | 12 | `4D 53 51 30 0A 0D 06 0B 0F 10 11 7F` | `08 FE BB 46 65 63 78 9C B6 C4 E1 1D 3D 34` |

Worked check of RX-1: sum 6, checksum `FFFA`, so xor1 = `FA`, xor2 = `FF`,
key = `05`. Keys per byte: `05 24 43 62`. `00^05=05`, `01^24=25`,
`02^43=41`, `03^62=61`.

RX-3 shows the empty-prefix trap: in prefix mode the same bytes would decode
as an empty prefix because `endChecksum` is 0.

Prefix mode (parameter: body size `B` = prefix length + suffix length):

| # | B | Prefix plain | Plain suffix | Raw section (xor1 xor2, encrypted prefix, suffix) | Expected prefix length |
| --- | --- | --- | --- | --- | --- |
| RP-1 | 9 | `01 02 03 04 05` | `20 65 00 00` | `F1 FF 0F 2F 4F 6F 8F 20 65 00 00` | 5 |
| RP-2 | 3 | `80` | `AA BB` | `80 FF FF AA BB` | 1 |
| RP-3 | 11 | `10 20 30 40 50 60 70 01` | `20 65 41` | `3F FE D1 C0 CF 5E 6D 3C 0B 9B 20 65 41` | 8 |

Negative vector RP-N: prefix plain `05 07 00`, raw `F4 FF 0E 2D 49`
(B = 3). Prefix mode stops after 2 bytes and returns the body `05 07 49`: the
third body byte is returned as plain `49` although it was encrypted. This is
the early-stop case; the decoder must not "fix" it, the encoder must avoid it.

Corruption vector RX-C: RX-1 with byte 3 changed from `25` to `24` must raise a
checksum error in whole-block mode.

## 3. Huffman

Used by ALLHTDS tilesets, ALLPICS portraits (image and animation), END.CPA
(both blocks) and the map tile-map section [WL-HU, SPEC-02, SPEC-03].

### 3.1 Bit order

One continuous bitstream, read most-significant bit first within each byte
[WL-HU]. Bit 0 of the stream is bit 7 (`0x80`) of the first byte.

### 3.2 Tree serialization

Recursive, pre-order [WL-HU]:

```text
readNode():
    b = readBit()
    if b == 1: return Leaf(readBits(8))       # 8-bit symbol, MSB first
    left  = readNode()
    readBit()                                  # separator bit, ignored
    right = readNode()
    return Node(left, right)
```

Details:

- The 8 symbol bits are not byte-aligned; they follow the leaf bit directly.
  [WL-SRC] `BinaryReader.readUint8` assembles the byte across a byte boundary
  MSB first.
- The separator bit between the left and right subtrees is present in the
  stream and its value is ignored [WL-HU]. The value written by the original
  tools is UNKNOWN. Encoder rule [LAB]: write 0.
- A tree may be a single leaf (one bit `1` plus 8 symbol bits). Then every
  output byte is that symbol and consumes zero data bits (section 3.3).
- The decoder must bound recursion depth (a valid tree over 256 symbols has
  depth at most 255); [LAB] limit 256, error above it.

### 3.3 Data decoding and termination

Directly after the tree, with no alignment [WL-HU]:

```text
for i in 0 .. decodedSize-1:
    node = root
    while node is not a leaf:
        node = readBit() == 0 ? node.left : node.right
    out[i] = node.symbol
```

- The bitstream does not store the decoded size. It always comes from the
  container: a u32 before the msq signature (SPEC-02 section 2.2) or the u32
  `tileMapDecodedSize` of a map (SPEC-03 section 7) [WL-HU].
- Decoding stops after exactly `decodedSize` bytes, not at an end marker.
- After the last byte the container advances to the next byte boundary before
  reading the next field ([WL-HU]; [WL-SRC] `huffman.ts` calls `sync()`).
  The padding bits are not checked. Encoder rule [LAB]: pad with zero bits.
- Reading past the end of the input is an error.

### 3.4 Encoder notes [LAB]

Any prefix-free tree decodes correctly, so the encoder's tree choice is free.
`codecs_ref.huff_encode` builds a deterministic tree: leaves are ordered by
(frequency, symbol value), merged nodes get creation numbers from 256 upward,
the first node popped becomes the left child. Empty input produces the
single-leaf tree for symbol `00`. Test vectors below come from this encoder; an
engine is only required to decode them, not to reproduce the same tree.

### 3.5 Test vectors

Parameter: `decodedSize` = number of decoded bytes. All five decoded
correctly by wastelib's `decodeHuffman`.

| # | decodedSize | Encoded | Decoded |
| --- | --- | --- | --- |
| HU-1 | 4 | `A0 80` | `41 41 41 41` |
| HU-2 | 6 | `40 50 0A C0` | `00 01 00 01 00 00` |
| HU-3 | 11 | `50 45 0D 44 28 4A 93 74 56 E0` | `41 42 52 41 43 41 44 41 42 52 41` |
| HU-4 | 1 | `80 00` | `00` |
| HU-5 | 6 | `42 88 62 16 3E` | `0A 0A 0A 0B 0B 0C` |

Worked bit-level check of HU-2. Bits of `40 50 0A C0`:
`01000000 01010000 00001010 11000000`.

- bit 0 = `0`: internal node.
- bits 1 to 9 = `1 00000001`: left child is leaf `01`.
- bit 10 = `0`: separator (ignored).
- bits 11 to 19 = `1 00000000`: right child is leaf `00`.
- Codes: `01` = 0, `00` = 1. Data bits 20 to 25 = `1 0 1 0 1 1` give
  `00 01 00 01 00 00`. Bits 26 to 31 are zero padding.

HU-1 is the single-leaf case: tree `1 01000001`, no data bits.

Separator vector HU-S: HU-2 with the separator bit set, encoded
`40 70 0A C0`, must still decode to `00 01 00 01 00 00`.

Over-read vector: the engine must report the byte offset after sync. For HU-3
with two extra bytes `AA 55` appended, decoding 11 bytes ends at offset 10.

## 4. Vertical XOR

A row predictor over bytes, not pixels [WL-VX].

### 4.1 Definition

With row stride `s` bytes [WL-VX]:

```text
decoded[x, 0] = encoded[x, 0]
decoded[x, y] = encoded[x, y] XOR decoded[x, y-1]
```

In place, on a flat buffer:

```text
for i in s .. len-1:
    data[i] = data[i] XOR data[i - s]
```

Ascending order is required; each byte uses the already decoded byte one row
up. Encoding is `enc[i] = dec[i] XOR dec[i - s]` for `i >= s`, computed from
the decoded buffer.

### 4.2 Strides per use

| Use | Stride (bytes) | Buffer length | Applied to | Source |
| --- | --- | --- | --- | --- |
| Tileset tile | 8 | 128 per tile | each 128-byte tile separately, after Huffman | tilesets.md |
| Portrait base image | 48 | 4032 | whole image, after Huffman | allpics.md |
| TITLE.PIC | 144 | 18432 | whole file, no Huffman | title.md |
| END.CPA base image | 144 | 18432 | whole image, after Huffman | ending.md |

Not vertical-XOR coded: portrait animation blocks [allpics.md], the END.CPA
animation block [ending.md], sprites, masks, cursors, the font (no compression
wrapper at all: sprites.md, cursors.md, font.md), and map tile maps (map.md
names only Huffman).

Tiles must be decoded one tile at a time: running the transform over the whole
4096-byte tileset with stride 8 would chain tile `n` row 0 onto tile `n-1`
row 15 and give wrong pixels [tilesets.md].

### 4.3 Edge cases

- A buffer shorter than or equal to one row is unchanged.
- The buffer length does not have to be a multiple of the stride for the
  transform itself; every documented use is an exact multiple.

### 4.4 Test vectors

All four decoded correctly by wastelib's `decodeVxor`.

| # | Stride | Encoded | Decoded |
| --- | --- | --- | --- |
| VX-1 | 2 | `11 22 00 00 22 66` | `11 22 11 22 33 44` |
| VX-2 | 4 | `FF 00 FF 00 00 00 00 00 FF FF FF FF` | `FF 00 FF 00 FF 00 FF 00 00 FF 00 FF` |
| VX-3 | 8 | `01 23 45 67 89 AB CD EF 00 00 00 00 00 00 00 00 FF FF FF FF FF FF FF FF` | `01 23 45 67 89 AB CD EF 01 23 45 67 89 AB CD EF FE DC BA 98 76 54 32 10` |
| VX-4 | 3 | `00 01 02` | `00 01 02` |

## 5. The fourth bit order: string tables

The compressed string tables use 5-bit codes packed least-significant bit
first, the opposite of Huffman. That codec is specified with its container in
SPEC-02 section 9, with test vectors ST-1 to ST-3.

## 6. Oracle interface

`SPEC/reference/codecs_ref.py` (Python 3.9+, standard library only) exposes:

| Function | Purpose |
| --- | --- |
| `rxor_encode(plain) -> bytes` | header bytes plus ciphertext |
| `rxor_decode_whole(data, n, offset=0) -> bytes` | whole-block mode, raises on checksum error |
| `rxor_decode_prefix(data, body_size, offset=0, wllib_guard=False) -> (body, prefix_len)` | prefix mode |
| `rxor_prefix_is_unambiguous(prefix) -> bool` | encoder check from section 2.7 |
| `huff_encode(data) -> bytes` / `huff_decode(data, size, offset=0) -> (out, next_offset)` | Huffman |
| `msqh_encode(payload, disk, sig)` / `msqh_decode(data, offset, sig) -> (payload, disk, next_offset)` | Huffman msq wrapper (SPEC-02 section 2.2) |
| `vxor_encode(data, stride)` / `vxor_decode(data, stride)` | vertical XOR |
| `strtab_encode(dictionary, strings)` / `strtab_decode(data, offset=0, end=None)` | string tables (SPEC-02 section 9) |

`--selftest` checks every vector in this file plus 401 seeded random round
trips. `--vectors` reprints the vectors from the encoders.

## 7. Disagreements between sources (codec level)

| Topic | wastelib | wllib | Engine rule |
| --- | --- | --- | --- |
| End of map prefix | first checksum match ([WL-RX], [WL-SRC]) | checksum match and next raw bytes `20 65` ([WLL] `read.go`) | wastelib rule; lab data satisfies both |
| Length of savegame and shop payloads | fixed: 0x800 and 760 (savegame.md, shopitemlist.md) | checksum-terminated, block ends at the next `msq` signature or end of file ([WLL] `read.go`) | fixed lengths |
| Separator bit | ignored ([WL-HU]) | not implemented: wllib has no Huffman decoder | ignore |

wllib does not decode Huffman or vertical XOR at all; it treats everything
after the encrypted map prefix as opaque plain bytes. Those two codecs are
therefore cross-checked only against wastelib.
