#!/usr/bin/env python3
"""Reference codecs for the Wasteland (1988, DOS) data formats.

Clean-room restatement written from the wastelib format documentation
(Klaus Reimer, MIT: doc/formats/rotating-xor.md, huffman.md, vertical-xor.md,
strings.md, exe.md) and cross-checked against badvassal/wllib (MIT, msq/).
No code from either project is copied here.

This module is the acceptance-test oracle for SPEC-01-codecs.md.
Run `python3 codecs_ref.py --selftest` to check every codec and every
published test vector.

Python 3.9+, standard library only.
"""

from __future__ import annotations

import heapq
import random
import sys

# ---------------------------------------------------------------------------
# Rotating XOR (SPEC-01 section 2)
# ---------------------------------------------------------------------------

KEY_STEP = 0x1F


def rxor_checksum(plain: bytes) -> int:
    """Checksum over decoded bytes: start at 0, subtract each byte, mod 2^16."""
    c = 0
    for b in plain:
        c = (c - b) & 0xFFFF
    return c


def rxor_encode(plain: bytes) -> bytes:
    """Return the two header bytes followed by the encrypted bytes.

    The header bytes are not free parameters: they must equal the low and
    high byte of the checksum of the plaintext, because the decoder compares
    its final checksum with xor1 | (xor2 << 8).
    """
    c = rxor_checksum(plain)
    xor1, xor2 = c & 0xFF, c >> 8
    key = xor1 ^ xor2
    out = bytearray((xor1, xor2))
    for b in plain:
        out.append(b ^ key)
        key = (key + KEY_STEP) & 0xFF
    return bytes(out)


def rxor_decode_whole(data: bytes, n: int, offset: int = 0) -> bytes:
    """Whole-block mode: decode exactly n bytes after the two header bytes.

    Raises ValueError when the final checksum does not match.
    """
    if offset + 2 + n > len(data):
        raise ValueError("rxor: input shorter than 2 + n bytes")
    xor1, xor2 = data[offset], data[offset + 1]
    key = xor1 ^ xor2
    end = xor1 | (xor2 << 8)
    c = 0
    out = bytearray(n)
    for i in range(n):
        d = data[offset + 2 + i] ^ key
        out[i] = d
        c = (c - d) & 0xFFFF
        key = (key + KEY_STEP) & 0xFF
    if c != end:
        raise ValueError("rxor: checksum mismatch (got %04X want %04X)" % (c, end))
    return bytes(out)


def rxor_decode_prefix(data: bytes, body_size: int, offset: int = 0,
                       wllib_guard: bool = False) -> tuple[bytes, int]:
    """Prefix mode (map blocks).

    data[offset:offset+2] are the header bytes; the body is the next
    body_size bytes. Decryption runs while the running checksum differs
    from endChecksum, testing before each byte (so an endChecksum of 0
    gives an empty prefix). The remaining body bytes are plain.

    wllib_guard=True adds wllib's extra condition: the prefix only ends
    where the next two raw bytes are 0x20 0x65.

    Returns (decoded_body, prefix_length). Raises ValueError if the
    checksum never matches inside the body.
    """
    xor1, xor2 = data[offset], data[offset + 1]
    key = xor1 ^ xor2
    end = xor1 | (xor2 << 8)
    base = offset + 2
    if base + body_size > len(data):
        raise ValueError("rxor: body runs past end of input")
    body = bytearray(data[base:base + body_size])
    c = 0
    i = 0
    while True:
        if c == end:
            if not wllib_guard or body[i:i + 2] == b"\x20\x65":
                break
        if i >= body_size:
            raise ValueError("rxor: checksum never matched inside the body")
        d = body[i] ^ key
        body[i] = d
        c = (c - d) & 0xFFFF
        key = (key + KEY_STEP) & 0xFF
        i += 1
    return bytes(body), i


def rxor_prefix_is_unambiguous(prefix: bytes) -> bool:
    """True when prefix-mode decoding of rxor_encode(prefix) stops exactly at
    len(prefix). The running checksum after k bytes equals the final value
    iff the sum of prefix[k:] is 0 mod 65536, so no proper suffix (and not
    the whole prefix) may sum to 0 mod 65536."""
    s = 0
    for k in range(len(prefix) - 1, -1, -1):
        s = (s + prefix[k]) & 0xFFFF
        if s == 0:
            return False
    return len(prefix) > 0


# ---------------------------------------------------------------------------
# Bit streams
# ---------------------------------------------------------------------------

class BitWriterMSB:
    """Writes bits most-significant-bit first within each byte."""

    def __init__(self) -> None:
        self.buf = bytearray()
        self.nbits = 0

    def bit(self, b: int) -> None:
        if self.nbits % 8 == 0:
            self.buf.append(0)
        if b:
            self.buf[-1] |= 0x80 >> (self.nbits % 8)
        self.nbits += 1

    def bits(self, value: int, count: int) -> None:
        for i in range(count - 1, -1, -1):
            self.bit((value >> i) & 1)

    def getvalue(self) -> bytes:
        return bytes(self.buf)  # final partial byte is zero-padded


class BitReaderMSB:
    def __init__(self, data: bytes, byte_offset: int = 0) -> None:
        self.data = data
        self.pos = byte_offset * 8

    def bit(self) -> int:
        byte = self.pos >> 3
        if byte >= len(self.data):
            raise ValueError("bitstream: end of data")
        b = (self.data[byte] >> (7 - (self.pos & 7))) & 1
        self.pos += 1
        return b

    def bits(self, count: int) -> int:
        v = 0
        for _ in range(count):
            v = (v << 1) | self.bit()
        return v

    def sync(self) -> int:
        """Advance to the next byte boundary; return the byte offset."""
        self.pos = (self.pos + 7) & ~7
        return self.pos >> 3


class BitWriterLSB:
    """Writes bits least-significant-bit first within each byte; multi-bit
    values are emitted low bit first (string tables)."""

    def __init__(self) -> None:
        self.buf = bytearray()
        self.nbits = 0

    def bits(self, value: int, count: int) -> None:
        for i in range(count):
            if self.nbits % 8 == 0:
                self.buf.append(0)
            if (value >> i) & 1:
                self.buf[-1] |= 1 << (self.nbits % 8)
            self.nbits += 1

    def getvalue(self) -> bytes:
        return bytes(self.buf)


class BitReaderLSB:
    def __init__(self, data: bytes, byte_offset: int = 0) -> None:
        self.data = data
        self.pos = byte_offset * 8

    def remaining(self) -> int:
        return len(self.data) * 8 - self.pos

    def bits(self, count: int) -> int:
        v = 0
        for i in range(count):
            byte = self.pos >> 3
            if byte >= len(self.data):
                raise ValueError("bitstream: end of data")
            v |= ((self.data[byte] >> (self.pos & 7)) & 1) << i
            self.pos += 1
        return v


# ---------------------------------------------------------------------------
# Huffman (SPEC-01 section 3)
# ---------------------------------------------------------------------------

def _huff_build_tree(data: bytes):
    """Deterministic tree: leaves ordered by (frequency, symbol); internal
    nodes get increasing creation numbers after all symbols (256+). The first
    node popped becomes the left child. A tree is a leaf (int) or a tuple
    (left, right)."""
    if not data:
        return 0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    heap = [(f, s, s) for s, f in enumerate(freq) if f]
    heapq.heapify(heap)
    if len(heap) == 1:
        return heap[0][2]
    serial = 256
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, serial, (a, b)))
        serial += 1
    return heap[0][2]


def _huff_write_tree(w: BitWriterMSB, node) -> None:
    if isinstance(node, int):
        w.bit(1)
        w.bits(node, 8)
    else:
        w.bit(0)
        _huff_write_tree(w, node[0])
        w.bit(0)  # separator bit; decoders ignore its value, lab encoders write 0
        _huff_write_tree(w, node[1])


def _huff_codes(node, prefix=(), table=None):
    if table is None:
        table = {}
    if isinstance(node, int):
        table[node] = prefix  # single-leaf tree: empty code
    else:
        _huff_codes(node[0], prefix + (0,), table)
        _huff_codes(node[1], prefix + (1,), table)
    return table


def huff_encode(data: bytes) -> bytes:
    """Serialized tree plus payload bits, MSB first, one continuous bitstream,
    zero-padded to a whole byte. The decoded size is NOT stored."""
    tree = _huff_build_tree(data)
    w = BitWriterMSB()
    _huff_write_tree(w, tree)
    codes = _huff_codes(tree)
    for b in data:
        for bit in codes[b]:
            w.bit(bit)
    return w.getvalue()


def _huff_read_tree(r: BitReaderMSB, depth: int = 0):
    if depth > 256:
        raise ValueError("huffman: tree too deep")
    if r.bit():
        return r.bits(8)
    left = _huff_read_tree(r, depth + 1)
    r.bit()  # separator, ignored
    right = _huff_read_tree(r, depth + 1)
    return (left, right)


def huff_decode(data: bytes, size: int, offset: int = 0) -> tuple[bytes, int]:
    """Decode exactly `size` bytes starting at byte `offset`.
    Returns (decoded, byte offset after syncing to the next byte boundary)."""
    r = BitReaderMSB(data, offset)
    tree = _huff_read_tree(r)
    out = bytearray(size)
    for i in range(size):
        node = tree
        while not isinstance(node, int):
            node = node[1] if r.bit() else node[0]
        out[i] = node
    return bytes(out), r.sync()


# Huffman-wrapped msq block used by ALLHTDS, ALLPICS and END.CPA
# (u32 decoded size, 3-byte signature, 1 disk byte, bitstream).

def msqh_encode(payload: bytes, disk: int = 0, sig: bytes = b"msq") -> bytes:
    assert len(sig) == 3
    return (len(payload).to_bytes(4, "little") + sig + bytes((disk,))
            + huff_encode(payload))


def msqh_decode(data: bytes, offset: int = 0, sig: bytes | None = b"msq"
                ) -> tuple[bytes, int, int]:
    """Returns (payload, disk byte, offset of the next block)."""
    size = int.from_bytes(data[offset:offset + 4], "little")
    if sig is not None and data[offset + 4:offset + 7] != sig:
        raise ValueError("msq: bad signature %r at %d" % (data[offset + 4:offset + 7], offset))
    disk = data[offset + 7]
    payload, nxt = huff_decode(data, size, offset + 8)
    return payload, disk, nxt


# ---------------------------------------------------------------------------
# Vertical XOR (SPEC-01 section 4)
# ---------------------------------------------------------------------------

def vxor_decode(data: bytes, stride: int) -> bytes:
    out = bytearray(data)
    for i in range(stride, len(out)):
        out[i] ^= out[i - stride]
    return bytes(out)


def vxor_encode(data: bytes, stride: int) -> bytes:
    out = bytearray(data)
    for i in range(len(out) - 1, stride - 1, -1):
        out[i] = data[i] ^ data[i - stride]
    return bytes(out)


# ---------------------------------------------------------------------------
# Compressed string tables (SPEC-02 section 9; strings.md, exe.md, map.md)
# ---------------------------------------------------------------------------

CODE_UPPER = 0x1E
CODE_HIGH = 0x1F


def _str_codes(dictionary: bytes, s: bytes) -> list[int]:
    codes = []
    for ch in s + b"\x00":
        idx = dictionary.find(bytes((ch,)))
        upper = False
        if idx < 0 and 0x41 <= ch <= 0x5A:
            idx = dictionary.find(bytes((ch + 0x20,)))
            upper = True
        if idx < 0 or idx >= 60:
            raise ValueError("string char 0x%02X not encodable with this dictionary" % ch)
        if upper:
            codes.append(CODE_UPPER)
        if idx >= 30:
            codes.append(CODE_HIGH)
            idx -= 30
        codes.append(idx)
    return codes


def strtab_encode(dictionary: bytes, strings: list[bytes]) -> bytes:
    """60-byte dictionary, u16 group pointers (relative to the byte after the
    dictionary), then groups of exactly 4 strings of 5-bit LSB-first codes.
    The string list is padded with empty strings to a multiple of 4."""
    if len(dictionary) != 60:
        raise ValueError("dictionary must be 60 bytes")
    if b"\x00" not in dictionary:
        raise ValueError("dictionary must contain a NUL terminator character")
    strings = list(strings)
    while len(strings) % 4 or not strings:
        strings.append(b"")
    ngroups = len(strings) // 4
    groups = []
    for g in range(ngroups):
        w = BitWriterLSB()
        for s in strings[4 * g:4 * g + 4]:
            for c in _str_codes(dictionary, s):
                w.bits(c, 5)
        groups.append(w.getvalue())
    ptrs = []
    pos = 2 * ngroups
    for gb in groups:
        ptrs.append(pos)
        pos += len(gb)
    out = bytearray(dictionary)
    for p in ptrs:
        out += p.to_bytes(2, "little")
    for gb in groups:
        out += gb
    return bytes(out)


def strtab_decode(data: bytes, offset: int = 0, end: int | None = None) -> list[bytes]:
    """Decode a string table starting at `offset`; `end` bounds the data
    (defaults to len(data)). Returns strings in index order (group*4+slot).
    Strings whose bits run past `end` are dropped, as in wastelib."""
    if end is None:
        end = len(data)
    view = data[:end]
    dictionary = view[offset:offset + 60]
    base = offset + 60
    first = int.from_bytes(view[base:base + 2], "little")
    ngroups = first >> 1
    ptrs = [int.from_bytes(view[base + 2 * i:base + 2 * i + 2], "little") for i in range(ngroups)]
    result = []
    for p in ptrs:
        if base + p >= len(view):
            continue
        r = BitReaderLSB(view, base + p)
        for _ in range(4):
            s = bytearray()
            upper = high = False
            done = False
            while r.remaining() >= 5:
                code = r.bits(5)
                if code == CODE_HIGH:
                    high = True
                elif code == CODE_UPPER:
                    upper = True
                else:
                    ch = dictionary[code + (30 if high else 0)]
                    if ch == 0:
                        done = True
                        break
                    if upper and 0x61 <= ch <= 0x7A:
                        ch -= 0x20
                    s.append(ch)
                    upper = high = False
            if done:
                result.append(bytes(s))
    return result


# ---------------------------------------------------------------------------
# Test vectors (published in SPEC-01 and SPEC-02; regenerate with --vectors)
# ---------------------------------------------------------------------------

def _h(s: str) -> bytes:
    return bytes.fromhex(s.replace(" ", ""))


RXOR_WHOLE_VECTORS = [
    # (plain hex, encoded hex = xor1 xor2 + ciphertext)
    ('00 01 02 03', 'FA FF 05 25 41 61'),
    ('FF FF FF FF FF FF FF FF', '08 F8 0F F0 D1 B2 93 74 55 36'),
    ('00 00 00 00', '00 00 00 1F 3E 5D'),
    ('4D 53 51 30 0A 0D 06 0B 0F 10 11 7F', '08 FE BB 46 65 63 78 9C B6 C4 E1 1D 3D 34'),
]

RXOR_PREFIX_VECTORS = [
    # (encrypted-prefix plain hex, plain suffix hex, raw section hex)
    ('01 02 03 04 05', '20 65 00 00', 'F1 FF 0F 2F 4F 6F 8F 20 65 00 00'),
    ('80', 'AA BB', '80 FF FF AA BB'),
    ('10 20 30 40 50 60 70 01', '20 65 41', '3F FE D1 C0 CF 5E 6D 3C 0B 9B 20 65 41'),
]

HUFF_VECTORS = [
    # (decoded hex, encoded hex); the decoded size is supplied externally
    ('41 41 41 41', 'A0 80'),
    ('00 01 00 01 00 00', '40 50 0A C0'),
    ('41 42 52 41 43 41 44 41 42 52 41', '50 45 0D 44 28 4A 93 74 56 E0'),
    ('00', '80 00'),
    ('0A 0A 0A 0B 0B 0C', '42 88 62 16 3E'),
]

VXOR_VECTORS = [
    # (stride, decoded hex, encoded hex)
    (2, '11 22 11 22 33 44', '11 22 00 00 22 66'),
    (4, 'FF 00 FF 00 FF 00 FF 00 00 FF 00 FF', 'FF 00 FF 00 00 00 00 00 FF FF FF FF'),
    (8, '01 23 45 67 89 AB CD EF 01 23 45 67 89 AB CD EF FE DC BA 98 76 54 32 10', '01 23 45 67 89 AB CD EF 00 00 00 00 00 00 00 00 FF FF FF FF FF FF FF FF'),
    (3, '00 01 02', '00 01 02'),
]

# A 60-byte dictionary used for the string-table vectors.
STR_DICT = (b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r"
            b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;")
assert len(STR_DICT) == 60, len(STR_DICT)



def _gen_vectors() -> dict:
    """Recompute all vectors from the encoders."""
    out = {"rxor_whole": [], "rxor_prefix": [], "huff": [], "vxor": [], "str": []}
    for plain, _ in RXOR_WHOLE_VECTORS:
        out["rxor_whole"].append((plain, rxor_encode(_h(plain)).hex(" ").upper()))
    for pre, suf, _ in RXOR_PREFIX_VECTORS:
        raw = rxor_encode(_h(pre)) + _h(suf)
        out["rxor_prefix"].append((pre, suf, raw.hex(" ").upper()))
    for dec, _ in HUFF_VECTORS:
        out["huff"].append((dec, huff_encode(_h(dec)).hex(" ").upper()))
    for stride, dec, _ in VXOR_VECTORS:
        out["vxor"].append((stride, dec, vxor_encode(_h(dec), stride).hex(" ").upper()))
    for strs in STR_TABLE_CASES:
        out["str"].append((strs, strtab_encode(STR_DICT, strs).hex(" ").upper()))
    return out


STR_TABLE_CASES = [
    [b"Hi"],
    [b"the rat", b"Ranger 7", b"", b"x"],
    [b"a\x0ab\x0ac\x0a", b"Read 12.\r", b"one", b"two", b"three"],
]

# Encoded string-table vectors; checked by the self test.
_STR_TABLE_FROZEN = [
    # hex of strtab_encode(STR_DICT, case) for each case in STR_TABLE_CASES
    '20 65 00 74 61 6E 6F 69 73 72 68 64 6C 75 63 6D 66 77 79 67 70 62 2E 2C 27 76 21 6B 3F 0D 30 31 32 33 34 35 36 37 38 39 78 6A 71 7A 3A 0A 0B 0C 0E 0F 10 11 06 2F 28 29 22 25 2B 3B 02 00 5E 1D 21 84 00',
    '20 65 00 74 61 6E 6F 69 73 72 68 64 6C 75 63 6D 66 77 79 67 70 62 2E 2C 27 76 21 6B 3F 0D 30 31 32 33 34 35 36 37 38 39 78 6A 71 7A 3A 0A 0B 0C 0E 0F 10 11 06 2F 28 29 22 25 2B 3B 02 00 43 05 90 C8 10 3E 91 32 43 02 FF 08 F1 95 00',
    '20 65 00 74 61 6E 6F 69 73 72 68 64 6C 75 63 6D 66 77 79 67 70 62 2E 2C 27 76 21 6B 3F 0D 30 31 32 33 34 35 36 37 38 39 78 6A 71 7A 3A 0A 0B 0C 0E 0F 10 11 06 2F 28 29 22 25 2B 3B 04 00 18 00 E4 BF FA 9F FB 4F F8 14 C8 02 3F 7C 61 BB 30 25 88 11 8D 00 43 A5 10 84 10 02',
]


# ---------------------------------------------------------------------------
# Self test
# ---------------------------------------------------------------------------

def _check(name: str, cond: bool, failures: list) -> None:
    if not cond:
        failures.append(name)


def selftest(verbose: bool = True) -> int:
    failures: list[str] = []
    counts = {}

    # Rotating XOR, whole mode: published vectors.
    for plain, enc in RXOR_WHOLE_VECTORS:
        p, e = _h(plain), _h(enc)
        _check("rxor_whole encode %s" % plain, rxor_encode(p) == e, failures)
        _check("rxor_whole decode %s" % plain, rxor_decode_whole(e, len(p)) == p, failures)
    # Corrupted input must fail the checksum.
    bad = bytearray(_h(RXOR_WHOLE_VECTORS[0][1]))
    bad[3] ^= 0x01
    try:
        rxor_decode_whole(bytes(bad), 4)
        _check("rxor_whole corrupt detection", False, failures)
    except ValueError:
        pass
    counts["rxor_whole_vectors"] = len(RXOR_WHOLE_VECTORS)

    # Rotating XOR, prefix mode: published vectors.
    for pre, suf, raw in RXOR_PREFIX_VECTORS:
        p, s, r = _h(pre), _h(suf), _h(raw)
        _check("rxor_prefix encode %s" % pre, rxor_encode(p) + s == r, failures)
        body, n = rxor_decode_prefix(r, len(p) + len(s))
        _check("rxor_prefix len %s" % pre, n == len(p), failures)
        _check("rxor_prefix body %s" % pre, body == p + s, failures)
    counts["rxor_prefix_vectors"] = len(RXOR_PREFIX_VECTORS)

    # Prefix ambiguity edge case: trailing zero byte ends the prefix early.
    amb = bytes((5, 7, 0))
    _check("rxor_prefix ambiguity detector", not rxor_prefix_is_unambiguous(amb), failures)
    _check("rxor RP-N encode", rxor_encode(amb) == _h("F4 FF 0E 2D 49"), failures)
    body, n = rxor_decode_prefix(_h("F4 FF 0E 2D 49"), 3)
    _check("rxor RP-N early stop on trailing zero", n == 2 and body == _h("05 07 49"), failures)

    # Huffman vectors.
    for dec, enc in HUFF_VECTORS:
        d, e = _h(dec), _h(enc)
        _check("huff encode %s" % dec, huff_encode(d) == e, failures)
        out, nxt = huff_decode(e, len(d))
        _check("huff decode %s" % dec, out == d, failures)
        _check("huff sync %s" % dec, nxt == len(e), failures)
    counts["huff_vectors"] = len(HUFF_VECTORS)

    # Separator bit value must be ignored: flip every separator to 1.
    # Tree for vector 2 is 0 [1 00000001] sep [1 00000000]; the separator is bit 10.
    e = bytearray(_h(HUFF_VECTORS[1][1]))
    e[1] |= 0x20  # bit index 10 counted from the MSB of byte 0
    out, _ = huff_decode(bytes(e), 6)
    _check("huff separator ignored", out == _h(HUFF_VECTORS[1][0]), failures)
    _check("huff HU-S literal", bytes(e) == _h("40 70 0A C0"), failures)
    out, nxt = huff_decode(_h(HUFF_VECTORS[2][1]) + b"\xAA\x55", 11)
    _check("huff over-read offset", nxt == 10, failures)

    # Vertical XOR vectors.
    for stride, dec, enc in VXOR_VECTORS:
        d, e = _h(dec), _h(enc)
        _check("vxor encode s=%d" % stride, vxor_encode(d, stride) == e, failures)
        _check("vxor decode s=%d" % stride, vxor_decode(e, stride) == d, failures)
    counts["vxor_vectors"] = len(VXOR_VECTORS)

    # String tables.
    for strs, enc in zip(STR_TABLE_CASES, _STR_TABLE_FROZEN):
        e = _h(enc)
        _check("strtab encode %r" % strs, strtab_encode(STR_DICT, strs) == e, failures)
        dec = strtab_decode(e)
        padded = list(strs) + [b""] * ((-len(strs)) % 4)
        _check("strtab decode %r" % strs, dec == padded, failures)
    counts["strtab_vectors"] = len(_STR_TABLE_FROZEN)

    # Randomised round trips (seeded).
    rng = random.Random(1988)
    n_rt = 0
    for trial in range(300):
        n = rng.choice((0, 1, 2, 3, 7, 64, 128, 760, 2048, 4032))
        alphabet = rng.choice((1, 2, 3, 16, 256))
        data = bytes(rng.randrange(alphabet) for _ in range(n))
        if n:
            _check("rxor rt %d" % trial, rxor_decode_whole(rxor_encode(data), n) == data, failures)
        enc = huff_encode(data)
        out, nxt = huff_decode(enc + b"\xAA\x55", n)
        _check("huff rt %d" % trial, out == data and nxt == len(enc), failures)
        stride = rng.choice((1, 2, 8, 48, 144))
        _check("vxor rt %d" % trial, vxor_decode(vxor_encode(data, stride), stride) == data, failures)
        if n and rxor_prefix_is_unambiguous(data):
            body, k = rxor_decode_prefix(rxor_encode(data) + b"\x20\x65", n + 2)
            _check("rxor prefix rt %d" % trial, k == n and body[:n] == data, failures)
        n_rt += 1
    # Huffman msq wrapper round trip with two blocks back to back.
    a, b = bytes(range(128)) * 2, bytes(4032)
    blob = msqh_encode(a, 0) + msqh_encode(b, 1)
    pa, da, nx = msqh_decode(blob, 0)
    pb, db, nx2 = msqh_decode(blob, nx)
    _check("msqh chain", pa == a and pb == b and da == 0 and db == 1 and nx2 == len(blob), failures)
    # Random string tables.
    letters = b"etaoinsrhdlucmfwygpb .,'!?0123456789"
    for trial in range(100):
        strs = [bytes(rng.choice(letters) for _ in range(rng.randrange(0, 30)))
                for _ in range(rng.randrange(1, 13))]
        strs = [bytes(c - 0x20 if (0x61 <= c <= 0x7A and rng.random() < 0.2) else c for c in s)
                for s in strs]
        enc = strtab_encode(STR_DICT, strs)
        padded = strs + [b""] * ((-len(strs)) % 4)
        _check("strtab rt %d" % trial, strtab_decode(enc) == padded, failures)
    counts["random_round_trips"] = n_rt + 100 + 1

    if verbose:
        for k, v in counts.items():
            print("%-22s %d" % (k, v))
        if failures:
            print("FAILED %d checks:" % len(failures))
            for f in failures[:40]:
                print("  " + f)
        else:
            print("codecs_ref selftest: OK")
    return 1 if failures else 0


def _print_vectors() -> None:
    v = _gen_vectors()
    for k, rows in v.items():
        print("==", k)
        for row in rows:
            print("  ", row)


if __name__ == "__main__":
    if "--vectors" in sys.argv:
        _print_vectors()
        sys.exit(0)
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(__doc__)
