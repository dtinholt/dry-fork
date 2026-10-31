"""Huffman bitstreams and the Huffman msq block (SPEC-01 section 3,
SPEC-02 section 2.2).

One continuous bitstream, read most-significant bit first within each byte.
The tree is serialized pre-order; a leaf is a ``1`` bit followed by 8 symbol
bits, an internal node is a ``0`` bit, the left subtree, a separator bit
(ignored) and the right subtree.
"""

from __future__ import annotations

import heapq

from .errors import FormatError

MAX_DEPTH = 256


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
        return bytes(self.buf)  # the final partial byte is zero-padded


class BitReaderMSB:
    def __init__(self, data: bytes, byte_offset: int = 0) -> None:
        self.data = data
        self.pos = byte_offset * 8

    def bit(self) -> int:
        byte = self.pos >> 3
        if byte >= len(self.data):
            raise FormatError("huffman: bitstream ran past the end of the input")
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


# ---------------------------------------------------------------------------
# Tree building and serialization
# ---------------------------------------------------------------------------

def _build_tree(data: bytes):
    """Deterministic tree: leaves ordered by (frequency, symbol); merged nodes
    get creation numbers from 256 upward; the first node popped becomes the
    left child. A tree is a leaf (int) or a tuple (left, right)."""
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


def _write_tree(w: BitWriterMSB, node) -> None:
    if isinstance(node, int):
        w.bit(1)
        w.bits(node, 8)
    else:
        w.bit(0)
        _write_tree(w, node[0])
        w.bit(0)  # separator bit; decoders ignore its value, encoders write 0
        _write_tree(w, node[1])


def _codes(node, prefix=(), table=None):
    if table is None:
        table = {}
    if isinstance(node, int):
        table[node] = prefix  # single-leaf tree: the empty code
    else:
        _codes(node[0], prefix + (0,), table)
        _codes(node[1], prefix + (1,), table)
    return table


def _read_tree(r: BitReaderMSB, depth: int = 0):
    if depth > MAX_DEPTH:
        raise FormatError("huffman: tree deeper than %d" % MAX_DEPTH)
    if r.bit():
        return r.bits(8)
    left = _read_tree(r, depth + 1)
    r.bit()  # separator, ignored
    right = _read_tree(r, depth + 1)
    return (left, right)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def decode(data: bytes, out_size: int, offset: int = 0):
    """Decode exactly ``out_size`` bytes starting at byte ``offset``.

    Returns ``(decoded, byte_offset_after_sync)``. Raises ``FormatError`` on
    reading past the end or a tree deeper than 256.
    """
    if out_size < 0:
        raise FormatError("huffman: negative decoded size")
    if offset < 0 or offset > len(data):
        raise FormatError("huffman: offset outside the input")
    r = BitReaderMSB(data, offset)
    tree = _read_tree(r)
    out = bytearray(out_size)
    for i in range(out_size):
        node = tree
        while not isinstance(node, int):
            node = node[1] if r.bit() else node[0]
        out[i] = node
    return bytes(out), r.sync()


def encode(data: bytes) -> bytes:
    """Serialized tree plus payload bits, MSB first, zero-padded to a whole
    byte. The decoded size is not stored (SPEC-01 3.4)."""
    data = bytes(data)
    tree = _build_tree(data)
    w = BitWriterMSB()
    _write_tree(w, tree)
    codes = _codes(tree)
    for b in data:
        for bit in codes[b]:
            w.bit(bit)
    return w.getvalue()


def decode_msq(data: bytes, offset: int = 0, signature: bytes = b"msq"):
    """Huffman msq block: u32 size, 3-byte signature, disk byte, bitstream.

    Returns ``(payload, disk, next_offset)``. Raises ``FormatError`` on a
    wrong signature or a truncated header.
    """
    if offset + 8 > len(data):
        raise FormatError("huffman msq: header runs past the end of the input")
    size = int.from_bytes(data[offset:offset + 4], "little")
    if signature is not None and data[offset + 4:offset + 7] != signature:
        raise FormatError("huffman msq: bad signature %s at %d"
                          % (bytes(data[offset + 4:offset + 7]).hex(" ").upper(), offset))
    disk = data[offset + 7]
    payload, nxt = decode(data, size, offset + 8)
    return payload, disk, nxt


def encode_msq(payload: bytes, disk: int = 0, signature: bytes = b"msq") -> bytes:
    """The inverse of :func:`decode_msq`."""
    payload = bytes(payload)
    if len(signature) != 3:
        raise FormatError("huffman msq: signature must be three bytes")
    return (len(payload).to_bytes(4, "little") + bytes(signature)
            + bytes((disk & 0xFF,)) + encode(payload))


__all__ = [
    "decode",
    "encode",
    "decode_msq",
    "encode_msq",
    "BitReaderMSB",
    "BitWriterMSB",
]
