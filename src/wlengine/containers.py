"""Containers and records (SPEC-02 sections 3 to 5 and 12).

LABTABLES.BIN stands in for the WL.EXE tables; the savegame and shop item list
are rotating-XOR msq blocks inside GAME1/GAME2.
"""

from __future__ import annotations

from . import codecs
from .errors import ChecksumError, FormatError

LABTABLES_MAGIC = b"WLLABTB1"
LABTABLES_SIZE = 0x438

# field: (offset, element format, count)
LT = {
    "mapOffsets": (0x008, "u32", 42),
    "tileMapOffsets": (0x0B0, "u16", 50),
    "locationMapping": (0x114, "u8", 50),
    "mapSizes": (0x146, "u8", 50),
    "sharedLocations": (0x178, "u8", 125),
    "mobSpriteMap": (0x1F5, "u8", 6),
    "savegameOffsets": (0x1FC, "u32", 2),
    "savegameSize": (0x204, "u16", 1),
    "shopListRelOffsets": (0x206, "u16", 4),
    "mapCounts": (0x20E, "u8", 2),
    "shopListCounts": (0x210, "u8", 2),
    "tilesetOffsets": (0x214, "u32", 9),
    "tilesetSizes": (0x238, "u16", 9),
    "portraitOffsets1": (0x24C, "u32", 34),
    "portraitOffsets2": (0x2D4, "u32", 49),
    "portraitIndices1": (0x398, "u8", 80),
    "portraitIndices2": (0x3E8, "u8", 80),
}
_WIDTH = {"u8": 1, "u16": 2, "u32": 4}

SAVEGAME_RESERVED = 0x1206
SAVEGAME_PAYLOAD = 0x800
SHOP_HEADER = bytes.fromhex("606060003708F839")
SHOP_BLOCK = 766
SHOP_PAYLOAD = 760


def _u16(v: int) -> bytes:
    return (v & 0xFFFF).to_bytes(2, "little")


def _u24(v: int) -> bytes:
    return (v & 0xFFFFFF).to_bytes(3, "little")


def _u32(v: int) -> bytes:
    return (v & 0xFFFFFFFF).to_bytes(4, "little")


def _r16(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o + 2], "little")


def _r24(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o + 3], "little")


def _r32(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o + 4], "little")


def _cstr(b: bytes, n: int) -> bytes:
    raw = bytes(b[:n])
    i = raw.find(b"\x00")
    return raw if i < 0 else raw[:i]


def _fixed(text, n: int) -> bytes:
    raw = text.encode("latin-1") if isinstance(text, str) else bytes(text)
    if len(raw) >= n:
        return raw[:n]
    return raw + bytes(n - len(raw))


# ---------------------------------------------------------------------------
# LABTABLES.BIN (SPEC-02 12.2)
# ---------------------------------------------------------------------------

def read_tables(path: str) -> dict:
    with open(path, "rb") as fh:
        b = fh.read()
    if len(b) != LABTABLES_SIZE or b[:8] != LABTABLES_MAGIC:
        raise FormatError("LABTABLES: bad magic or size")
    t = {}
    for k, (off, fmt, n) in LT.items():
        w = _WIDTH[fmt]
        vals = [int.from_bytes(b[off + i * w:off + (i + 1) * w], "little") for i in range(n)]
        t[k] = vals[0] if n == 1 else vals
    return t


def resolve_location(tables: dict, location: int):
    """SPEC-02 3.4 after the shared-location step.

    Returns ``(location, disk_code, map_index)``; ``FormatError`` for a
    location code of 0.
    """
    if location < 0:
        raise FormatError("location %d is out of range" % location)
    if location >= 128:
        shared = tables["sharedLocations"]
        if location - 128 >= len(shared):
            raise FormatError("location %d has no shared-location entry" % location)
        location = shared[location - 128]
    mapping = tables["locationMapping"]
    if location >= len(mapping):
        raise FormatError("location %d is out of range" % location)
    code = mapping[location]
    if code == 0:
        raise FormatError("location %d has code 0 (unused slot)" % location)
    return location, code >> 6, code & 0x3F


# ---------------------------------------------------------------------------
# Character record (SPEC-02 4.4)
# ---------------------------------------------------------------------------

_ATTRS = ("strength", "intelligence", "luck", "speed", "agility", "dexterity", "charisma")


def decode_character(record: bytes) -> dict:
    if len(record) < 0x100:
        raise FormatError("character record: shorter than 0x100 bytes")
    b = record
    c = {"name": _cstr(b[0x00:0x0E], 14).decode("latin-1")}
    for i, k in enumerate(_ATTRS):
        c[k] = b[0x0E + i]
    c.update({
        "money": _r24(b, 0x15), "gender": b[0x18], "nationality": b[0x19],
        "armorClass": b[0x1A], "maxCon": _r16(b, 0x1B), "curCon": _r16(b, 0x1D),
        "weaponSlot": b[0x1F], "skillPoints": b[0x20], "experience": _r24(b, 0x21),
        "level": b[0x24], "armorSlot": b[0x25], "lastCon": _r16(b, 0x26),
        "afflictions": b[0x28], "npc": b[0x29], "itemRefuse": b[0x2B],
        "skillRefuse": b[0x2C], "attribRefuse": b[0x2D], "tradeRefuse": b[0x2E],
        "joinString": b[0x30], "willingness": b[0x31],
        "rank": _cstr(b[0x32:0x4B], 25).decode("latin-1"), "gameWon": b[0x4B],
        "specialPromotion": b[0x4C],
    })
    c["skills"] = [[b[0x80 + 2 * i], b[0x81 + 2 * i]] for i in range(30) if b[0x80 + 2 * i]]
    c["items"] = [[b[0xBD + 2 * i], b[0xBE + 2 * i]] for i in range(30) if b[0xBD + 2 * i]]
    return c


def encode_character(character: dict) -> bytes:
    c = character
    b = bytearray(0x100)
    b[0x00:0x0E] = _fixed(c.get("name", ""), 14)
    for i, k in enumerate(_ATTRS):
        b[0x0E + i] = c.get(k, 0) & 0xFF
    b[0x15:0x18] = _u24(c.get("money", 0))
    b[0x18] = c.get("gender", 0) & 0xFF
    b[0x19] = c.get("nationality", 0) & 0xFF
    b[0x1A] = c.get("armorClass", 0) & 0xFF
    b[0x1B:0x1D] = _u16(c.get("maxCon", 0))
    b[0x1D:0x1F] = _u16(c.get("curCon", 0))
    b[0x1F] = c.get("weaponSlot", 0) & 0xFF
    b[0x20] = c.get("skillPoints", 0) & 0xFF
    b[0x21:0x24] = _u24(c.get("experience", 0))
    b[0x24] = c.get("level", 0) & 0xFF
    b[0x25] = c.get("armorSlot", 0) & 0xFF
    b[0x26:0x28] = _u16(c.get("lastCon", 0))
    b[0x28] = c.get("afflictions", 0) & 0xFF
    b[0x29] = c.get("npc", 0) & 0xFF
    b[0x2B] = c.get("itemRefuse", 0) & 0xFF
    b[0x2C] = c.get("skillRefuse", 0) & 0xFF
    b[0x2D] = c.get("attribRefuse", 0) & 0xFF
    b[0x2E] = c.get("tradeRefuse", 0) & 0xFF
    b[0x30] = c.get("joinString", 0) & 0xFF
    b[0x31] = c.get("willingness", 0) & 0xFF
    b[0x32:0x4B] = _fixed(c.get("rank", ""), 25)
    b[0x4B] = c.get("gameWon", 0) & 0xFF
    b[0x4C] = c.get("specialPromotion", 0) & 0xFF
    for i, (sid, lvl) in enumerate(c.get("skills", [])[:30]):
        b[0x80 + 2 * i] = sid & 0xFF
        b[0x81 + 2 * i] = lvl & 0xFF
    for i, (iid, st) in enumerate(c.get("items", [])[:30]):
        b[0xBD + 2 * i] = iid & 0xFF
        b[0xBE + 2 * i] = st & 0xFF
    return bytes(b)


# ---------------------------------------------------------------------------
# Savegame block (SPEC-02 4)
# ---------------------------------------------------------------------------

def _check_msq_header(game: bytes, offset: int, what: str) -> int:
    if offset < 0 or offset + 4 > len(game):
        raise FormatError("%s: header runs past the end of the file" % what)
    if game[offset:offset + 3] != b"msq" or game[offset + 3] not in (0x30, 0x31):
        raise FormatError("%s: bad header %s" % (what, bytes(game[offset:offset + 4]).hex(" ").upper()))
    return game[offset + 3] - 0x30


def decode_savegame(game: bytes, offset: int) -> dict:
    _check_msq_header(game, offset, "savegame")
    p = codecs.rotating_xor_decode_whole(game, SAVEGAME_PAYLOAD, offset + 4)
    groups = []
    for g in range(4):
        o = g * 14
        groups.append({"order": list(p[o + 1:o + 8]), "x": p[o + 8], "y": p[o + 9],
                       "map": p[o + 10], "prevX": p[o + 11], "prevY": p[o + 12],
                       "prevMap": p[o + 13]})
    sg = {"groups": groups, "viewportX": p[0x78], "viewportY": p[0x79],
          "currentMembers": p[0x7D], "currentParty": p[0x7E], "currentMap": p[0x7F],
          "totalMembers": p[0x80], "extraGroups": p[0x81], "minute": p[0x83],
          "hour": p[0x84], "combatScrollSpeed": p[0x85], "serial": _r32(p, 0xF5)}
    sg["characters"] = [decode_character(p[0x100 + i * 0x100:0x200 + i * 0x100]) for i in range(7)]
    return sg


def encode_savegame(savegame: dict, disk: int) -> bytes:
    sg = savegame
    p = bytearray(SAVEGAME_PAYLOAD)
    for g, grp in enumerate(sg.get("groups", [])[:4]):
        o = g * 14
        order = list(grp.get("order", [0] * 7))[:7]
        p[o + 1:o + 1 + len(order)] = bytes(x & 0xFF for x in order)
        p[o + 8] = grp.get("x", 0) & 0xFF
        p[o + 9] = grp.get("y", 0) & 0xFF
        p[o + 10] = grp.get("map", 0) & 0xFF
        p[o + 11] = grp.get("prevX", 0) & 0xFF
        p[o + 12] = grp.get("prevY", 0) & 0xFF
        p[o + 13] = grp.get("prevMap", 0) & 0xFF
    p[0x78] = sg.get("viewportX", 0) & 0xFF
    p[0x79] = sg.get("viewportY", 0) & 0xFF
    p[0x7D] = sg.get("currentMembers", 0) & 0xFF
    p[0x7E] = sg.get("currentParty", 0) & 0xFF
    p[0x7F] = sg.get("currentMap", 0) & 0xFF
    p[0x80] = sg.get("totalMembers", 0) & 0xFF
    p[0x81] = sg.get("extraGroups", 0) & 0xFF
    p[0x83] = sg.get("minute", 0) & 0xFF
    p[0x84] = sg.get("hour", 0) & 0xFF
    p[0x85] = sg.get("combatScrollSpeed", 0) & 0xFF
    p[0xF5:0xF9] = _u32(sg.get("serial", 0))
    for i, ch in enumerate(sg.get("characters", [])[:7]):
        p[0x100 + i * 0x100:0x200 + i * 0x100] = encode_character(ch)
    block = b"msq" + bytes(((0x30 + disk) & 0xFF,)) + codecs.rotating_xor_encode(bytes(p))
    return block + bytes(SAVEGAME_RESERVED - len(block))


# ---------------------------------------------------------------------------
# Shop item list block (SPEC-02 5)
# ---------------------------------------------------------------------------

def decode_shop_list(game: bytes, offset: int) -> dict:
    _check_msq_header(game, offset, "shop list")
    p = codecs.rotating_xor_decode_whole(game, SHOP_PAYLOAD, offset + 4)
    items = []
    for i in range(94):
        r = p[8 + 8 * i:16 + 8 * i]
        items.append({"price": _r16(r, 0), "stock": r[2], "type": r[3] >> 3,
                      "lowFlags": r[3] & 7, "capacity": r[4], "skill": r[5],
                      "damage": r[6], "ammo": r[7]})
    return {"header": p[:8], "items": items}


def encode_shop_list(items: list, disk: int) -> bytes:
    p = bytearray(SHOP_HEADER)
    for i in range(94):
        it = items[i] if i < len(items) else None
        if it is None:
            p += bytes(8)
        else:
            p += (_u16(it.get("price", 0))
                  + bytes((it.get("stock", 0) & 0xFF,
                           ((it.get("type", 0) & 0x1F) << 3) | (it.get("lowFlags", 0) & 7),
                           it.get("capacity", 0) & 0xFF,
                           it.get("skill", 0) & 0xFF,
                           it.get("damage", 0) & 0xFF,
                           it.get("ammo", 0) & 0xFF)))
    block = b"msq" + bytes(((0x30 + disk) & 0xFF,)) + codecs.rotating_xor_encode(bytes(p))
    if len(block) != SHOP_BLOCK:
        raise FormatError("shop list: encoded block is %d bytes, expected %d" % (len(block), SHOP_BLOCK))
    return block


__all__ = [
    "read_tables", "resolve_location", "decode_savegame", "encode_savegame",
    "decode_character", "encode_character", "decode_shop_list", "encode_shop_list",
]
