"""Graphics containers (SPEC-02 sections 6 to 8, 12.6, 12.7).

Tilesets, portraits, sprites and masks, the font, cursors, the title picture
and the ending animation.
"""

from __future__ import annotations

from . import codecs, huffman
from .errors import FormatError

PORTRAIT_BASE_SIZE = 4032
PORTRAIT_STRIDE = 48
TITLE_SIZE = 18432
TITLE_STRIDE = 144
ENDING_SIGNATURE = b"\x08\x67\x01"


def _r16(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o + 2], "little")


def unpack4(data: bytes, width: int) -> list:
    """Unpack packed 4-bpp rows: high nibble = left pixel."""
    bpr = width // 2
    rows = []
    for y in range(len(data) // bpr):
        row = []
        for x in range(bpr):
            v = data[y * bpr + x]
            row.append(v >> 4)
            row.append(v & 0x0F)
        rows.append(row)
    return rows


def pack4(pixels: list) -> bytes:
    out = bytearray()
    for row in pixels:
        for x in range(0, len(row), 2):
            out.append(((row[x] & 0x0F) << 4) | (row[x + 1] & 0x0F))
    return bytes(out)


def _planes_decode(b: bytes, w: int, h: int) -> list:
    bpr = w // 8
    plane = bpr * h
    return [[sum(((b[bit * plane + y * bpr + x // 8] >> (7 - x % 8)) & 1) << bit
                 for bit in range(4)) for x in range(w)] for y in range(h)]


# ---------------------------------------------------------------------------
# Tilesets (SPEC-02 6)
# ---------------------------------------------------------------------------

def read_tilesets(path: str) -> list:
    with open(path, "rb") as fh:
        data = fh.read()
    tilesets = []
    offset = 0
    while offset < len(data):
        payload, _disk, offset = huffman.decode_msq(data, offset)
        if len(payload) % 128:
            raise FormatError("tileset: decoded size %d is not a multiple of 128" % len(payload))
        tiles = []
        for i in range(0, len(payload), 128):
            raw = codecs.vertical_xor_decode(payload[i:i + 128], 8)
            tiles.append(unpack4(raw, 16))
        tilesets.append(tiles)
    return tilesets


# ---------------------------------------------------------------------------
# Portraits (SPEC-02 7)
# ---------------------------------------------------------------------------

def portrait_offset(tables: dict, raw_id: int, disk: int = 1):
    """The compact index of a raw portrait id, or ``None`` for 0x80."""
    if disk == 2:
        indices, offsets = tables["portraitIndices2"], tables["portraitOffsets2"]
    else:
        indices, offsets = tables["portraitIndices1"], tables["portraitOffsets1"]
    if raw_id < 0 or raw_id >= len(indices):
        return None
    idx = indices[raw_id]
    if idx == 0x80:
        return None
    if idx >= len(offsets):
        return None
    return offsets[idx]


def _decode_animation(payload: bytes):
    if len(payload) < 4:
        raise FormatError("portrait animation: payload shorter than four bytes")
    ss = _r16(payload, 0)
    if 2 + ss + 2 > len(payload):
        raise FormatError("portrait animation: script section runs past the end")
    sec = payload[2:2 + ss]
    scripts, cur, i = [], [], 0
    while i < len(sec):
        if sec[i] == 0xFF:
            scripts.append(cur)
            cur = []
            i += 1
        else:
            if i + 1 >= len(sec):
                raise FormatError("portrait animation: truncated script line")
            cur.append([sec[i], sec[i + 1]])
            i += 2
    us = _r16(payload, 2 + ss)
    if 4 + ss + us != len(payload):
        raise FormatError("portrait animation: size fields do not add up")
    ub = payload[4 + ss:4 + ss + us]
    updates, cur, i = [], [], 0
    while i < len(ub):
        h = _r16(ub, i)
        i += 2
        if h == 0xFFFF:
            updates.append(cur)
            cur = []
            continue
        n, off = (h >> 12) + 1, h & 0x0FFF
        if i + n > len(ub):
            raise FormatError("portrait animation: patch runs past the end")
        if off + n > PORTRAIT_BASE_SIZE:
            raise FormatError("portrait animation: patch outside the base image")
        cur.append([off, ub[i:i + n]])
        i += n
    return scripts, updates


def read_portrait(path: str, offset: int) -> dict:
    with open(path, "rb") as fh:
        data = fh.read()
    if offset < 0 or offset >= len(data):
        raise FormatError("portrait: offset %d outside the file" % offset)
    base_raw, _disk, nxt = huffman.decode_msq(data, offset)
    if len(base_raw) != PORTRAIT_BASE_SIZE:
        raise FormatError("portrait: base image is %d bytes, expected %d"
                          % (len(base_raw), PORTRAIT_BASE_SIZE))
    base = codecs.vertical_xor_decode(base_raw, PORTRAIT_STRIDE)
    anim, _disk2, _nxt = huffman.decode_msq(data, nxt)
    scripts, updates = _decode_animation(anim)
    return {"base": base, "scripts": scripts, "updates": updates}


def apply_portrait_update(image: bytes, update) -> bytes:
    """XOR-apply a list of ``[offset, bytes]`` patches (SPEC-02 7.2)."""
    img = bytearray(image)
    for off, data in update:
        data = bytes(data)
        if off < 0 or off + len(data) > len(img):
            raise FormatError("portrait update: patch outside the image")
        for k, v in enumerate(data):
            img[off + k] ^= v
    return bytes(img)


# ---------------------------------------------------------------------------
# Sprites, font, cursors (SPEC-02 8.1 to 8.3)
# ---------------------------------------------------------------------------

def read_sprites(ic_path: str, mask_path: str) -> list:
    with open(ic_path, "rb") as fh:
        ic = fh.read()
    with open(mask_path, "rb") as fh:
        mk = fh.read()
    if len(ic) % 128 or len(mk) % 32:
        raise FormatError("sprites: file size is not a whole number of records")
    n_ic, n_mk = len(ic) // 128, len(mk) // 32
    if n_ic != n_mk:
        raise FormatError("sprites: %d sprites but %d masks" % (n_ic, n_mk))
    out = []
    for n in range(n_ic):
        pixels = _planes_decode(ic[n * 128:(n + 1) * 128], 16, 16)
        m = mk[n * 32:(n + 1) * 32]
        transparent = [[(m[y * 2 + x // 8] >> (7 - x % 8)) & 1 for x in range(16)]
                       for y in range(16)]
        out.append({"pixels": pixels, "transparent": transparent})
    return out


def read_font(path: str) -> list:
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) % 32:
        raise FormatError("font: file size is not a whole number of glyphs")
    return [_planes_decode(data[g * 32:(g + 1) * 32], 8, 8) for g in range(len(data) // 32)]


def glyph_index(code: int, glyph_count: int) -> int:
    """L-FN1: glyph ``n`` renders code ``n + 0x20``; other codes render glyph 0."""
    idx = code - 0x20
    if 0 <= idx < glyph_count:
        return idx
    return 0


def read_cursors(path: str) -> list:
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) % 256:
        raise FormatError("cursors: file size is not a whole number of cursors")
    out = []
    for k in range(len(data) // 256):
        b = data[k * 256:(k + 1) * 256]
        pix, vis = [], []
        for y in range(16):
            prow, vrow = [], []
            for x in range(16):
                half, bi = x // 8, 7 - x % 8
                vrow.append((b[y * 4 + (1 - half)] >> bi) & 1)
                prow.append(sum(((b[bit * 64 + y * 4 + (3 - half)] >> bi) & 1) << bit
                                for bit in range(4)))
            pix.append(prow)
            vis.append(vrow)
        out.append({"pixels": pix, "visible": vis})
    return out


# ---------------------------------------------------------------------------
# Title and ending (SPEC-02 8.4, 8.5)
# ---------------------------------------------------------------------------

def read_title(path: str) -> bytes:
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) != TITLE_SIZE:
        raise FormatError("title: %d bytes, expected %d" % (len(data), TITLE_SIZE))
    return codecs.vertical_xor_decode(data, TITLE_STRIDE)


def _decode_ending_animation(payload: bytes) -> list:
    if len(payload) < 4:
        raise FormatError("ending animation: payload shorter than four bytes")
    n = _r16(payload, 0)
    if n != len(payload) - 4 or _r16(payload, len(payload) - 2) != 0:
        raise FormatError("ending animation: bad framing")
    i, ups = 2, []
    while True:
        if i + 2 > len(payload):
            raise FormatError("ending animation: truncated update")
        d = _r16(payload, i)
        i += 2
        if d == 0xFFFF:
            break
        patches = []
        while True:
            if i + 2 > len(payload):
                raise FormatError("ending animation: truncated patch list")
            o = _r16(payload, i)
            i += 2
            if o == 0xFFFF:
                break
            if i + 4 > len(payload):
                raise FormatError("ending animation: truncated patch")
            patches.append([o, payload[i:i + 4]])
            i += 4
        ups.append([d, patches])
    return ups


def read_ending(path: str) -> dict:
    with open(path, "rb") as fh:
        data = fh.read()
    base_raw, _disk, nxt = huffman.decode_msq(data, 0)
    if len(base_raw) != TITLE_SIZE:
        raise FormatError("ending: base image is %d bytes, expected %d" % (len(base_raw), TITLE_SIZE))
    base = codecs.vertical_xor_decode(base_raw, TITLE_STRIDE)
    anim, _disk2, _nxt = huffman.decode_msq(data, nxt, ENDING_SIGNATURE)
    return {"base": base, "updates": _decode_ending_animation(anim)}


def apply_ending_update(image: bytes, patches) -> bytes:
    """Patches replace four bytes each (SPEC-02 8.5)."""
    out = bytearray(image)
    for off, data in patches:
        data = bytes(data)
        cell_x, y = off % 40, off // 40
        bo = y * TITLE_STRIDE + cell_x * 4
        if bo + len(data) > len(out):
            raise FormatError("ending update: patch outside the image")
        out[bo:bo + len(data)] = data
    return bytes(out)


__all__ = [
    "read_tilesets", "read_portrait", "portrait_offset", "apply_portrait_update",
    "read_sprites", "read_font", "glyph_index", "read_cursors", "read_title",
    "read_ending", "apply_ending_update", "unpack4", "pack4",
]
