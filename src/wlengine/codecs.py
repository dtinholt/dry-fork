"""Byte-level codecs: rotating XOR and vertical XOR (SPEC-01 sections 2 and 4).

Rotating XOR is used by the GAME1/GAME2 msq blocks: whole-block mode for the
savegame payload and the shop item list, prefix mode inside map blocks.
"""

from __future__ import annotations

from .errors import ChecksumError, FormatError

KEY_STEP = 0x1F


def _rxor_checksum(plain: bytes) -> int:
    """Checksum over decoded bytes: start at 0, subtract each byte, mod 2^16."""
    c = 0
    for b in plain:
        c = (c - b) & 0xFFFF
    return c


def rotating_xor_encode(plain: bytes) -> bytes:
    """Return xor1, xor2, ciphertext (SPEC-01 2.4).

    The header bytes are not free: they must equal the low and high byte of
    the checksum of the plaintext, because the decoder compares its final
    checksum with ``xor1 | (xor2 << 8)``.
    """
    plain = bytes(plain)
    c = _rxor_checksum(plain)
    xor1, xor2 = c & 0xFF, c >> 8
    key = xor1 ^ xor2
    out = bytearray((xor1, xor2))
    for b in plain:
        out.append(b ^ key)
        key = (key + KEY_STEP) & 0xFF
    return bytes(out)


def _rxor_header(data: bytes, offset: int = 0):
    if offset + 2 > len(data):
        raise FormatError("rotating XOR: input shorter than the two header bytes")
    xor1, xor2 = data[offset], data[offset + 1]
    return xor1, xor2, xor1 ^ xor2, xor1 | (xor2 << 8)


def rotating_xor_decode_whole(data: bytes, n: int, offset: int = 0) -> bytes:
    """Whole-block mode: decode exactly ``n`` bytes after the two header bytes.

    Raises ``FormatError`` when the input is too short and ``ChecksumError``
    when the final checksum does not match the header (SPEC-01 2.5).
    """
    if n < 0:
        raise FormatError("rotating XOR: negative length")
    if offset + 2 + n > len(data):
        raise FormatError("rotating XOR: input shorter than 2 + %d bytes" % n)
    xor1, xor2, key, end = _rxor_header(data, offset)
    c = 0
    out = bytearray(n)
    base = offset + 2
    for i in range(n):
        d = data[base + i] ^ key
        out[i] = d
        c = (c - d) & 0xFFFF
        key = (key + KEY_STEP) & 0xFF
    if c != end:
        raise ChecksumError("rotating XOR: checksum mismatch (got %04X want %04X)" % (c, end))
    return bytes(out)


def rotating_xor_decode_prefix(data: bytes, body_size: int, offset: int = 0):
    """Prefix mode (SPEC-01 2.6).

    ``data[offset:offset+2]`` are the header bytes; the body is the next
    ``body_size`` bytes. Decryption runs while the running checksum differs
    from ``endChecksum``, testing before each byte, so an ``endChecksum`` of 0
    gives an empty prefix. The remaining body bytes are plain.

    Returns ``(decoded_body, prefix_length)``. Raises ``FormatError`` when the
    checksum never matches inside the body.
    """
    if body_size < 0:
        raise FormatError("rotating XOR: negative body size")
    xor1, xor2, key, end = _rxor_header(data, offset)
    base = offset + 2
    if base + body_size > len(data):
        raise FormatError("rotating XOR: body runs past the end of the input")
    body = bytearray(data[base:base + body_size])
    c = 0
    i = 0
    while True:
        if c == end:
            break
        if i >= body_size:
            raise FormatError("rotating XOR: checksum never matched inside the body")
        d = body[i] ^ key
        body[i] = d
        c = (c - d) & 0xFFFF
        key = (key + KEY_STEP) & 0xFF
        i += 1
    return bytes(body), i


def rotating_xor_prefix_length(data: bytes, body_size: int, offset: int = 0) -> int:
    """Prefix length found by prefix mode for a body of ``body_size`` bytes."""
    return rotating_xor_decode_prefix(data, body_size, offset)[1]


def rotating_xor_decode(data: bytes, mode: str, length: int) -> bytes:
    """Dispatch on ``mode``: ``"whole"`` or ``"prefix"`` (SPEC-07 2.1)."""
    if mode == "whole":
        return rotating_xor_decode_whole(data, length)
    if mode == "prefix":
        return rotating_xor_decode_prefix(data, length)[0]
    raise FormatError("rotating XOR: unknown mode %r" % (mode,))


def rotating_xor_prefix_is_unambiguous(prefix: bytes) -> bool:
    """True when prefix-mode decoding of ``rotating_xor_encode(prefix)`` stops
    exactly at ``len(prefix)`` (SPEC-01 2.7)."""
    s = 0
    for k in range(len(prefix) - 1, -1, -1):
        s = (s + prefix[k]) & 0xFFFF
        if s == 0:
            return False
    return len(prefix) > 0


# ---------------------------------------------------------------------------
# Vertical XOR (SPEC-01 section 4)
# ---------------------------------------------------------------------------

def vertical_xor_decode(data: bytes, stride: int) -> bytes:
    """Row predictor over bytes: ``out[i] = data[i] XOR out[i - stride]``."""
    out = bytearray(data)
    if stride <= 0:
        return bytes(out)
    for i in range(stride, len(out)):
        out[i] ^= out[i - stride]
    return bytes(out)


def vertical_xor_encode(data: bytes, stride: int) -> bytes:
    """``enc[i] = dec[i] XOR dec[i - stride]`` for ``i >= stride``."""
    out = bytearray(data)
    if stride <= 0:
        return bytes(out)
    for i in range(len(out) - 1, stride - 1, -1):
        out[i] = data[i] ^ data[i - stride]
    return bytes(out)


__all__ = [
    "rotating_xor_encode",
    "rotating_xor_decode",
    "rotating_xor_decode_whole",
    "rotating_xor_decode_prefix",
    "rotating_xor_prefix_length",
    "rotating_xor_prefix_is_unambiguous",
    "vertical_xor_decode",
    "vertical_xor_encode",
]
