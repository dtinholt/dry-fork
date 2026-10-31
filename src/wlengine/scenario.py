"""The scenario compiler (SPEC-05 section 13).

``compile(scenario_dir, out_dir)`` reads ``scenario.json`` and the files it
lists and writes the lab data set of SPEC-02 section 12.1: GAME1 (four maps,
the new-game savegame, three shop lists), LABTABLES.BIN, LABSTR.BIN,
LABSKILL.BIN, LABHOOKS.JSON, PARAGRAPHS.JSON, ALLHTDS1, ALLPICS1, IC0_9.WLF,
MASKS.WLF, COLORF.FNT, CURS, TITLE.PIC and END.CPA.

Everything is written with the engine's own encoders, so reading the output
back through the engine's loaders returns the JSON content again.
"""

from __future__ import annotations

import json
import os

from . import codecs, containers, graphics, huffman, maps, rules, strings
from .errors import FormatError

# The 60-byte dictionary D of SPEC-02 section 9.3.
DICT = (b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r"
        b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;")

# Section order inside the map-data body (SPEC-03 section 6.1).
TABLE_ORDER_A = [0, 1, 2, 3, 4, 5, 6, 7, 15]
TABLE_ORDER_B = [8, 9, 10, 11, 12, 13, 14]

NO_CHANGE = 255

MAPINFO_FIELDS = ("encounterFrequency", "tileset", "randomMonsterTypes",
                  "maxRandomEncounters", "borderImage")

PORTRAIT_BASE_SIZE = graphics.PORTRAIT_BASE_SIZE
PORTRAIT_STRIDE = graphics.PORTRAIT_STRIDE
TITLE_STRIDE = graphics.TITLE_STRIDE
ENDING_SIGNATURE = graphics.ENDING_SIGNATURE


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _u16(v: int) -> bytes:
    return (v & 0xFFFF).to_bytes(2, "little")


def _u32(v: int) -> bytes:
    return (v & 0xFFFFFFFF).to_bytes(4, "little")


def _fixed(text, n: int) -> bytes:
    raw = text.encode("latin-1") if isinstance(text, str) else bytes(text)
    return raw[:n] + bytes(max(0, n - len(raw)))


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _write(out_dir: str, name: str, data: bytes) -> None:
    with open(os.path.join(out_dir, name), "wb") as fh:
        fh.write(data)


def _pad4(lst: list) -> list:
    return list(lst) + [""] * ((-len(lst)) % 4)


# ---------------------------------------------------------------------------
# Action records (SPEC-03 section 9.2, lab layouts)
# ---------------------------------------------------------------------------

def _tail(nc: int, na: int) -> bytes:
    return bytes((nc,)) if nc >= 253 else bytes((nc, na))


def encode_record(cls: int, r: dict) -> bytes:
    nc, na = r.get("newClass", NO_CHANGE), r.get("newAction", 0)
    if cls == 1:  # PRINT
        msgs = r["messages"]
        b = bytes(m | (0x80 if i == len(msgs) - 1 else 0) for i, m in enumerate(msgs))
        return b + _tail(nc, na)
    if cls == 3:  # FIXED_ENCOUNTER
        b = bytes((r["visibleDistance"], r["hitDistance"], r["message"]))
        for mob, rnd, grp in r["groups"]:
            b += bytes((mob, (0x80 if rnd else 0) | grp))
        flags = r["properName"] | (r["friendly"] << 1) | (r["immobile"] << 2) | (r["npc"] << 4)
        return b + bytes((flags,)) + _tail(nc, na)
    if cls == 4:  # MASK (lab door)
        return bytes((r["message"], (0x80 if r["impassable"] else 0) | r["tile"])) + _tail(nc, na)
    if cls == 5:  # LOOT (wllib layout)
        b = bytes((nc if nc != NO_CHANGE else 0, na))
        for iid, fixed_, amt in r["items"]:
            b += bytes(((0x80 if fixed_ else 0) | iid, amt))
        if r.get("cash") is not None:
            fixed_, amt = r["cash"]
            b += bytes((0xDE if fixed_ else 0x5E,)) + _u16(amt)
        return b + b"\xFF"
    if cls == 6:  # SHOP (lab)
        return bytes((r["shop"], r["message"])) + _tail(nc, na)
    if cls == 10:  # TRANSITION
        flags = (0x80 if r["relative"] else 0) | (0x40 if r["confirm"] else 0) | r["message"]
        return bytes((flags, r["x"] & 0xFF, r["y"] & 0xFF, r["location"])) + _tail(nc, na)
    if cls == 11:  # BLOCKED
        return bytes((r["message"],)) + _tail(nc, na)
    raise FormatError("scenario: lab rules define no record for class %d" % cls)


def encode_mapinfo(size: int, mi: dict) -> bytes:
    b = bytearray(50)
    b[2] = size
    for i, k in enumerate(MAPINFO_FIELDS):
        b[5 + i] = mi[k]
    b[0x0A:0x0C] = _u16(mi["timePerStep"])
    b[0x0C] = mi["healRate"]
    return bytes(b)


def encode_mob(m: dict) -> bytes:
    return (_u16(m["sturdiness"])
            + bytes((m["combatRating"], m["randomDamage"],
                     (m["maxGroup"] << 4) | m["armorClass"],
                     (m["fixedDamage"] << 4) | m["weaponType"],
                     m["type"], m["portrait"])))


# ---------------------------------------------------------------------------
# Map block (SPEC-03 sections 3 to 9)
# ---------------------------------------------------------------------------

def build_map(m: dict, disk: int = 0):
    """Return ``(block, tile_map_offset, facts)`` for one map dict."""
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
    body += encode_mapinfo(S, m["info"])

    offsets = [0] * 16

    def emit_table(c: int) -> None:
        recs = m["actions"].get(c)
        if not recs:
            return
        start = len(body)
        offsets[c] = start
        encs = [None] + [encode_record(c, r) for r in recs]  # slot 0 is null
        pos = start + 2 * len(encs)
        ptrs = []
        for e in encs:
            if e is None:
                ptrs.append(0)
            else:
                ptrs.append(pos)
                pos += len(e)
        for p in ptrs:
            body.extend(_u16(p))
        for e in encs:
            if e is not None:
                body.extend(e)

    for c in TABLE_ORDER_A:
        emit_table(c)
    npc_off = None
    if m["npcs"]:
        npc_off = len(body)
        n = len(m["npcs"])
        body.extend(_u16(0))
        first = npc_off + 2 + 2 * n
        for i in range(n):
            body.extend(_u16(first + i * 0x100))
        for ch in m["npcs"]:
            body.extend(containers.encode_character(ch))
    for c in TABLE_ORDER_B:
        emit_table(c)
    specials_off = 0  # lab rule: no special-action table
    names_off = len(body)
    for mob in m["mobs"]:
        body.extend(mob["name"] + b"\x00")
    data_off = len(body)
    for mob in m["mobs"]:
        body.extend(encode_mob(mob))
    strings_off = len(body)
    if npc_off is None:
        npc_off = strings_off  # lab rule: no NPCs -> npcOffset = stringsOffset
    body.extend(strings.encode_table(m["dictionary"], m["strings"]))

    cd = _u16(strings_off) + _u16(names_off) + _u16(data_off)
    for o in offsets:
        cd += _u16(o)
    cd += _u16(specials_off) + _u16(npc_off)
    body[cd_at:cd_at + 42] = cd

    prefix = bytes(body[:strings_off])
    if not codecs.rotating_xor_prefix_is_unambiguous(prefix):
        raise FormatError("scenario: map %r has an ambiguous encrypted prefix"
                          % m.get("name", "?"))
    enc = codecs.rotating_xor_encode(prefix)
    data_section = enc + bytes(body[strings_off:]) + b"\x00"  # final byte: unknown, lab 0
    tile_map = bytes(v for row in img for v in row)
    tsec = _u32(S * S) + _u32(0) + huffman.encode(tile_map)
    header = b"msq" + bytes(((0x30 + disk) & 0xFF,))
    block = header + data_section + tsec
    tmo = len(header) + len(data_section)
    facts = {"bodySize": len(body), "encryptedPrefixLength": strings_off,
             "centralDirectory": {"stringsOffset": strings_off, "mobNamesOffset": names_off,
                                  "mobDataOffset": data_off, "actionClassOffsets": offsets,
                                  "specialsOffset": specials_off, "npcOffset": npc_off}}
    return block, tmo, facts


# ---------------------------------------------------------------------------
# JSON to engine-record conversion
# ---------------------------------------------------------------------------

def _record_from_json(c: int, r: dict) -> dict:
    if c == 1:
        d = {"messages": r["messages"]}
    elif c == 3:
        d = {"visibleDistance": r["visible_distance"], "hitDistance": r["hit_distance"],
             "message": r["message"], "groups": r["groups"], "properName": r["proper_name"],
             "friendly": r["friendly"], "immobile": r["immobile"], "npc": 0}
    elif c == 4:
        d = {"message": r["message"], "impassable": r["impassable"], "tile": r["tile"]}
    elif c == 5:
        d = {"items": r["items"], "cash": r["cash"]}
    elif c == 6:
        d = {"shop": r["shop"], "message": r["message"]}
    elif c == 10:
        d = {k: r[k] for k in ("relative", "confirm", "message", "x", "y", "location")}
    elif c == 11:
        d = {"message": r["message"]}
    else:
        raise FormatError("scenario: lab rules define no record for class %d" % c)
    d["newClass"], d["newAction"] = r["new_class"], r["new_action"]
    return d


def _character_from_json(p: dict, npc: int, catalog: dict, ranks: list) -> dict:
    a = p["attrs"]
    level = p["level"]
    hp = 10 + a["STR"] + (level - 1) * (2 + a["STR"] // 5)
    bonus = 0
    if p["armour_slot"]:
        bonus = catalog[p["items"][p["armour_slot"] - 1][0]]["damage"]
    evasion = dict((s, l) for s, l in p["skills"]).get(11, 0)
    return {
        "name": p["name"].encode("latin-1"), "strength": a["STR"], "intelligence": a["IQ"],
        "luck": a["LCK"], "speed": a["SPD"], "agility": a["AGL"], "dexterity": 0,
        "charisma": a["CHA"], "money": p["money"], "gender": p["gender"],
        "nationality": p["nationality"], "armorClass": a["AGL"] // 5 + bonus + evasion,
        "maxCon": hp, "curCon": hp, "weaponSlot": p["weapon_slot"], "skillPoints": 0,
        "experience": p["xp"], "level": level, "armorSlot": p["armour_slot"], "lastCon": 0,
        "afflictions": 0, "npc": npc, "itemRefuse": 0, "skillRefuse": 0, "attribRefuse": 0,
        "tradeRefuse": 0, "joinString": 0, "willingness": 0,
        "rank": ranks[min(level, 7) - 1].encode("latin-1"), "gameWon": 0,
        "specialPromotion": 0, "skills": [list(x) for x in p["skills"]],
        "items": [list(x) for x in p["items"]],
    }


def _map_from_json(m: dict, size: int, catalog: dict, ranks: list) -> dict:
    info = m["info"]
    mi = {"encounterFrequency": info["encounter_frequency"], "tileset": info["tileset"],
          "randomMonsterTypes": info["random_monster_types"],
          "maxRandomEncounters": info["max_random_encounters"],
          "borderImage": info["border_image"], "timePerStep": info["time_per_step"],
          "healRate": info["heal_rate"]}
    mobs = []
    for mob in m["mobs"]:
        name = mob["name"].encode("latin-1")
        if mob.get("plural_suffix"):
            name += b"\x0a\x0a" + mob["plural_suffix"].encode("latin-1") + b"\x0a"
        mobs.append({"name": name, "sturdiness": mob["sturdiness"],
                     "combatRating": mob["combat_rating"], "randomDamage": mob["random_damage"],
                     "maxGroup": mob["max_group"], "armorClass": mob["armor_class"],
                     "fixedDamage": mob["fixed_damage"], "weaponType": mob["weapon_type"],
                     "type": mob["type"], "portrait": mob["portrait"]})
    actions = {}
    for c, recs in m["records"].items():
        if recs:
            actions[int(c)] = [_record_from_json(int(c), r) for r in recs]
    return {"size": size, "class": m["action_class"], "action": m["action_value"],
            "image": [[t + 10 for t in row] for row in m["tiles"]],
            "info": mi, "actions": actions,
            "npcs": [_character_from_json(n, 1, catalog, ranks) for n in m["npcs"]],
            "mobs": mobs, "dictionary": DICT,
            "strings": [s.encode("latin-1") for s in m["strings"]]}


# ---------------------------------------------------------------------------
# Savegame and shop lists
# ---------------------------------------------------------------------------

def _build_savegame(scenario_dir: str, scen: dict, catalog: dict, ranks: list) -> bytes:
    party = _load_json(os.path.join(scenario_dir, "party.json"))["party"]
    st = scen["start"]
    n = len(party)
    chars = [_character_from_json(p, 0, catalog, ranks) for p in party]
    empty = containers.decode_character(bytes(0x100))
    groups = [{"order": list(range(1, n + 1)) + [0] * (7 - n), "x": st["x"], "y": st["y"],
               "map": st["location"], "prevX": 0, "prevY": 0, "prevMap": 0}]
    groups += [{"order": [0] * 7, "x": 0, "y": 0, "map": 0,
                "prevX": 0, "prevY": 0, "prevMap": 0}] * 3
    sg = {"groups": groups, "viewportX": st["x"], "viewportY": st["y"],
          "currentMembers": n, "currentParty": 0, "currentMap": st["location"],
          "totalMembers": n, "extraGroups": 0, "minute": 0, "hour": st["hour"],
          "combatScrollSpeed": 0, "serial": 0, "characters": chars + [empty] * (7 - n)}
    return containers.encode_savegame(sg, 0)


def _shop_items(sh: dict, catalog: dict) -> list:
    recs = []
    for i in range(94):
        it = catalog.get(i + 1)
        if it is None:
            recs.append({"price": 0, "stock": 0, "type": 0, "lowFlags": 0,
                         "capacity": 0, "skill": 0, "damage": 0, "ammo": 0})
        else:
            recs.append({"price": it["price"], "stock": sh["stock"].get(str(it["id"]), 0),
                         "type": it["type_byte"] >> 3, "lowFlags": it["type_byte"] & 7,
                         "capacity": it["capacity"], "skill": it["skill"],
                         "damage": it["damage"], "ammo": it["ammo"]})
    return recs


# ---------------------------------------------------------------------------
# LABTABLES.BIN (SPEC-02 section 12.2)
# ---------------------------------------------------------------------------

def _encode_labtables(t: dict) -> bytes:
    out = bytearray(containers.LABTABLES_SIZE)
    out[0:8] = containers.LABTABLES_MAGIC
    for k, (off, fmt, n) in containers.LT.items():
        vals = t[k] if isinstance(t[k], list) else [t[k]]
        if len(vals) != n:
            raise FormatError("LABTABLES: %s has %d values, expected %d" % (k, len(vals), n))
        w = containers._WIDTH[fmt]
        for i, v in enumerate(vals):
            out[off + i * w:off + (i + 1) * w] = (v & ((1 << (8 * w)) - 1)).to_bytes(w, "little")
    return bytes(out)


def _build_labtables(map_facts: list, sg_off: int, tileset_size: int,
                     portrait_offsets: list) -> bytes:
    n = len(map_facts)
    t = {
        "mapOffsets": [mf[0] for mf in map_facts] + [0] * (42 - n),
        "tileMapOffsets": [mf[1] for mf in map_facts] + [0] * (50 - n),
        "locationMapping": [(2 << 6) | i for i in range(n)] + [0] * (50 - n),
        "mapSizes": [mf[3]["size"] for mf in map_facts] + [0] * (50 - n),
        "sharedLocations": [2] * 125,
        "mobSpriteMap": [0, 6, 3, 4, 2, 1],
        "savegameOffsets": [sg_off, 0xFFFFFFFF],
        "savegameSize": containers.SAVEGAME_RESERVED,
        "shopListRelOffsets": [i * containers.SHOP_BLOCK for i in range(4)],
        "mapCounts": [n, 0],
        "shopListCounts": [3, 0],
        "tilesetOffsets": [0] * 9,
        "tilesetSizes": [tileset_size] + [0] * 8,
        "portraitOffsets1": list(portrait_offsets) + [0] * (34 - len(portrait_offsets)),
        "portraitOffsets2": [0] * 49,
        "portraitIndices1": [0x80, 0, 1, 2, 3] + [0x80] * 75,
        "portraitIndices2": [0x80] * 80,
    }
    return _encode_labtables(t)


# ---------------------------------------------------------------------------
# LABSTR.BIN (SPEC-02 section 12.3) and LABSKILL.BIN (SPEC-04 section 3.2)
# ---------------------------------------------------------------------------

def _labstr_file(tables: list) -> bytes:
    n = len(tables)
    head = strings.LABSTR_MAGIC + _u16(n) + _u16(0)
    pos = len(head) + 8 * n
    offs, sizes = b"", b""
    for t in tables:
        offs += _u32(pos)
        sizes += _u32(len(t))
        pos += len(t)
    return head + offs + sizes + b"".join(tables)


def _build_labstr(scenario_dir: str, scen: dict) -> bytes:
    strs = _load_json(os.path.join(scenario_dir, "strings.json"))["strings"]
    skills = _load_json(os.path.join(scenario_dir, "skills.json"))["skills"]
    items = _load_json(os.path.join(scenario_dir, "items.json"))["items"]
    lt = scen["labstr_tables"]
    t1 = [""] * (max(s["id"] for s in strs) + 1)
    for s in strs:
        t1[s["id"]] = s["text"].replace("{name}", "\x0b").replace("{num}", "\x0f")
    t2 = [""] + [s["name"] for s in sorted(skills, key=lambda k: k["id"])]
    t2 += [it["name"] for it in sorted(items, key=lambda k: k["id"])]
    tables = [lt["0"]["strings"], t1, t2, lt["3"]["strings"], lt["4"]["strings"],
              lt["5"]["strings"]]
    enc = [strings.encode_table(DICT, [s.encode("latin-1") for s in _pad4(t)]) for t in tables]
    return _labstr_file(enc)


def _build_labskill(scenario_dir: str) -> bytes:
    d = _load_json(os.path.join(scenario_dir, "skills.json"))
    e0 = d["entry0"]
    out = bytearray()
    out += bytes(((e0["iq_req"] << 3) | e0["cost"], e0["attr_offset"]))
    for s in sorted(d["skills"], key=lambda k: k["id"]):
        out += bytes(s["labskill_bytes"])
    return bytes(out)


# ---------------------------------------------------------------------------
# Graphics (SPEC-02 sections 6 to 8, 12.6, 12.7)
# ---------------------------------------------------------------------------

def _planes_encode(pix: list, bytes_per_row: int) -> bytes:
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


def _mask_encode(mask: list) -> bytes:
    out = bytearray()
    for row in mask:
        for bx in range(2):
            v = 0
            for i in range(8):
                v |= (row[bx * 8 + i] & 1) << (7 - i)
            out.append(v)
    return bytes(out)


def _cursor_encode(pix: list, vis: list) -> bytes:
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


def _portrait_anim_encode(scripts: list, updates: list) -> bytes:
    sb = bytearray()
    for sc in scripts:
        for d, u in sc:
            sb += bytes((d, u))
        sb.append(0xFF)
    ub = bytearray()
    for upd in updates:
        for off, data in upd:
            ub += _u16(((len(data) - 1) << 12) | off) + data
        ub += _u16(0xFFFF)
    return _u16(len(sb)) + bytes(sb) + _u16(len(ub)) + bytes(ub)


def _ending_anim_encode(updates: list) -> bytes:
    st = bytearray()
    for delay, patches in updates:
        st += _u16(delay)
        for off, data in patches:
            st += _u16(off) + data
        st += _u16(0xFFFF)
    st += _u16(0xFFFF)
    return _u16(len(st)) + bytes(st) + _u16(0)


def _placeholder_tile(t: int) -> list:
    """Tile ``t``: fill ``t mod 16``, one-pixel border ``(t + 8) mod 16``."""
    pix = [[t % 16 for _ in range(16)] for _ in range(16)]
    border = (t + 8) % 16
    for x in range(16):
        pix[0][x] = border
        pix[15][x] = border
    for y in range(16):
        pix[y][0] = border
        pix[y][15] = border
    return pix


def _placeholder_portrait(p: int) -> list:
    """Portrait ``p``: fill ``4 + p``, centred 48 x 42 rectangle of colour 15."""
    pix = [[4 + p for _ in range(96)] for _ in range(84)]
    for y in range(21, 63):
        for x in range(24, 72):
            pix[y][x] = 15
    return pix


def _build_allhtds(scenario_dir: str) -> bytes:
    tiles = _load_json(os.path.join(scenario_dir, "tiles.json"))["tiles"]
    raw = b"".join(codecs.vertical_xor_encode(graphics.pack4(_placeholder_tile(t["id"])), 8)
                   for t in sorted(tiles, key=lambda k: k["id"]))
    return huffman.encode_msq(raw, 0)


def _build_allpics(scenario_dir: str):
    portraits = _load_json(os.path.join(scenario_dir, "portraits.json"))["portraits"]
    out = bytearray()
    offsets = []
    for p in sorted(portraits, key=lambda k: k["raw_id"]):
        base = graphics.pack4(_placeholder_portrait(p["raw_id"] - 1))
        upd = [(2000, b"\xff" * 8)]
        anim = _portrait_anim_encode([[(20, 0), (20, 0)]], [upd])
        offsets.append(len(out))
        out += huffman.encode_msq(codecs.vertical_xor_encode(base, PORTRAIT_STRIDE), 0)
        out += huffman.encode_msq(anim, 0)
    return bytes(out), offsets


def _build_sprites():
    sprites, masks = bytearray(), bytearray()
    for n in range(10):
        pix = [[(n + x // 4 + y // 4) % 16 for x in range(16)] for y in range(16)]
        msk = [[1 if (x - 7.5) ** 2 + (y - 7.5) ** 2 > 56 else 0
                for x in range(16)] for y in range(16)]
        sprites += _planes_encode(pix, 2)
        masks += _mask_encode(msk)
    return bytes(sprites), bytes(masks)


def _build_font() -> bytes:
    out = bytearray()
    for g in range(32):
        pix = [[((g >> (x % 5)) & 1) * ((g + y) % 15 + 1) for x in range(8)]
               for y in range(8)]
        out += _planes_encode(pix, 1)
    return bytes(out)


def _build_cursors() -> bytes:
    out = bytearray()
    for k in range(2):
        pix = [[(x + y + k) % 16 for x in range(16)] for y in range(16)]
        vis = [[1 if x <= y + k * 3 else 0 for x in range(16)] for y in range(16)]
        out += _cursor_encode(pix, vis)
    return bytes(out)


def _build_title() -> bytes:
    pix = [[((x // 18) ^ (y // 16)) % 16 for x in range(288)] for y in range(128)]
    return codecs.vertical_xor_encode(graphics.pack4(pix), TITLE_STRIDE)


def _build_ending() -> bytes:
    base = graphics.pack4([[((x + y) // 24) % 16 for x in range(288)] for y in range(128)])
    updates = [(5, [(41, bytes.fromhex("11223344")), (40 * 100 + 35, bytes.fromhex("FFEEDDCC"))]),
               (9, [(0, bytes.fromhex("0F0F0F0F"))])]
    anim = _ending_anim_encode(updates)
    return (huffman.encode_msq(codecs.vertical_xor_encode(base, TITLE_STRIDE), 0)
            + huffman.encode_msq(anim, 0, ENDING_SIGNATURE))


# ---------------------------------------------------------------------------
# The compiler
# ---------------------------------------------------------------------------

def compile(scenario_dir: str, out_dir: str) -> None:
    """Compile a scenario directory into a lab data set (SPEC-05 section 13)."""
    _compile(scenario_dir, out_dir)


# ---------------------------------------------------------------------------
# Loading a compiled lab data set (SPEC-02 section 12, SPEC-05)
# ---------------------------------------------------------------------------


def _call(mod, names, *args, **kwargs):
    for n in names:
        fn = getattr(mod, n, None)
        if callable(fn):
            return fn(*args, **kwargs)
    raise FormatError("scenario: %s has none of %r" % (mod.__name__, names))


class Scenario:
    """A compiled lab data set, read back through the engine's own loaders."""

    def __init__(self, data_dir):
        self.dir = data_dir
        self.maps = {}
        self.hooks = []
        self.paragraphs = {}
        self.skills = {}
        self.shops = {}
        self.savegame = None
        self.location_names = {}
        self.start = {"location": 0, "x": 0, "y": 0, "hour": 8, "minute": 0,
                      "day": 1, "paragraph": 1}
        self._load()

    # -- raw file access ---------------------------------------------------

    def _read(self, name):
        path = os.path.join(self.dir, name)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as fh:
            return fh.read()

    def _json(self, name):
        path = os.path.join(self.dir, name)
        if not os.path.exists(path):
            return None
        return _load_json(path)

    # -- loading -----------------------------------------------------------

    def _load(self):
        self.tables = containers.read_tables(os.path.join(self.dir, "LABTABLES.BIN"))
        self.game1 = self._read("GAME1")
        self._load_maps()
        self._load_savegame()
        self._load_shops()
        labstr = os.path.join(self.dir, "LABSTR.BIN")
        if os.path.exists(labstr):
            self.labstr = strings.read_labstr(labstr)
        skills = os.path.join(self.dir, "LABSKILL.BIN")
        if os.path.exists(skills):
            self.skill_table = rules.read_skill_table(skills)
        hooks = self._json("LABHOOKS.JSON")
        if hooks is not None:
            self.hooks = hooks if isinstance(hooks, list) else hooks.get("hooks", [])
        paras = self._json("PARAGRAPHS.JSON")
        if paras is not None:
            self.paragraphs = paras.get("paragraphs", paras) if isinstance(paras, dict) else paras
        locs = self._json("LOCATIONS.JSON")
        if locs is not None:
            entries = locs.get("locations", locs) if isinstance(locs, dict) else locs
            for e in entries or []:
                try:
                    self.location_names[int(e["location"])] = e["name"]
                except (KeyError, TypeError, ValueError):
                    continue

    def _load_maps(self):
        counts = self.tables["mapCounts"]
        for loc in range(len(self.tables["locationMapping"])):
            code = self.tables["locationMapping"][loc]
            if code == 0:
                continue
            disk = code >> 6
            if disk == 2 and counts[0] == 0:
                continue
            if disk == 1 and counts[1] == 0:
                continue
            try:
                self.maps[loc] = maps.load_map(self.dir, loc)
            except FormatError:
                continue

    def _load_savegame(self):
        offs = self.tables["savegameOffsets"]
        if not offs or offs[0] == 0xFFFFFFFF:
            return
        self.savegame = containers.decode_savegame(self.game1, offs[0])
        sg = self.savegame
        g0 = sg["groups"][0]
        self.start = {"location": g0["map"], "x": g0["x"], "y": g0["y"],
                      "hour": sg["hour"], "minute": sg["minute"], "day": 1,
                      "paragraph": 1}

    def _load_shops(self):
        offs = self.tables["savegameOffsets"]
        if not offs or offs[0] == 0xFFFFFFFF:
            return
        base = offs[0] + self.tables["savegameSize"]
        rel = self.tables["shopListRelOffsets"]
        for i in range(self.tables["shopListCounts"][0]):
            self.shops[i] = containers.decode_shop_list(self.game1, base + rel[i])

    def party_from_savegame(self):
        sg = self.savegame
        if sg is None:
            return []
        out = []
        n = sg["currentMembers"]
        for i in range(n):
            c = sg["characters"][i]
            aff = c["afflictions"]
            cond = 2 if aff & 2 else (1 if aff & 1 else 0)
            out.append({
                "slot": i + 1, "name": c["name"], "npc": c["npc"],
                "level": c["level"], "xp": c["experience"],
                "max_hp": c["maxCon"], "hp": c["curCon"], "cond": cond,
                "money": c["money"], "ac": c["armorClass"], "rank": c["rank"],
                "skill_points": c["skillPoints"],
                "items": [list(x) for x in c["items"]],
                "skills": [list(x) for x in c["skills"]],
                "weapon_slot": c["weaponSlot"], "armour_slot": c["armorSlot"],
                "attrs": {"STR": c["strength"], "IQ": c["intelligence"],
                          "LCK": c["luck"], "SPD": c["speed"],
                          "AGL": c["agility"], "CHA": c["charisma"]},
                "gender": c["gender"], "nationality": c["nationality"],
                "game_won": c["gameWon"],
            })
        return out

    def _load_game1(self, raw):
        res = _call(containers, ("decode_game1", "decode_game", "read_game1",
                                 "parse_game1", "load_game1", "decode_game_file"),
                    raw)
        if isinstance(res, dict):
            for key, val in res.items():
                if key in ("maps", "map"):
                    if isinstance(val, dict):
                        self.maps.update(val)
                    else:
                        for i, m in enumerate(val):
                            self.maps[i] = m
                elif key in ("savegame", "save"):
                    self.savegame = val
                elif key in ("shops", "shop_lists"):
                    if isinstance(val, dict):
                        self.shops.update(val)
                    else:
                        for i, s in enumerate(val):
                            self.shops[i] = s
        elif isinstance(res, (list, tuple)):
            for i, m in enumerate(res):
                self.maps[i] = m

    def _load_labtables(self, raw):
        res = _call(containers, ("decode_labtables", "read_labtables",
                                 "parse_labtables", "labtables_decode"), raw)
        if isinstance(res, dict):
            for key, val in res.items():
                if key in ("maps", "map_offsets"):
                    if isinstance(val, dict):
                        self.maps.update(val)
                elif key in ("savegame", "save"):
                    self.savegame = val
                elif key in ("shops", "shop_lists"):
                    if isinstance(val, dict):
                        self.shops.update(val)
                    else:
                        for i, s in enumerate(val):
                            self.shops[i] = s

    def _load_labstr(self, raw):
        res = _call(strings, ("decode_labstr", "read_labstr", "parse_labstr",
                              "decode_tables", "decode_table"), raw)
        if isinstance(res, dict):
            for key, val in res.items():
                if isinstance(val, dict):
                    self.paragraphs.setdefault(key, val)

    def _load_labskill(self, raw):
        res = _call(rules, ("decode_labskill", "read_labskill", "parse_labskill",
                            "decode_skills"), raw)
        if isinstance(res, dict):
            self.skills = res
        elif isinstance(res, list):
            self.skills = {i: s for i, s in enumerate(res)}

    # -- accessors ---------------------------------------------------------

    def map(self, location):
        return self.maps.get(location)

    def location_name(self, location):
        """The display name of ``location`` (SPEC-06 2.1), or ``""``."""
        return self.location_names.get(location, "")

    def hook(self, location, x, y):
        for h in self.hooks:
            if h.get("location") == location and h.get("x") == x and h.get("y") == y:
                return h
        return None

    def paragraph(self, n):
        return self.paragraphs.get(n) or self.paragraphs.get(str(n))

    def premade_party(self):
        return self.party_from_savegame()

    def shop_items(self, n):
        """The 94 decoded records of shop list ``n`` (SPEC-02 section 5)."""
        return self.shops[n]["items"]

    def item(self, item_id):
        """Item id N is record N - 1 of shop list 0 (LR-47)."""
        if item_id < 1:
            return None
        recs = self.shop_items(0)
        if item_id - 1 >= len(recs):
            return None
        return recs[item_id - 1]

    def skill(self, skill_id):
        """``(min_iq, cost, attr_offset)`` for skill id 1 to 35 (LR-6)."""
        if skill_id < 1 or skill_id >= len(self.skill_table):
            return (0, 0, 0)
        b0, b1 = self.skill_table[skill_id]
        return (b0 >> 3, b0 & 7, b1)

    def skill_name(self, skill_id):
        t2 = self.labstr[2] if len(self.labstr) > 2 else []
        if 0 <= skill_id < len(t2):
            return t2[skill_id]
        return ""

    def rank(self, level):
        t3 = self.labstr[3] if len(self.labstr) > 3 else []
        i = min(level, 7) - 1
        if 0 <= i < len(t3):
            return t3[i]
        return ""

    def ui(self, n):
        t1 = self.labstr[1] if len(self.labstr) > 1 else []
        if 0 <= n < len(t1):
            return t1[n]
        return ""

    def map_string(self, location, n):
        m = self.maps.get(location)
        if m is None or n >= len(m["strings"]):
            return ""
        return m["strings"][n]


def load(data_dir):
    """Load a compiled lab data set from ``data_dir``."""
    return Scenario(data_dir)


def _compile(scenario_dir: str, out_dir: str) -> None:
    """Compile the scenario in ``scenario_dir`` into ``out_dir`` (SPEC-05 13)."""
    scen = _load_json(os.path.join(scenario_dir, "scenario.json"))
    items = _load_json(os.path.join(scenario_dir, "items.json"))["items"]
    catalog = {it["id"]: it for it in items}
    ranks = scen["labstr_tables"]["3"]["strings"]
    os.makedirs(out_dir, exist_ok=True)

    game = bytearray()
    map_facts = []
    for loc in scen["locations"]:
        m = _load_json(os.path.join(scenario_dir, loc["file"]))
        mm = _map_from_json(m, loc["size"], catalog, ranks)
        mm["name"] = loc["name"]
        block, tmo, facts = build_map(mm, 0)
        map_facts.append((len(game), tmo, facts, loc))
        game += block

    sg_off = len(game)
    game += _build_savegame(scenario_dir, scen, catalog, ranks)

    shops = _load_json(os.path.join(scenario_dir, "shops.json"))["shops"]
    for sh in shops:
        game += containers.encode_shop_list(_shop_items(sh, catalog), 0)
    _write(out_dir, "GAME1", bytes(game))

    allhtds = _build_allhtds(scenario_dir)
    allpics, portrait_offsets = _build_allpics(scenario_dir)
    _write(out_dir, "ALLHTDS1", allhtds)
    _write(out_dir, "ALLPICS1", allpics)

    sprites, masks = _build_sprites()
    _write(out_dir, "IC0_9.WLF", sprites)
    _write(out_dir, "MASKS.WLF", masks)
    _write(out_dir, "COLORF.FNT", _build_font())
    _write(out_dir, "CURS", _build_cursors())
    _write(out_dir, "TITLE.PIC", _build_title())
    _write(out_dir, "END.CPA", _build_ending())

    _write(out_dir, "LABTABLES.BIN",
           _build_labtables(map_facts, sg_off, len(allhtds), portrait_offsets))
    _write(out_dir, "LABSTR.BIN", _build_labstr(scenario_dir, scen))
    _write(out_dir, "LABSKILL.BIN", _build_labskill(scenario_dir))
    # Location names (SPEC-06 2.1 status line).  The binary formats carry no
    # location name, so the compiler writes them beside the data files.
    _write(out_dir, "LOCATIONS.JSON",
           json.dumps({"locations": [{"location": l["location"], "name": l["name"]}
                                     for l in scen["locations"]]}).encode("utf-8"))

    for src, dst in (("hooks.json", "LABHOOKS.JSON"), ("paragraphs.json", "PARAGRAPHS.JSON")):
        with open(os.path.join(scenario_dir, src), "rb") as fh:
            _write(out_dir, dst, fh.read())


# Late binding of the maps module: some helpers below reference ``maps`` at
# call time, so the import only has to exist by the time the module is loaded.
from . import maps  # noqa: E402,F401


__all__ = ["compile", "build_map", "encode_record", "encode_mapinfo", "encode_mob"]
