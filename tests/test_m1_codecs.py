"""M1: codecs (SPEC-01). Oracle: SPEC/reference/codecs_ref.py vectors plus
seeded random round trips. API: SPEC-07 section 2.1 to 2.3."""

from __future__ import annotations

import random

import pytest

import wl_support as W
from wl_support import call, check_bytes, check_eq, expect_error, fail

pytestmark = pytest.mark.milestone("M1")

H = bytes.fromhex


def _h(s: str) -> bytes:
    return bytes.fromhex(s.replace(" ", ""))


C = W.codecs_oracle()

RX = {"RX-%d" % (i + 1): (p, e) for i, (p, e) in enumerate(C.RXOR_WHOLE_VECTORS)}
RP = {"RP-%d" % (i + 1): v for i, v in enumerate(C.RXOR_PREFIX_VECTORS)}
HU = {"HU-%d" % (i + 1): v for i, v in enumerate(C.HUFF_VECTORS)}
VX = {"VX-%d" % (i + 1): v for i, v in enumerate(C.VXOR_VECTORS)}


# ---- rotating XOR, whole-block mode (SPEC-01 sections 2.1 to 2.5, 2.8) -----

@pytest.mark.parametrize("vid", sorted(RX))
def test_rotating_xor_whole_decode(vid):
    plain, enc = (_h(x) for x in RX[vid])
    got = call("codecs.rotating_xor_decode", enc, "whole", len(plain))
    check_bytes("%s whole-mode decode of %d bytes" % (vid, len(plain)), got, plain)


@pytest.mark.parametrize("vid", sorted(RX))
def test_rotating_xor_encode(vid):
    plain, enc = (_h(x) for x in RX[vid])
    got = call("codecs.rotating_xor_encode", plain)
    check_bytes("%s encode (header bytes are the checksum, SPEC-01 2.4)" % vid, got, enc)


def test_rotating_xor_whole_checksum_error():
    bad = bytearray(_h(RX["RX-1"][1]))
    bad[3] = 0x24  # RX-C: byte 3 changed from 25 to 24
    expect_error("ChecksumError", "codecs.rotating_xor_decode", bytes(bad), "whole", 4, what="RX-C")


def test_rotating_xor_whole_short_input():
    expect_error("FormatError", "codecs.rotating_xor_decode", _h("FA FF 05 25"), "whole", 4,
                 what="RX-1 truncated to 4 bytes, length 4")


# ---- rotating XOR, prefix mode (SPEC-01 sections 2.6, 2.7, 2.8) -------------

@pytest.mark.parametrize("vid", sorted(RP))
def test_rotating_xor_prefix_body(vid):
    pre, suf, raw = (_h(x) for x in RP[vid])
    got = call("codecs.rotating_xor_decode", raw, "prefix", len(pre) + len(suf))
    check_bytes("%s prefix-mode body (B = %d)" % (vid, len(pre) + len(suf)), got, pre + suf)


@pytest.mark.parametrize("vid", sorted(RP))
def test_rotating_xor_prefix_length(vid):
    pre, suf, raw = (_h(x) for x in RP[vid])
    got = call("codecs.rotating_xor_prefix_length", raw, len(pre) + len(suf))
    check_eq("%s prefix length (B = %d)" % (vid, len(pre) + len(suf)), got, len(pre))


def test_rotating_xor_prefix_early_stop():
    raw = _h("F4 FF 0E 2D 49")  # RP-N
    body = call("codecs.rotating_xor_decode", raw, "prefix", 3)
    check_bytes("RP-N body (the decoder must not fix the early stop)", body, _h("05 07 49"))
    n = call("codecs.rotating_xor_prefix_length", raw, 3)
    check_eq("RP-N prefix length", n, 2)


def test_rotating_xor_prefix_empty():
    raw = _h(RX["RX-3"][1])  # endChecksum 0: the loop stops before the first byte
    body = call("codecs.rotating_xor_decode", raw, "prefix", 4)
    check_bytes("RX-3 read in prefix mode: body is plain", body, raw[2:])
    check_eq("RX-3 read in prefix mode: prefix length", call("codecs.rotating_xor_prefix_length", raw, 4), 0)


def test_rotating_xor_prefix_no_match():
    expect_error("FormatError", "codecs.rotating_xor_decode", _h("00 01 41"), "prefix", 1,
                 what="header 00 01, B = 1, checksum never matches")


# ---- Huffman (SPEC-01 section 3) --------------------------------------------

@pytest.mark.parametrize("vid", sorted(HU))
def test_huffman_decode(vid):
    dec, enc = (_h(x) for x in HU[vid])
    got = call("huffman.decode", enc, len(dec))
    if not (isinstance(got, (tuple, list)) and len(got) == 2):
        fail("huffman.decode must return (bytes, next_offset), got %s" % W.short(got))
    check_bytes("%s decoded bytes (decodedSize %d)" % (vid, len(dec)), got[0], dec)
    check_eq("%s byte offset after sync" % vid, got[1], len(enc))


def test_huffman_separator_bit_ignored():
    got = call("huffman.decode", _h("40 70 0A C0"), 6)
    check_bytes("HU-S decoded bytes", got[0], _h("00 01 00 01 00 00"))


def test_huffman_next_offset_with_trailing_bytes():
    enc = _h(HU["HU-3"][1]) + _h("AA 55")
    got = call("huffman.decode", enc, 11)
    check_bytes("HU-3 + AA 55 decoded bytes", got[0], _h(HU["HU-3"][0]))
    check_eq("HU-3 + AA 55 offset after sync", got[1], 10)


def test_huffman_decode_at_offset():
    dec, enc = (_h(x) for x in HU["HU-5"])
    got = call("huffman.decode", _h("99 99 99") + enc, len(dec), 3)
    check_bytes("HU-5 at byte offset 3: decoded bytes", got[0], dec)
    check_eq("HU-5 at byte offset 3: offset after sync", got[1], 3 + len(enc))


def test_huffman_read_past_end():
    expect_error("FormatError", "huffman.decode", _h(HU["HU-3"][1])[:5], 11,
                 what="HU-3 cut to 5 bytes, decodedSize 11")


def test_huffman_tree_too_deep():
    expect_error("FormatError", "huffman.decode", bytes(64), 1, what="64 zero bytes: tree deeper than 256")


@pytest.mark.parametrize("vid", sorted(HU))
def test_huffman_encode_round_trip(vid):
    dec = _h(HU[vid][0])
    enc = call("huffman.encode", dec)
    if not isinstance(enc, (bytes, bytearray)):
        fail("huffman.encode must return bytes, got %s" % type(enc).__name__)
    try:
        out, nxt = C.huff_decode(bytes(enc), len(dec))
    except ValueError as e:
        fail("%s: engine encoding is not a valid bitstream for the reference decoder: %s" % (vid, e))
    check_bytes("%s: reference decode of the engine encoding" % vid, out, dec)
    check_eq("%s: engine encoding length (zero padding to a whole byte only)" % vid, len(enc), nxt)


# ---- vertical XOR (SPEC-01 section 4) ---------------------------------------

@pytest.mark.parametrize("vid", sorted(VX))
def test_vertical_xor_decode(vid):
    stride, dec, enc = VX[vid][0], _h(VX[vid][1]), _h(VX[vid][2])
    check_bytes("%s decode, stride %d" % (vid, stride), call("codecs.vertical_xor_decode", enc, stride), dec)


@pytest.mark.parametrize("vid", sorted(VX))
def test_vertical_xor_encode(vid):
    stride, dec, enc = VX[vid][0], _h(VX[vid][1]), _h(VX[vid][2])
    check_bytes("%s encode, stride %d" % (vid, stride), call("codecs.vertical_xor_encode", dec, stride), enc)


def test_vertical_xor_short_buffer():
    check_bytes("buffer of 3 bytes with stride 8 is unchanged",
                call("codecs.vertical_xor_decode", _h("01 02 03"), 8), _h("01 02 03"))


# ---- seeded random round trips (SPEC-01 section 6) ---------------------------

SIZES = (1, 2, 3, 7, 64, 128, 760, 2048, 4032)
ALPHABETS = (1, 2, 3, 16, 256)
CASES = ["rand-%02d" % i for i in range(8)]


def _case(cid: str, salt: int) -> tuple[bytes, random.Random]:
    rng = random.Random(1988 * 1000 + salt * 100 + int(cid[-2:]))
    n = rng.choice(SIZES)
    a = rng.choice(ALPHABETS)
    return bytes(rng.randrange(a) for _ in range(n)), rng


@pytest.mark.parametrize("cid", CASES)
def test_random_rotating_xor_decode(cid):
    data, _ = _case(cid, 1)
    enc = C.rxor_encode(data)
    got = call("codecs.rotating_xor_decode", enc, "whole", len(data))
    check_bytes("%s: whole-mode decode of a %d-byte reference encoding" % (cid, len(data)), got, data)


@pytest.mark.parametrize("cid", CASES)
def test_random_rotating_xor_encode(cid):
    data, _ = _case(cid, 2)
    got = call("codecs.rotating_xor_encode", data)
    check_bytes("%s: encoding of %d bytes" % (cid, len(data)), got, C.rxor_encode(data))


@pytest.mark.parametrize("cid", CASES[:6])
def test_random_rotating_xor_prefix(cid):
    data, rng = _case(cid, 3)
    while not C.rxor_prefix_is_unambiguous(data):
        data = bytes(rng.randrange(1, 256) for _ in range(len(data)))
    raw = C.rxor_encode(data) + b"\x20\x65\x00"
    b = len(data) + 3
    check_eq("%s: prefix length of a %d-byte encrypted prefix" % (cid, len(data)),
             call("codecs.rotating_xor_prefix_length", raw, b), len(data))
    check_bytes("%s: prefix-mode body" % cid, call("codecs.rotating_xor_decode", raw, "prefix", b),
                data + b"\x20\x65\x00")


@pytest.mark.parametrize("cid", CASES)
def test_random_huffman_decode(cid):
    data, _ = _case(cid, 4)
    enc = C.huff_encode(data) + b"\xAA\x55"
    got = call("huffman.decode", enc, len(data))
    check_bytes("%s: decode of a %d-byte reference encoding" % (cid, len(data)), got[0], data)
    check_eq("%s: offset after sync" % cid, got[1], len(enc) - 2)


@pytest.mark.parametrize("cid", CASES)
def test_random_huffman_encode(cid):
    data, _ = _case(cid, 5)
    enc = call("huffman.encode", data)
    try:
        out, nxt = C.huff_decode(bytes(enc), len(data))
    except (ValueError, TypeError) as e:
        fail("%s: engine encoding of %d bytes rejected by the reference decoder: %s" % (cid, len(data), e))
    check_bytes("%s: reference decode of the engine encoding of %d bytes" % (cid, len(data)), out, data)
    back = call("huffman.decode", bytes(enc), len(data))
    check_bytes("%s: engine decode of its own encoding" % cid, back[0], data)


@pytest.mark.parametrize("cid", CASES)
def test_random_vertical_xor(cid):
    data, rng = _case(cid, 6)
    stride = rng.choice((1, 2, 8, 48, 144))
    enc = C.vxor_encode(data, stride)
    check_bytes("%s: decode, %d bytes, stride %d" % (cid, len(data), stride),
                call("codecs.vertical_xor_decode", enc, stride), data)
    check_bytes("%s: encode, %d bytes, stride %d" % (cid, len(data), stride),
                call("codecs.vertical_xor_encode", data, stride), enc)
