#!/usr/bin/env python3
"""Synthetic fixture generator for the Wasteland clean-room engine.

Writes a complete, original (non-Interplay) data set in the formats of
SPEC-02-containers.md and SPEC-03-maps.md, plus manifest.json holding the
ground truth an engine must reproduce when it decodes the files.

    python3 fixtures_gen.py OUTDIR [--seed N]   write the data set
    python3 fixtures_gen.py --selftest          write to a temp dir, re-read
                                                every file with codecs_ref and
                                                compare with the manifest

Deterministic: the same seed gives byte-identical files. Standard library only.
Every structure the generator writes is either documented (cited in the SPEC
files) or a "lab rule v1" defined in SPEC-02 section 12 and SPEC-03 section 9.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codecs_ref as C  # noqa: E402

DEFAULT_SEED = 19880101

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def u16(v: int) -> bytes:
    return (v & 0xFFFF).to_bytes(2, "little")


def u24(v: int) -> bytes:
    return (v & 0xFFFFFF).to_bytes(3, "little")


def u32(v: int) -> bytes:
    return (v & 0xFFFFFFFF).to_bytes(4, "little")


def r16(b: bytes, o: int) -> int:
    return b[o] | (b[o + 1] << 8)


def r24(b: bytes, o: int) -> int:
    return b[o] | (b[o + 1] << 8) | (b[o + 2] << 16)


def r32(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o + 4], "little")


def s(b: bytes) -> str:
    """bytes -> JSON-safe string (latin-1, one char per byte)."""
    return b.decode("latin-1")


def cstr(b: bytes, n: int) -> bytes:
    """Read a NUL-terminated string from a fixed field of n bytes."""
    b = b[:n]
    i = b.find(b"\x00")
    return b if i < 0 else b[:i]


def fixed(text: bytes, n: int) -> bytes:
    assert len(text) < n, (text, n)
    return text + bytes(n - len(text))


def pack4(pixels: list[list[int]]) -> bytes:
    """Rows of 4-bit pixels -> packed bytes, high nibble = left pixel."""
    out = bytearray()
    for row in pixels:
        for x in range(0, len(row), 2):
            out.append((row[x] << 4) | row[x + 1])
    return bytes(out)


def unpack4(data: bytes, width: int) -> list[list[int]]:
    rows = []
    stride = width // 2
    for y in range(len(data) // stride):
        row = []
        for b in data[y * stride:(y + 1) * stride]:
            row += [b >> 4, b & 0x0F]
        rows.append(row)
    return rows


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------
# Lab tables file (SPEC-02 section 12.2): stands in for the WL.EXE tables
# ---------------------------------------------------------------------------

LABTABLES_MAGIC = b"WLLABTB1"
LABTABLES_SIZE = 0x438
LT = {  # field: (offset, element format, count)
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
_W = {"u8": 1, "u16": 2, "u32": 4}


def labtables_encode(t: dict) -> bytes:
    out = bytearray(LABTABLES_SIZE)
    out[0:8] = LABTABLES_MAGIC
    for k, (off, fmt, n) in LT.items():
        vals = t[k] if isinstance(t[k], list) else [t[k]]
        assert len(vals) == n, (k, len(vals), n)
        w = _W[fmt]
        for i, v in enumerate(vals):
            out[off + i * w:off + (i + 1) * w] = (v & ((1 << (8 * w)) - 1)).to_bytes(w, "little")
    return bytes(out)


def labtables_decode(b: bytes) -> dict:
    if b[0:8] != LABTABLES_MAGIC or len(b) != LABTABLES_SIZE:
        raise ValueError("LABTABLES: bad magic or size")
    t = {}
    for k, (off, fmt, n) in LT.items():
        w = _W[fmt]
        vals = [int.from_bytes(b[off + i * w:off + (i + 1) * w], "little") for i in range(n)]
        t[k] = vals[0] if n == 1 else vals
    return t


# ---------------------------------------------------------------------------
# Character record, savegame, shop list (savegame.md, shopitemlist.md)
# ---------------------------------------------------------------------------

def char_encode(c: dict) -> bytes:
    b = bytearray(0x100)
    b[0x00:0x0E] = fixed(c["name"], 14)
    for i, k in enumerate(("strength", "intelligence", "luck", "speed", "agility", "dexterity", "charisma")):
        b[0x0E + i] = c[k]
    b[0x15:0x18] = u24(c["money"])
    b[0x18] = c["gender"]
    b[0x19] = c["nationality"]
    b[0x1A] = c["armorClass"]
    b[0x1B:0x1D] = u16(c["maxCon"])
    b[0x1D:0x1F] = u16(c["curCon"])
    b[0x1F] = c["weaponSlot"]
    b[0x20] = c["skillPoints"]
    b[0x21:0x24] = u24(c["experience"])
    b[0x24] = c["level"]
    b[0x25] = c["armorSlot"]
    b[0x26:0x28] = u16(c["lastCon"])
    b[0x28] = c["afflictions"]
    b[0x29] = c["npc"]
    b[0x2B] = c["itemRefuse"]
    b[0x2C] = c["skillRefuse"]
    b[0x2D] = c["attribRefuse"]
    b[0x2E] = c["tradeRefuse"]
    b[0x30] = c["joinString"]
    b[0x31] = c["willingness"]
    b[0x32:0x4B] = fixed(c["rank"], 25)
    b[0x4B] = c["gameWon"]
    b[0x4C] = c["specialPromotion"]
    for i, (sid, lvl) in enumerate(c["skills"]):
        b[0x80 + 2 * i] = sid
        b[0x81 + 2 * i] = lvl
    for i, (iid, st) in enumerate(c["items"]):
        b[0xBD + 2 * i] = iid
        b[0xBE + 2 * i] = st
    return bytes(b)


def char_decode(b: bytes) -> dict:
    assert len(b) == 0x100
    c = {"name": s(cstr(b[0x00:0x0E], 14))}
    for i, k in enumerate(("strength", "intelligence", "luck", "speed", "agility", "dexterity", "charisma")):
        c[k] = b[0x0E + i]
    c.update({
        "money": r24(b, 0x15), "gender": b[0x18], "nationality": b[0x19],
        "armorClass": b[0x1A], "maxCon": r16(b, 0x1B), "curCon": r16(b, 0x1D),
        "weaponSlot": b[0x1F], "skillPoints": b[0x20], "experience": r24(b, 0x21),
        "level": b[0x24], "armorSlot": b[0x25], "lastCon": r16(b, 0x26),
        "afflictions": b[0x28], "npc": b[0x29], "itemRefuse": b[0x2B],
        "skillRefuse": b[0x2C], "attribRefuse": b[0x2D], "tradeRefuse": b[0x2E],
        "joinString": b[0x30], "willingness": b[0x31],
        "rank": s(cstr(b[0x32:0x4B], 25)), "gameWon": b[0x4B],
        "specialPromotion": b[0x4C],
    })
    c["skills"] = [[b[0x80 + 2 * i], b[0x81 + 2 * i]] for i in range(30) if b[0x80 + 2 * i]]
    c["items"] = [[b[0xBD + 2 * i], b[0xBE + 2 * i]] for i in range(30) if b[0xBD + 2 * i]]
    return c


SAVEGAME_RESERVED = 0x1206
SAVEGAME_PAYLOAD = 0x800


def savegame_encode(sg: dict, disk: int) -> bytes:
    p = bytearray(SAVEGAME_PAYLOAD)
    for g, grp in enumerate(sg["groups"]):
        o = g * 14
        p[o + 1:o + 8] = bytes(grp["order"])
        p[o + 8] = grp["x"]
        p[o + 9] = grp["y"]
        p[o + 10] = grp["map"]
        p[o + 11] = grp["prevX"]
        p[o + 12] = grp["prevY"]
        p[o + 13] = grp["prevMap"]
    p[0x78] = sg["viewportX"]
    p[0x79] = sg["viewportY"]
    p[0x7D] = sg["currentMembers"]
    p[0x7E] = sg["currentParty"]
    p[0x7F] = sg["currentMap"]
    p[0x80] = sg["totalMembers"]
    p[0x81] = sg["extraGroups"]
    p[0x83] = sg["minute"]
    p[0x84] = sg["hour"]
    p[0x85] = sg["combatScrollSpeed"]
    p[0xF5:0xF9] = u32(sg["serial"])
    for i, ch in enumerate(sg["characters"]):
        p[0x100 + i * 0x100:0x200 + i * 0x100] = char_encode(ch)
    block = b"msq" + bytes((0x30 + disk,)) + C.rxor_encode(bytes(p))
    assert len(block) == 0x806
    return block + bytes(SAVEGAME_RESERVED - 0x806)


def savegame_decode(game: bytes, off: int) -> dict:
    if game[off:off + 3] != b"msq" or game[off + 3] not in (0x30, 0x31):
        raise ValueError("savegame: bad header")
    p = C.rxor_decode_whole(game, SAVEGAME_PAYLOAD, off + 4)
    groups = []
    for g in range(4):
        o = g * 14
        groups.append({"order": list(p[o + 1:o + 8]), "x": p[o + 8], "y": p[o + 9],
                       "map": p[o + 10], "prevX": p[o + 11], "prevY": p[o + 12],
                       "prevMap": p[o + 13]})
    sg = {"groups": groups, "viewportX": p[0x78], "viewportY": p[0x79],
          "currentMembers": p[0x7D], "currentParty": p[0x7E], "currentMap": p[0x7F],
          "totalMembers": p[0x80], "extraGroups": p[0x81], "minute": p[0x83],
          "hour": p[0x84], "combatScrollSpeed": p[0x85], "serial": r32(p, 0xF5)}
    sg["characters"] = [char_decode(p[0x100 + i * 0x100:0x200 + i * 0x100]) for i in range(7)]
    sg["tailAllZero"] = not any(game[off + 0x806:off + SAVEGAME_RESERVED])
    return sg


SHOP_HEADER = bytes.fromhex("606060003708F839")
SHOP_BLOCK = 766


def shop_encode(items: list[dict], disk: int) -> bytes:
    p = bytearray(SHOP_HEADER)
    for i in range(94):
        it = items[i] if i < len(items) else None
        if it is None:
            p += bytes(8)
        else:
            p += (u16(it["price"]) + bytes((it["stock"], (it["type"] << 3) | it["lowFlags"],
                                            it["capacity"], it["skill"], it["damage"], it["ammo"])))
    blk = b"msq" + bytes((0x30 + disk,)) + C.rxor_encode(bytes(p))
    assert len(blk) == SHOP_BLOCK
    return blk


def shop_decode(game: bytes, off: int) -> dict:
    p = C.rxor_decode_whole(game, 760, off + 4)
    items = []
    for i in range(94):
        r = p[8 + 8 * i:16 + 8 * i]
        items.append({"price": r16(r, 0), "stock": r[2], "type": r[3] >> 3, "lowFlags": r[3] & 7,
                      "capacity": r[4], "skill": r[5], "damage": r[6], "ammo": r[7]})
    return {"header": p[:8].hex(), "items": items}


# ---------------------------------------------------------------------------
# Map block (map.md + SPEC-03 lab rules)
# ---------------------------------------------------------------------------

# Section order inside the map-data body after map info (SPEC-03 section 6.1):
# action tables 0..7, table 15, NPC section, tables 8..14, specials,
# monster names, monster data, strings.
TABLE_ORDER_A = [0, 1, 2, 3, 4, 5, 6, 7, 15]
TABLE_ORDER_B = [8, 9, 10, 11, 12, 13, 14]

NO_CHANGE = 255


def tail(nc: int, na: int) -> bytes:
    return bytes((nc,)) if nc >= 253 else bytes((nc, na))


def rec_encode(cls: int, r: dict) -> bytes:
    nc, na = r.get("newClass", NO_CHANGE), r.get("newAction", 0)
    if cls == 1:  # PRINT
        msgs = r["messages"]
        b = bytes(m | (0x80 if i == len(msgs) - 1 else 0) for i, m in enumerate(msgs))
        return b + tail(nc, na)
    if cls == 3:  # FIXED ENCOUNTER
        b = bytes((r["visibleDistance"], r["hitDistance"], r["message"]))
        for mob, rnd, grp in r["groups"]:
            b += bytes((mob, (0x80 if rnd else 0) | grp))
        flags = (r["properName"] | (r["friendly"] << 1) | (r["immobile"] << 2) | (r["npc"] << 4))
        return b + bytes((flags,)) + tail(nc, na)
    if cls == 4:  # MASK (lab door)
        return bytes((r["message"], (0x80 if r["impassable"] else 0) | r["tile"])) + tail(nc, na)
    if cls == 5:  # LOOT (wllib layout: class and action always present)
        b = bytes((nc if nc != NO_CHANGE else 0, na))
        for iid, fixed_, amt in r["items"]:
            b += bytes(((0x80 if fixed_ else 0) | iid, amt))
        if r.get("cash") is not None:
            fixed_, amt = r["cash"]
            b += bytes((0xDE if fixed_ else 0x5E,)) + u16(amt)
        return b + b"\xFF"
    if cls == 6:  # SHOP (lab)
        return bytes((r["shop"], r["message"])) + tail(nc, na)
    if cls == 10:  # TRANSITION
        flags = (0x80 if r["relative"] else 0) | (0x40 if r["confirm"] else 0) | r["message"]
        return bytes((flags, r["x"] & 0xFF, r["y"] & 0xFF, r["location"])) + tail(nc, na)
    if cls == 11:  # BLOCKED
        return bytes((r["message"],)) + tail(nc, na)
    raise ValueError("lab rules v1 define no record for class %d" % cls)


def _tail_read(b: bytes, o: int, r: dict) -> int:
    nc = b[o]
    o += 1
    if nc < 253:
        r["newClass"], r["newAction"] = nc, b[o]
        o += 1
    else:
        r["newClass"], r["newAction"] = nc, 0
    return o


def i8(v: int) -> int:
    return v - 256 if v >= 128 else v


def rec_decode(cls: int, b: bytes, o: int) -> dict:
    r: dict = {}
    if cls == 1:
        msgs = []
        while True:
            m = b[o]
            o += 1
            msgs.append(m & 0x7F)
            if m & 0x80:
                break
        r["messages"] = msgs
        _tail_read(b, o, r)
    elif cls == 3:
        r["visibleDistance"], r["hitDistance"], r["message"] = b[o], b[o + 1], b[o + 2]
        o += 3
        r["groups"] = []
        for _ in range(3):
            r["groups"].append([b[o], bool(b[o + 1] & 0x80), b[o + 1] & 0x7F])
            o += 2
        f = b[o]
        o += 1
        r.update({"properName": f & 1, "friendly": (f >> 1) & 1, "immobile": (f >> 2) & 1, "npc": f >> 4})
        _tail_read(b, o, r)
    elif cls == 4:
        r["message"], r["impassable"], r["tile"] = b[o], bool(b[o + 1] & 0x80), b[o + 1] & 0x7F
        _tail_read(b, o + 2, r)
    elif cls == 5:
        r["newClass"], r["newAction"] = b[o], b[o + 1]
        o += 2
        r["items"], r["cash"] = [], None
        while b[o] != 0xFF:
            if b[o] in (0xDE, 0x5E):
                r["cash"] = [b[o] == 0xDE, r16(b, o + 1)]
                o += 3
            else:
                r["items"].append([b[o] & 0x7F, bool(b[o] & 0x80), b[o + 1]])
                o += 2
    elif cls == 6:
        r["shop"], r["message"] = b[o], b[o + 1]
        _tail_read(b, o + 2, r)
    elif cls == 10:
        f = b[o]
        r.update({"relative": bool(f & 0x80), "confirm": bool(f & 0x40), "message": f & 0x3F,
                  "x": i8(b[o + 1]), "y": i8(b[o + 2]), "location": b[o + 3]})
        _tail_read(b, o + 4, r)
    elif cls == 11:
        r["message"] = b[o]
        _tail_read(b, o + 1, r)
    else:
        raise ValueError("class %d has no lab record" % cls)
    return r


def _norm(cls: int, r: dict) -> dict:
    """Canonical form of a record as rec_decode returns it (for the manifest)."""
    return rec_decode(cls, rec_encode(cls, r), 0)


def mob_encode(m: dict) -> bytes:
    return (u16(m["sturdiness"]) + bytes((m["combatRating"], m["randomDamage"],
            (m["maxGroup"] << 4) | m["armorClass"], (m["fixedDamage"] << 4) | m["weaponType"],
            m["type"], m["portrait"])))


def mob_decode(b: bytes, name: bytes) -> dict:
    return {"name": s(name), "sturdiness": r16(b, 0), "combatRating": b[2], "randomDamage": b[3],
            "maxGroup": b[4] >> 4, "armorClass": b[4] & 15, "fixedDamage": b[5] >> 4,
            "weaponType": b[5] & 15, "type": b[6], "portrait": b[7]}


MAPINFO_FIELDS = ("encounterFrequency", "tileset", "randomMonsterTypes",
                  "maxRandomEncounters", "borderImage")


def mapinfo_encode(size: int, mi: dict) -> bytes:
    b = bytearray(50)
    b[2] = size
    for i, k in enumerate(MAPINFO_FIELDS):
        b[5 + i] = mi[k]
    b[0x0A:0x0C] = u16(mi["timePerStep"])
    b[0x0C] = mi["healRate"]
    return bytes(b)  # bytes 0, 1, 3, 4 and the 37 combat string bytes are 0 (lab)


def mapinfo_decode(b: bytes) -> dict:
    d = {"unknown00": b[0], "unknown01": b[1], "mapSize": b[2], "unknown03": b[3], "unknown04": b[4]}
    for i, k in enumerate(MAPINFO_FIELDS):
        d[k] = b[5 + i]
    d["timePerStep"] = r16(b, 0x0A)
    d["healRate"] = b[0x0C]
    d["combatStringIds"] = list(b[0x0D:0x32])
    return d


def build_map(m: dict, disk: int) -> tuple[bytes, int, dict]:
    """Return (block bytes, tileMapOffset, facts)."""
    S = m["size"]
    cls, act, img = m["class"], m["action"], m["image"]
    body = bytearray()
    for y in range(S):
        for x in range(0, S, 2):
            body.append((cls[y][x] << 4) | cls[y][x + 1])  # high nibble = even x
    for y in range(S):
        body += bytes(act[y])
    cd_at = len(body)
    body += bytes(42)
    body += mapinfo_encode(S, m["info"])
    assert len(body) == (0x062A if S == 32 else 0x182A) + 50

    offsets = [0] * 16

    def emit_table(c: int) -> None:
        recs = m["actions"].get(c)
        if not recs:
            return
        start = len(body)
        offsets[c] = start
        encs = [None] + [rec_encode(c, r) for r in recs]  # slot 0 is null
        ptr_area = 2 * len(encs)
        pos = start + ptr_area
        ptrs = []
        for e in encs:
            if e is None:
                ptrs.append(0)
            else:
                ptrs.append(pos)
                pos += len(e)
        for p in ptrs:
            body.extend(u16(p))
        for e in encs:
            if e is not None:
                body.extend(e)

    for c in TABLE_ORDER_A:
        emit_table(c)
    npc_off = None
    if m["npcs"]:
        npc_off = len(body)
        n = len(m["npcs"])
        body.extend(u16(0))
        first = npc_off + 2 + 2 * n
        for i in range(n):
            body.extend(u16(first + i * 0x100))
        for ch in m["npcs"]:
            body.extend(char_encode(ch))
    for c in TABLE_ORDER_B:
        emit_table(c)
    specials_off = 0  # lab rule: no special-action table
    names_off = len(body)
    for mob in m["mobs"]:
        body.extend(mob["name"] + b"\x00")
    data_off = len(body)
    for mob in m["mobs"]:
        body.extend(mob_encode(mob))
    strings_off = len(body)
    if npc_off is None:
        npc_off = strings_off  # lab rule: no NPCs -> npcOffset = stringsOffset
    body.extend(C.strtab_encode(m["dictionary"], m["strings"]))

    cd = u16(strings_off) + u16(names_off) + u16(data_off)
    for o in offsets:
        cd += u16(o)
    cd += u16(specials_off) + u16(npc_off)
    body[cd_at:cd_at + 42] = cd

    prefix = bytes(body[:strings_off])
    if not C.rxor_prefix_is_unambiguous(prefix):
        raise ValueError("ambiguous encrypted prefix")
    enc = C.rxor_encode(prefix)
    data_section = enc + bytes(body[strings_off:]) + b"\x00"  # final byte: unknown, lab 0
    tile_map = bytes(v for row in img for v in row)
    tsec = u32(S * S) + u32(0) + C.huff_encode(tile_map)
    header = b"msq" + bytes((0x30 + disk,))
    block = header + data_section + tsec
    tmo = len(header) + len(data_section)
    facts = {"bodySize": len(body), "encryptedPrefixLength": strings_off,
             "centralDirectory": {"stringsOffset": strings_off, "mobNamesOffset": names_off,
                                  "mobDataOffset": data_off, "actionClassOffsets": offsets,
                                  "specialsOffset": specials_off, "npcOffset": npc_off}}
    return block, tmo, facts


def map_decode(game: bytes, off: int, size: int, tmo: int) -> dict:
    """Reference reader following SPEC-03 sections 3 to 9."""
    if game[off:off + 3] != b"msq":
        raise ValueError("map: bad header")
    body_size = tmo - 7
    body, plen = C.rxor_decode_prefix(game, body_size, off + 4)
    _, plen2 = C.rxor_decode_prefix(game, body_size, off + 4, wllib_guard=True)
    t = off + tmo
    tsize = r32(game, t)
    if tsize != size * size:
        raise ValueError("map: tile-map size %d != %d" % (tsize, size * size))
    tiles, end = C.huff_decode(game, tsize, t + 8)
    n = size * size
    cm, am = body[:n // 2], body[n // 2:n // 2 + n]
    cdo = n // 2 + n
    cd = body[cdo:cdo + 42]
    sd = {"stringsOffset": r16(cd, 0), "mobNamesOffset": r16(cd, 2), "mobDataOffset": r16(cd, 4),
          "actionClassOffsets": [r16(cd, 6 + 2 * i) for i in range(16)],
          "specialsOffset": r16(cd, 0x26), "npcOffset": r16(cd, 0x28)}
    info = mapinfo_decode(body[cdo + 42:cdo + 92])
    cls = [[(cm[(y * size + x) >> 1] >> 4) if x % 2 == 0 else (cm[(y * size + x) >> 1] & 15)
            for x in range(size)] for y in range(size)]
    act = [list(am[y * size:(y + 1) * size]) for y in range(size)]
    img = [list(tiles[y * size:(y + 1) * size]) for y in range(size)]
    # action tables
    actions = {}
    for c in range(16):
        o = sd["actionClassOffsets"][c]
        if o == 0:
            continue
        ptrs, pos, end_ptr = [], o, None
        while end_ptr is None or pos < end_ptr:
            p = r16(body, pos)
            ptrs.append(p)
            pos += 2
            if p and (end_ptr is None or p < end_ptr):
                end_ptr = p
        actions[str(c)] = [None if p == 0 else rec_decode(c, body, p) for p in ptrs]
    # NPCs
    npcs = []
    o = sd["npcOffset"]
    if r16(body, o) == 0:
        pos, lo, ptrs = o + 2, None, []
        while lo is None or pos < lo:
            p = r16(body, pos)
            ptrs.append(p)
            pos += 2
            lo = p if lo is None or p < lo else lo
        npcs = [char_decode(body[p:p + 0x100]) for p in ptrs]
    nm = (sd["stringsOffset"] - sd["mobDataOffset"]) // 8
    names, p = [], sd["mobNamesOffset"]
    for _ in range(nm):
        e = body.index(b"\x00", p)
        names.append(body[p:e])
        p = e + 1
    mobs = [mob_decode(body[sd["mobDataOffset"] + 8 * i:sd["mobDataOffset"] + 8 * i + 8], names[i])
            for i in range(nm)]
    strings = C.strtab_decode(body, sd["stringsOffset"])
    return {"size": size, "bodySize": body_size, "encryptedPrefixLength": plen,
            "wllibPrefixLength": plen2, "blockEnd": end - off, "centralDirectory": sd,
            "info": info, "cells": {"actionClass": cls, "action": act, "image": img},
            "actions": actions, "npcs": npcs, "mobs": mobs, "strings": [s(x) for x in strings]}


# ---------------------------------------------------------------------------
# Graphics containers
# ---------------------------------------------------------------------------

def planes_encode(pix: list[list[int]], bytes_per_row: int) -> bytes:
    """Four 1-bit planes (blue, green, red, intensity), MSB = leftmost pixel."""
    out = bytearray()
    for bit in range(4):
        for row in pix:
            for bx in range(bytes_per_row):
                v = 0
                for i in range(8):
                    v |= ((row[bx * 8 + i] >> bit) & 1) << (7 - i)
                out.append(v)
    return bytes(out)


def planes_decode(b: bytes, w: int, h: int) -> list[list[int]]:
    bpr = w // 8
    plane = bpr * h
    return [[sum(((b[bit * plane + y * bpr + x // 8] >> (7 - x % 8)) & 1) << bit for bit in range(4))
             for x in range(w)] for y in range(h)]


def mask_encode(mask: list[list[int]]) -> bytes:
    out = bytearray()
    for row in mask:
        for bx in range(2):
            v = 0
            for i in range(8):
                v |= (row[bx * 8 + i] & 1) << (7 - i)
            out.append(v)
    return bytes(out)


def cursor_encode(pix: list[list[int]], vis: list[list[int]]) -> bytes:
    out = bytearray()
    for bit in range(4):
        for y in range(16):
            def byte(src, x0, fn):
                v = 0
                for i in range(8):
                    v |= (fn(src[y][x0 + i]) & 1) << (7 - i)
                return v
            out += bytes((byte(vis, 8, int), byte(vis, 0, int),
                          byte(pix, 8, lambda p: p >> bit), byte(pix, 0, lambda p: p >> bit)))
    return bytes(out)


def cursor_decode(b: bytes) -> tuple[list[list[int]], list[list[int]]]:
    pix, vis = [], []
    for y in range(16):
        prow, vrow = [], []
        for x in range(16):
            half, bi = x // 8, 7 - x % 8
            vrow.append((b[y * 4 + (1 - half)] >> bi) & 1)
            prow.append(sum(((b[bit * 64 + y * 4 + (3 - half)] >> bi) & 1) << bit for bit in range(4)))
        pix.append(prow)
        vis.append(vrow)
    return pix, vis


def portrait_anim_encode(scripts: list[list[tuple[int, int]]], updates: list[list[tuple[int, bytes]]]) -> bytes:
    sb = bytearray()
    for sc in scripts:
        for d, u in sc:
            sb += bytes((d, u))
        sb.append(0xFF)
    ub = bytearray()
    for upd in updates:
        for off, data in upd:
            assert 1 <= len(data) <= 16 and off < 0x1000
            ub += u16(((len(data) - 1) << 12) | off) + data
        ub += u16(0xFFFF)
    return u16(len(sb)) + bytes(sb) + u16(len(ub)) + bytes(ub)


def portrait_anim_decode(b: bytes) -> tuple[list, list]:
    ss = r16(b, 0)
    sec = b[2:2 + ss]
    scripts, cur, i = [], [], 0
    while i < len(sec):
        if sec[i] == 0xFF:
            scripts.append(cur)
            cur = []
            i += 1
        else:
            cur.append([sec[i], sec[i + 1]])
            i += 2
    us = r16(b, 2 + ss)
    ub = b[4 + ss:4 + ss + us]
    updates, cur, i = [], [], 0
    while i < len(ub):
        h = r16(ub, i)
        i += 2
        if h == 0xFFFF:
            updates.append(cur)
            cur = []
            continue
        n, off = (h >> 12) + 1, h & 0x0FFF
        cur.append([off, ub[i:i + n].hex()])
        i += n
    if 4 + ss + us != len(b):
        raise ValueError("portrait animation: size fields do not add up")
    return scripts, updates


def apply_updates(base: bytes, upd: list) -> bytes:
    img = bytearray(base)
    for off, hx in upd:
        for k, v in enumerate(bytes.fromhex(hx)):
            img[off + k] ^= v
    return bytes(img)


def ending_anim_encode(updates: list[tuple[int, list[tuple[int, bytes]]]]) -> bytes:
    st = bytearray()
    for delay, patches in updates:
        st += u16(delay)
        for off, data in patches:
            assert len(data) == 4
            st += u16(off) + data
        st += u16(0xFFFF)
    st += u16(0xFFFF)
    return u16(len(st)) + bytes(st) + u16(0)


def ending_anim_decode(b: bytes) -> list:
    n = r16(b, 0)
    if n != len(b) - 4 or r16(b, len(b) - 2) != 0:
        raise ValueError("END.CPA: bad animation framing")
    i, ups = 2, []
    while True:
        d = r16(b, i)
        i += 2
        if d == 0xFFFF:
            break
        patches = []
        while True:
            o = r16(b, i)
            i += 2
            if o == 0xFFFF:
                break
            patches.append([o, b[i:i + 4].hex()])
            i += 4
        ups.append([d, patches])
    return ups


def ending_apply(img: bytes, patches: list) -> bytes:
    out = bytearray(img)
    for off, hx in patches:
        cell_x, y = off % 40, off // 40
        bo = y * 144 + cell_x * 4
        out[bo:bo + 4] = bytes.fromhex(hx)
    return bytes(out)


# ---------------------------------------------------------------------------
# Lab string-table file LABSTR.BIN (SPEC-02 section 12.3)
# ---------------------------------------------------------------------------

LABSTR_MAGIC = b"WLLABST1"


def labstr_encode(tables: list[bytes]) -> bytes:
    n = len(tables)
    head = LABSTR_MAGIC + u16(n) + u16(0)
    pos = len(head) + 8 * n
    offs, sizes = b"", b""
    for t in tables:
        offs += u32(pos)
        sizes += u32(len(t))
        pos += len(t)
    return head + offs + sizes + b"".join(tables)


def labstr_decode(b: bytes) -> list[list[bytes]]:
    if b[:8] != LABSTR_MAGIC:
        raise ValueError("LABSTR: bad magic")
    n = r16(b, 8)
    out = []
    for i in range(n):
        o, z = r32(b, 12 + 4 * i), r32(b, 12 + 4 * n + 4 * i)
        out.append(C.strtab_decode(b[:o + z], o))
    return out


# ---------------------------------------------------------------------------
# Content generation (original lab content, seeded)
# ---------------------------------------------------------------------------

DICT = (b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r"
        b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;")
assert len(DICT) == 60 and DICT[:2] == b"\x20\x65"


def make_character(rng: random.Random, name: bytes, npc: int = 0) -> dict:
    return {
        "name": name, "strength": rng.randrange(3, 19), "intelligence": rng.randrange(3, 19),
        "luck": rng.randrange(3, 19), "speed": rng.randrange(3, 19), "agility": rng.randrange(3, 19),
        "dexterity": rng.randrange(3, 19), "charisma": rng.randrange(3, 19),
        "money": rng.randrange(0, 5000), "gender": rng.randrange(2), "nationality": rng.randrange(5),
        "armorClass": rng.randrange(0, 5), "maxCon": rng.randrange(20, 60), "curCon": 0,
        "weaponSlot": 1, "skillPoints": rng.randrange(0, 10), "experience": rng.randrange(0, 2000),
        "level": rng.randrange(1, 4), "armorSlot": 2, "lastCon": 0, "afflictions": 0, "npc": npc,
        "itemRefuse": 0, "skillRefuse": 0, "attribRefuse": 0, "tradeRefuse": 0,
        "joinString": 1 if npc else 0, "willingness": 50 if npc else 0,
        "rank": b"Lab Recruit", "gameWon": 0, "specialPromotion": 0,
        "skills": [[rng.randrange(1, 36), rng.randrange(1, 4)] for _ in range(rng.randrange(2, 6))],
        "items": [[rng.randrange(1, 90), rng.randrange(0, 0x80)] for _ in range(rng.randrange(2, 6))]
        + [[0x2A, 0x83]],  # one jammed weapon: bit 7 set, severity 3
    }


def blank_map(rng: random.Random, S: int, location: int) -> dict:
    cls = [[0] * S for _ in range(S)]
    act = [[0] * S for _ in range(S)]
    img = [[10 + 1 + rng.randrange(8) for _ in range(S)] for _ in range(S)]
    for i in range(S):
        for (x, y) in ((i, 0), (i, S - 1), (0, i), (S - 1, i)):
            cls[y][x] = 11  # blocked border, action 0 = no record
            img[y][x] = 10  # tile 0: wall
    for _ in range(S):  # scatter some sprite images (indices 0..9)
        x, y = rng.randrange(1, S - 1), rng.randrange(1, S - 1)
        img[y][x] = rng.randrange(10)
    return {"size": S, "location": location, "class": cls, "action": act, "image": img,
            "actions": {}, "npcs": [], "mobs": [], "dictionary": DICT}


def put(m: dict, x: int, y: int, c: int, rec: dict | None, image: int | None = None) -> None:
    """Place a cell; the record (if any) is appended to the class table and the
    action byte becomes its 1-based slot (slot 0 is the null pointer)."""
    m["class"][y][x] = c
    if rec is None:
        m["action"][y][x] = 0
    else:
        recs = m["actions"].setdefault(c, [])
        recs.append(rec)
        m["action"][y][x] = len(recs)
    if image is not None:
        m["image"][y][x] = image


def make_maps(rng: random.Random) -> list[dict]:
    maps = []
    # Map 0: 32x32 town, location 0
    m = blank_map(rng, 32, 0)
    m["strings"] = [b"", b"Enter the pump house?", b"Ma Rusty's Trading Post.",
                    b"The door is locked.", b"A note is nailed to the post.",
                    b"Read paragraph 3.", b"Rubble blocks the way.", b"Welcome, \x0b."]
    m["info"] = {"encounterFrequency": 0, "tileset": 0, "randomMonsterTypes": 0,
                 "maxRandomEncounters": 0, "borderImage": 10, "timePerStep": 0x0100, "healRate": 4}
    put(m, 5, 5, 4, {"message": 0, "impassable": False, "tile": 10 + 12,
                     "newClass": 0, "newAction": 0}, 10 + 11)
    put(m, 6, 5, 4, {"message": 3, "impassable": True, "tile": 10 + 12}, 10 + 11)
    put(m, 10, 10, 10, {"relative": False, "confirm": True, "message": 1, "x": 10, "y": 20,
                        "location": 1}, 10 + 20)
    put(m, 12, 10, 6, {"shop": 0, "message": 2}, 10 + 21)
    put(m, 14, 10, 5, {"newClass": 0, "newAction": 0, "items": [[0x2A, True, 12], [0x11, False, 1]],
                       "cash": [True, 250]}, 10 + 22)
    put(m, 16, 10, 1, {"messages": [4, 5]}, 10 + 23)
    put(m, 18, 10, 3, {"visibleDistance": 4, "hitDistance": 1, "message": 0,
                       "groups": [[1, False, 3], [2, True, 2], [0, False, 0]],
                       "properName": 0, "friendly": 0, "immobile": 0, "npc": 0,
                       "newClass": 0, "newAction": 0})
    put(m, 20, 10, 11, {"message": 6})
    m["npcs"] = [make_character(rng, b"Hobo Joe", npc=1)]
    m["mobs"] = [
        {"name": b"rad rat\x0a\x0as\x0a", "sturdiness": 12, "combatRating": 3, "randomDamage": 1,
         "maxGroup": 6, "armorClass": 0, "fixedDamage": 0, "weaponType": 1, "type": 1, "portrait": 1},
        {"name": b"leather jerk\x0a\x0as\x0a", "sturdiness": 30, "combatRating": 5, "randomDamage": 2,
         "maxGroup": 4, "armorClass": 1, "fixedDamage": 1, "weaponType": 2, "type": 3, "portrait": 2},
    ]
    maps.append(m)

    # Map 1: 32x32 interior, location 1
    m = blank_map(rng, 32, 1)
    m["strings"] = [b"", b"Back outside.", b"A hatch leads down.", b"You vault the gap."]
    m["info"] = {"encounterFrequency": 0, "tileset": 0, "randomMonsterTypes": 0,
                 "maxRandomEncounters": 0, "borderImage": 10, "timePerStep": 0x0030, "healRate": 2}
    put(m, 10, 21, 10, {"relative": False, "confirm": False, "message": 1, "x": 11, "y": 10,
                        "location": 0}, 10 + 20)
    put(m, 20, 20, 10, {"relative": False, "confirm": True, "message": 2, "x": 32, "y": 32,
                        "location": 130}, 10 + 24)  # shared location 130 -> location 2
    put(m, 5, 8, 10, {"relative": True, "confirm": False, "message": 3, "x": 2, "y": 0,
                      "location": 1})
    m["mobs"] = [{"name": b"mutant bat\x0a\x0as\x0a", "sturdiness": 9, "combatRating": 4,
                  "randomDamage": 1, "maxGroup": 8, "armorClass": 0, "fixedDamage": 0,
                  "weaponType": 1, "type": 2, "portrait": 3}]
    maps.append(m)

    # Map 2: 64x64 wasteland, location 2
    m = blank_map(rng, 64, 2)
    m["strings"] = [b"", b"The way you came.", b"Scorpitron!", b"Supplies cache."]
    m["info"] = {"encounterFrequency": 0, "tileset": 0, "randomMonsterTypes": 0,
                 "maxRandomEncounters": 0, "borderImage": 10, "timePerStep": 0x0200, "healRate": 1}
    put(m, 32, 33, 10, {"relative": False, "confirm": False, "message": 1, "x": 0, "y": 0,
                        "location": 255}, 10 + 20)  # 255 = previous location
    put(m, 40, 40, 3, {"visibleDistance": 6, "hitDistance": 2, "message": 2,
                       "groups": [[3, False, 1], [0, False, 0], [0, False, 0]],
                       "properName": 1, "friendly": 0, "immobile": 1, "npc": 0,
                       "newClass": 0, "newAction": 0})
    put(m, 50, 12, 3, {"visibleDistance": 3, "hitDistance": 1, "message": 0,
                       "groups": [[1, True, 4], [2, True, 4], [0, False, 0]],
                       "properName": 0, "friendly": 1, "immobile": 0, "npc": 0})
    put(m, 20, 50, 5, {"newClass": 0, "newAction": 0, "items": [[0x05, False, 2]],
                       "cash": [False, 100]}, 10 + 22)
    m["mobs"] = [
        {"name": b"wasteland dog\x0a\x0as\x0a", "sturdiness": 15, "combatRating": 4, "randomDamage": 1,
         "maxGroup": 5, "armorClass": 0, "fixedDamage": 0, "weaponType": 1, "type": 1, "portrait": 1},
        {"name": b"raider\x0a\x0as\x0a", "sturdiness": 40, "combatRating": 6, "randomDamage": 2,
         "maxGroup": 6, "armorClass": 2, "fixedDamage": 2, "weaponType": 3, "type": 3, "portrait": 2},
        {"name": b"Scorpitron", "sturdiness": 900, "combatRating": 12, "randomDamage": 8,
         "maxGroup": 1, "armorClass": 9, "fixedDamage": 6, "weaponType": 5, "type": 5, "portrait": 3},
    ]
    maps.append(m)
    return maps


def make_tile(rng: random.Random, t: int) -> list[list[int]]:
    base = t % 16
    return [[(base + ((x ^ y) >> (t % 3)) + (1 if rng.random() < 0.1 else 0)) % 16
             for x in range(16)] for y in range(16)]


def make_portrait(rng: random.Random, p: int) -> list[list[int]]:
    return [[((x // (6 + p)) + (y // (5 + p)) + p) % 16 if rng.random() > 0.02 else rng.randrange(16)
             for x in range(96)] for y in range(84)]


def generate(outdir: str, seed: int = DEFAULT_SEED) -> dict:
    rng = random.Random(seed)
    os.makedirs(outdir, exist_ok=True)
    files: dict[str, bytes] = {}
    manifest: dict = {"formatVersion": 1, "generator": "fixtures_gen.py", "seed": seed}

    # ---- GAME1: three maps, savegame, one shop list
    maps = make_maps(rng)
    game = bytearray()
    map_facts = []
    for i, m in enumerate(maps):
        for attempt in range(64):
            try:
                block, tmo, facts = build_map(m, 0)
                break
            except ValueError:
                m["mobs"][-1]["sturdiness"] += 1  # deterministic nudge until the prefix is unambiguous
        else:
            raise RuntimeError("could not build map %d" % i)
        if b"msq" in block[4:]:
            raise RuntimeError("map %d block contains 'msq' after its header" % i)
        map_facts.append((len(game), tmo, facts))
        game += block
    sg_off = len(game)
    party = [make_character(rng, n) for n in (b"Hell Razor", b"Angela Dth", b"Thrasher", b"Snake Vargas")]
    empty = {k: (b"" if k in ("name", "rank") else ([] if k in ("skills", "items") else 0))
             for k in party[0]}
    savegame = {
        "groups": [{"order": [1, 2, 3, 4, 0, 0, 0], "x": 11, "y": 12, "map": 0,
                    "prevX": 3, "prevY": 4, "prevMap": 0}]
        + [{"order": [0] * 7, "x": 0, "y": 0, "map": 0, "prevX": 0, "prevY": 0, "prevMap": 0}] * 3,
        "viewportX": 7, "viewportY": 8, "currentMembers": 4, "currentParty": 0, "currentMap": 0,
        "totalMembers": 4, "extraGroups": 0, "minute": 30, "hour": 9, "combatScrollSpeed": 3,
        "serial": 0x00010203, "characters": party + [empty] * 3,
    }
    game += savegame_encode(savegame, 0)
    shop_off = len(game)
    shop_items = [{"price": rng.randrange(1, 3000), "stock": rng.randrange(0, 20),
                   "type": rng.randrange(0, 32), "lowFlags": rng.randrange(2),
                   "capacity": rng.randrange(0, 40), "skill": rng.randrange(0, 36),
                   "damage": rng.randrange(0, 20), "ammo": rng.randrange(0, 90)} for _ in range(12)]
    game += shop_encode(shop_items, 0)
    files["GAME1"] = bytes(game)

    # ---- ALLHTDS1: one tileset of 32 tiles
    tiles = [make_tile(rng, t) for t in range(32)]
    raw_tiles = b"".join(C.vxor_encode(pack4(t), 8) for t in tiles)
    allhtds = C.msqh_encode(raw_tiles, 0)
    files["ALLHTDS1"] = allhtds

    # ---- ALLPICS1: four portraits, each with a two-frame animation
    allpics = bytearray()
    portrait_offsets = []
    portraits_truth = []
    for p in range(4):
        pix = make_portrait(rng, p)
        base = pack4(pix)
        upd = [(48 * 30 + 20 + p, bytes(rng.randrange(1, 256) for _ in range(8))),
               (48 * 31 + 20 + p, bytes(rng.randrange(1, 256) for _ in range(16)))]
        anim = portrait_anim_encode([[(4, 0), (4, 0)]], [upd])
        portrait_offsets.append(len(allpics))
        allpics += C.msqh_encode(C.vxor_encode(base, 48), 0) + C.msqh_encode(anim, 0)
        frame1 = apply_updates(base, [[o, d.hex()] for o, d in upd])
        portraits_truth.append({"rawId": p, "compactIndex": p, "offset": portrait_offsets[-1],
                                "base": base.hex(), "baseSha256": sha(base),
                                "scripts": [[[4, 0], [4, 0]]],
                                "updates": [[[o, d.hex()] for o, d in upd]],
                                "frames": [{"sha256": sha(base)}, {"sha256": sha(frame1), "hex": frame1.hex()}],
                                "animDecodedSize": len(anim)})
    files["ALLPICS1"] = bytes(allpics)

    # ---- sprites, masks, font, cursors, title, ending
    sprites, masks, sprite_truth = bytearray(), bytearray(), []
    for n in range(10):
        pix = [[(n + x // 4 + y // 4) % 16 for x in range(16)] for y in range(16)]
        msk = [[1 if (x - 7.5) ** 2 + (y - 7.5) ** 2 > 56 else 0 for x in range(16)] for y in range(16)]
        sprites += planes_encode(pix, 2)
        masks += mask_encode(msk)
        sprite_truth.append({"pixels": pix, "transparent": msk})
    files["IC0_9.WLF"], files["MASKS.WLF"] = bytes(sprites), bytes(masks)
    font, font_truth = bytearray(), []
    for g in range(32):
        pix = [[((g >> (x % 5)) & 1) * ((g + y) % 15 + 1) for x in range(8)] for y in range(8)]
        font += planes_encode(pix, 1)
        font_truth.append(pix)
    files["COLORF.FNT"] = bytes(font)
    curs, curs_truth = bytearray(), []
    for k in range(2):
        pix = [[(x + y + k) % 16 for x in range(16)] for y in range(16)]
        vis = [[1 if x <= y + k * 3 else 0 for x in range(16)] for y in range(16)]
        curs += cursor_encode(pix, vis)
        curs_truth.append({"pixels": pix, "visible": vis})
    files["CURS"] = bytes(curs)
    title = pack4([[((x // 18) ^ (y // 16)) % 16 for x in range(288)] for y in range(128)])
    files["TITLE.PIC"] = C.vxor_encode(title, 144)
    end_base = pack4([[((x + y) // 24) % 16 for x in range(288)] for y in range(128)])
    end_updates = [(5, [(41, bytes.fromhex("11223344")), (40 * 100 + 35, bytes.fromhex("FFEEDDCC"))]),
                   (9, [(0, bytes.fromhex("0F0F0F0F"))])]
    end_anim = ending_anim_encode(end_updates)
    files["END.CPA"] = C.msqh_encode(C.vxor_encode(end_base, 144), 0) + C.msqh_encode(end_anim, 0, b"\x08\x67\x01")
    f1 = ending_apply(end_base, [[o, d.hex()] for o, d in end_updates[0][1]])
    f2 = ending_apply(f1, [[o, d.hex()] for o, d in end_updates[1][1]])

    # ---- LABSTR.BIN: two string tables
    strtabs = [[b"WASTELAND LAB", b"Press any key.", b"Lab scenario v1"],
               [b"\x0b hits \x0f time\x0a\x0as\x0a.\r", b"Yes or no?\r\r\x11\x10Yes\r\x10No\r",
                b"\x0b is out cold.\x06", b"h\x0cim\x0cer\x0c", b"\x0ehe\x0eshe\x0eit\x0e"]]
    files["LABSTR.BIN"] = labstr_encode([C.strtab_encode(DICT, t) for t in strtabs])

    # ---- LABTABLES.BIN
    tables = {
        "mapOffsets": [mf[0] for mf in map_facts] + [0] * 39,
        "tileMapOffsets": [mf[1] for mf in map_facts] + [0] * 47,
        "locationMapping": [(2 << 6) | i for i in range(3)] + [0] * 47,
        "mapSizes": [m["size"] for m in maps] + [0] * 47,
        "sharedLocations": [2] * 125,
        "mobSpriteMap": [0, 6, 3, 4, 2, 1],
        "savegameOffsets": [sg_off, 0xFFFFFFFF],
        "savegameSize": SAVEGAME_RESERVED,
        "shopListRelOffsets": [0, SHOP_BLOCK, SHOP_BLOCK, SHOP_BLOCK],
        "mapCounts": [3, 0], "shopListCounts": [1, 0],
        "tilesetOffsets": [0] * 9, "tilesetSizes": [len(allhtds)] + [0] * 8,
        "portraitOffsets1": portrait_offsets + [0] * 30, "portraitOffsets2": [0] * 49,
        "portraitIndices1": [0, 1, 2, 3] + [0x80] * 76, "portraitIndices2": [0x80] * 80,
    }
    files["LABTABLES.BIN"] = labtables_encode(tables)

    # ---- manifest
    maps_truth = []
    for m, (off, tmo, facts) in zip(maps, map_facts):
        padded = list(m["strings"]) + [b""] * ((-len(m["strings"])) % 4)
        maps_truth.append({
            "game": 1, "index": m["location"], "location": m["location"], "size": m["size"],
            "offset": off, "tileMapOffset": tmo, "bodySize": facts["bodySize"],
            "encryptedPrefixLength": facts["encryptedPrefixLength"],
            "centralDirectory": facts["centralDirectory"],
            "info": mapinfo_decode(mapinfo_encode(m["size"], m["info"])),
            "cells": {"actionClass": m["class"], "action": m["action"], "image": m["image"]},
            "actions": {str(c): [None] + [_norm(c, r) for r in recs] for c, recs in sorted(m["actions"].items())},
            "npcs": [char_decode(char_encode(c)) for c in m["npcs"]],
            "mobs": [mob_decode(mob_encode(x), x["name"]) for x in m["mobs"]],
            "strings": [s(x) for x in padded],
        })
    manifest.update({
        "files": {k: {"size": len(v), "sha256": sha(v)} for k, v in sorted(files.items())},
        "tables": tables,
        "maps": maps_truth,
        "savegame": {"offset": sg_off, **savegame_decode(files["GAME1"], sg_off)},
        "shopLists": [{"offset": shop_off, **shop_decode(files["GAME1"], shop_off)}],
        "tilesets": [{"id": 0, "file": "ALLHTDS1", "offset": 0, "disk": 0, "tileCount": 32,
                      "tiles": tiles}],
        "portraits": portraits_truth,
        "sprites": sprite_truth,
        "font": font_truth,
        "cursors": curs_truth,
        "title": {"sha256": sha(title), "firstRow": unpack4(title[:144], 288)[0]},
        "ending": {"baseSha256": sha(end_base), "updates": [[d, [[o, p.hex()] for o, p in ps]]
                                                            for d, ps in end_updates],
                   "frameSha256": [sha(end_base), sha(f1), sha(f2)]},
        "stringTables": [[s(x) for x in (t + [b""] * ((-len(t)) % 4))] for t in strtabs],
    })
    for name, data in files.items():
        with open(os.path.join(outdir, name), "wb") as fh:
            fh.write(data)
    with open(os.path.join(outdir, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
    return manifest


# ---------------------------------------------------------------------------
# Reference reader: re-read every file and compare with the manifest
# ---------------------------------------------------------------------------

def verify(outdir: str) -> list[str]:
    def rd(n: str) -> bytes:
        with open(os.path.join(outdir, n), "rb") as fh:
            return fh.read()

    with open(os.path.join(outdir, "manifest.json")) as fh:
        man = json.load(fh)
    errs: list[str] = []

    def eq(label: str, got, want) -> None:
        if got != want:
            errs.append("%s: got %s want %s" % (label, str(got)[:120], str(want)[:120]))

    for name, meta in man["files"].items():
        eq("file %s sha256" % name, sha(rd(name)), meta["sha256"])
    t = labtables_decode(rd("LABTABLES.BIN"))
    eq("tables", t, man["tables"])
    game = rd("GAME1")
    # maps located only through the tables, via location indices
    for loc in range(50):
        code = t["locationMapping"][loc]
        if code >> 6 != 2:
            continue
        idx = code & 0x3F
        got = map_decode(game, t["mapOffsets"][idx], t["mapSizes"][loc], t["tileMapOffsets"][loc])
        want = man["maps"][idx]
        for k in ("size", "bodySize", "encryptedPrefixLength", "centralDirectory", "info", "cells",
                  "actions", "npcs", "mobs", "strings"):
            g = got[k]
            if k == "actions":
                g = json.loads(json.dumps(g))
            eq("map %d %s" % (idx, k), json.loads(json.dumps(g)), want[k])
        eq("map %d wllib prefix" % idx, got["wllibPrefixLength"], want["encryptedPrefixLength"])
        nxt = t["mapOffsets"][idx + 1] if idx + 1 < t["mapCounts"][0] else t["savegameOffsets"][0]
        eq("map %d block end" % idx, t["mapOffsets"][idx] + got["blockEnd"], nxt)
    sg = savegame_decode(game, t["savegameOffsets"][0])
    want = dict(man["savegame"])
    want.pop("offset")
    eq("savegame", json.loads(json.dumps(sg)), want)
    shop_base = t["savegameOffsets"][0] + t["savegameSize"]
    for i in range(t["shopListCounts"][0]):
        eq("shop %d" % i, shop_decode(game, shop_base + t["shopListRelOffsets"][i])["items"],
           man["shopLists"][i]["items"])
    eq("game length", len(game), shop_base + t["shopListCounts"][0] * SHOP_BLOCK)
    # tileset
    ah = rd("ALLHTDS1")
    payload, disk, nxt = C.msqh_decode(ah, t["tilesetOffsets"][0])
    eq("tileset size field", nxt, t["tilesetSizes"][0])
    tiles = [unpack4(C.vxor_decode(payload[i:i + 128], 8), 16) for i in range(0, len(payload), 128)]
    eq("tileset tiles", tiles, man["tilesets"][0]["tiles"])
    # portraits via the two-stage lookup
    ap = rd("ALLPICS1")
    for pt in man["portraits"]:
        ci = t["portraitIndices1"][pt["rawId"]]
        off = t["portraitOffsets1"][ci]
        base_raw, _, o2 = C.msqh_decode(ap, off)
        base = C.vxor_decode(base_raw, 48)
        anim, _, _ = C.msqh_decode(ap, o2)
        scripts, updates = portrait_anim_decode(anim)
        eq("portrait %d base" % pt["rawId"], base.hex(), pt["base"])
        eq("portrait %d scripts" % pt["rawId"], scripts, pt["scripts"])
        eq("portrait %d updates" % pt["rawId"], updates, pt["updates"])
        f1 = apply_updates(base, updates[scripts[0][0][1]])
        f2 = apply_updates(f1, updates[scripts[0][1][1]])
        eq("portrait %d frame1" % pt["rawId"], sha(f1), pt["frames"][1]["sha256"])
        eq("portrait %d frame2 returns to base" % pt["rawId"], sha(f2), pt["frames"][0]["sha256"])
    # sprites
    sp, mk = rd("IC0_9.WLF"), rd("MASKS.WLF")
    for n, st in enumerate(man["sprites"]):
        eq("sprite %d" % n, planes_decode(sp[n * 128:(n + 1) * 128], 16, 16), st["pixels"])
        m = [[(mk[n * 32 + y * 2 + x // 8] >> (7 - x % 8)) & 1 for x in range(16)] for y in range(16)]
        eq("mask %d" % n, m, st["transparent"])
    fn = rd("COLORF.FNT")
    for g, pix in enumerate(man["font"]):
        eq("glyph %d" % g, planes_decode(fn[g * 32:(g + 1) * 32], 8, 8), pix)
    cu = rd("CURS")
    for k, ct in enumerate(man["cursors"]):
        pix, vis = cursor_decode(cu[k * 256:(k + 1) * 256])
        eq("cursor %d pixels" % k, [[p if v else p for p, v in zip(pr, vr)] for pr, vr in zip(pix, vis)],
           ct["pixels"])
        eq("cursor %d visible" % k, vis, ct["visible"])
    ti = C.vxor_decode(rd("TITLE.PIC"), 144)
    eq("title", sha(ti), man["title"]["sha256"])
    ed = rd("END.CPA")
    eb, _, o2 = C.msqh_decode(ed, 0)
    eb = C.vxor_decode(eb, 144)
    ea, _, _ = C.msqh_decode(ed, o2, sig=b"\x08\x67\x01")
    ups = ending_anim_decode(ea)
    eq("ending updates", ups, man["ending"]["updates"])
    frames = [eb]
    for _, ps in ups:
        frames.append(ending_apply(frames[-1], ps))
    eq("ending frames", [sha(f) for f in frames], man["ending"]["frameSha256"])
    st = labstr_decode(rd("LABSTR.BIN"))
    eq("string tables", [[s(x) for x in tb] for tb in st], man["stringTables"])
    return errs


def selftest() -> int:
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        man = generate(d1)
        generate(d2)
        errs = verify(d1)
        same = all(open(os.path.join(d1, f), "rb").read() == open(os.path.join(d2, f), "rb").read()
                   for f in os.listdir(d1))
        print("files written:      %d (+ manifest.json)" % len(man["files"]))
        for name, meta in man["files"].items():
            print("  %-14s %6d bytes  sha256 %s" % (name, meta["size"], meta["sha256"][:16]))
        for m in man["maps"]:
            print("map %d: %dx%d offset %d tileMapOffset %d body %d prefix %d" % (
                m["index"], m["size"], m["size"], m["offset"], m["tileMapOffset"], m["bodySize"],
                m["encryptedPrefixLength"]))
        print("deterministic:      %s" % ("yes" if same else "NO"))
        if errs or not same:
            print("FAILED %d checks" % len(errs))
            for e in errs[:40]:
                print("  " + e)
            return 1
        print("fixtures_gen selftest: OK")
        return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        sys.exit(selftest())
    if not args:
        print(__doc__)
        sys.exit(2)
    seed = DEFAULT_SEED
    if "--seed" in args:
        seed = int(args[args.index("--seed") + 1])
    out = args[0]
    generate(out, seed)
    errs = verify(out)
    print("wrote %s (seed %d); verify: %s" % (out, seed, "OK" if not errs else "%d errors" % len(errs)))
    sys.exit(1 if errs else 0)
