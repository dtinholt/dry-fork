"""Compressed string tables (SPEC-02 sections 9 and 12.3).

A table is a 60-byte dictionary, u16 group pointers (relative to the byte
after the dictionary), then groups of up to four strings of 5-bit codes packed
least-significant bit first.
"""

from __future__ import annotations

from .errors import FormatError

CODE_UPPER = 0x1E
CODE_HIGH = 0x1F

LABSTR_MAGIC = b"WLLABST1"


class BitWriterLSB:
    """Writes bits least-significant-bit first; multi-bit values low bit first."""

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
                raise FormatError("string table: bitstream ran past the end")
            v |= ((self.data[byte] >> (self.pos & 7)) & 1) << i
            self.pos += 1
        return v


def _str_codes(dictionary: bytes, s: bytes) -> list[int]:
    codes = []
    for ch in s + b"\x00":
        idx = dictionary.find(bytes((ch,)))
        upper = False
        if idx < 0 and 0x41 <= ch <= 0x5A:
            idx = dictionary.find(bytes((ch + 0x20,)))
            upper = True
        if idx < 0 or idx >= 60:
            raise FormatError("string table: character 0x%02X is not encodable" % ch)
        if upper:
            codes.append(CODE_UPPER)
        if idx >= 30:
            codes.append(CODE_HIGH)
            idx -= 30
        codes.append(idx)
    return codes


def encode_table(dictionary: bytes, strings: list[bytes]) -> bytes:
    """60-byte dictionary first, then groups of exactly four strings (L-ST1)."""
    dictionary = bytes(dictionary)
    if len(dictionary) != 60:
        raise FormatError("string table: the dictionary must be 60 bytes")
    if b"\x00" not in dictionary:
        raise FormatError("string table: the dictionary must contain a NUL character")
    strings = [bytes(s) for s in strings]
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


def decode_table(data: bytes, offset: int = 0, end: int = None) -> list:
    """Decode a string table starting at ``offset``; ``end`` bounds the data.

    Returns strings in index order (group x 4 + slot). A pointer at or past the
    end of the data is skipped and a string whose bits run out is dropped, so
    an out-of-range final group pointer never fails.
    """
    if end is None:
        end = len(data)
    if offset < 0 or offset + 60 > end or end > len(data):
        raise FormatError("string table: dictionary runs past the end of the data")
    view = data[:end]
    dictionary = view[offset:offset + 60]
    base = offset + 60
    if base + 2 > len(view):
        raise FormatError("string table: no group pointer table")
    first = int.from_bytes(view[base:base + 2], "little")
    ngroups = first >> 1
    ptrs = []
    for i in range(ngroups):
        p0 = base + 2 * i
        if p0 + 2 > len(view):
            break
        ptrs.append(int.from_bytes(view[p0:p0 + 2], "little"))
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


def read_labstr(path: str) -> list:
    """Every table of LABSTR.BIN, each padded to a multiple of four as decoded."""
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 12 or data[:8] != LABSTR_MAGIC:
        raise FormatError("LABSTR: bad magic")
    count = int.from_bytes(data[8:10], "little")
    if 12 + 8 * count > len(data):
        raise FormatError("LABSTR: table directory runs past the end of the file")
    tables = []
    for i in range(count):
        off = int.from_bytes(data[12 + 4 * i:16 + 4 * i], "little")
        size = int.from_bytes(data[12 + 4 * count + 4 * i:16 + 4 * count + 4 * i], "little")
        if off + size > len(data):
            raise FormatError("LABSTR: table %d runs past the end of the file" % i)
        strings = decode_table(data[:off + size], off)
        tables.append([s.decode("latin-1") for s in strings])
    return tables


__all__ = ["decode_table", "encode_table", "read_labstr"]
