"""M2: containers (SPEC-02). Oracle: the fixture set written by
SPEC/reference/fixtures_gen.py at session start, compared with its manifest.
API: SPEC-07 sections 2.3 to 2.5."""

from __future__ import annotations

import hashlib

import pytest

import wl_support as W
from wl_support import call, check_bytes, check_eq, expect_error, fail

pytestmark = pytest.mark.milestone("M2")

C = W.codecs_oracle()
TABLE_KEYS = ["mapOffsets", "tileMapOffsets", "locationMapping", "mapSizes", "sharedLocations",
              "mobSpriteMap", "savegameOffsets", "savegameSize", "shopListRelOffsets", "mapCounts",
              "shopListCounts", "tilesetOffsets", "tilesetSizes", "portraitOffsets1", "portraitOffsets2",
              "portraitIndices1", "portraitIndices2"]
SG_SCALARS = ["viewportX", "viewportY", "currentMembers", "currentParty", "currentMap", "totalMembers",
              "extraGroups", "minute", "hour", "combatScrollSpeed", "serial"]


def sha(b) -> str:
    return hashlib.sha256(bytes(b)).hexdigest()


def _tables(fx):
    t = call("containers.read_tables", fx.path("LABTABLES.BIN"))
    if not isinstance(t, dict):
        fail("containers.read_tables must return a dict, got %s" % type(t).__name__)
    return t


def _savegame(fx):
    off = fx.manifest["savegame"]["offset"]
    sg = call("containers.decode_savegame", fx.read("GAME1"), off)
    if not isinstance(sg, dict):
        fail("containers.decode_savegame must return a dict, got %s" % type(sg).__name__)
    return sg


# ---- LABTABLES.BIN (SPEC-02 section 12.2) -----------------------------------

@pytest.mark.parametrize("key", TABLE_KEYS)
def test_lab_tables_field(fixture_set, key):
    t = _tables(fixture_set)
    if key not in t:
        fail("read_tables result has no key %r" % key)
    check_eq("LABTABLES.BIN field %s" % key, t[key], fixture_set.manifest["tables"][key])


def test_lab_tables_bad_magic(fixture_set, tmp_path):
    b = bytearray(fixture_set.read("LABTABLES.BIN"))
    b[0:8] = b"WLLABTB9"
    p = tmp_path / "LABTABLES.BIN"
    p.write_bytes(bytes(b))
    expect_error("FormatError", "containers.read_tables", str(p), what="magic WLLABTB9")


@pytest.mark.parametrize("loc,want", [(0, [0, 2, 0]), (1, [1, 2, 1]), (2, [2, 2, 2]), (130, [2, 2, 2]),
                                      (252, [2, 2, 2])])
def test_resolve_location(fixture_set, loc, want):
    t = _tables(fixture_set)
    got = call("containers.resolve_location", t, loc)
    check_eq("resolve_location(%d) as (location, disk code, map index)" % loc, got, want)


def test_resolve_location_unused(fixture_set):
    t = _tables(fixture_set)
    expect_error("FormatError", "containers.resolve_location", t, 7, what="location 7 has code 0")


# ---- savegame (SPEC-02 section 4) -------------------------------------------

def test_savegame_groups(fixture_set):
    sg = _savegame(fixture_set)
    check_eq("savegame groups", sg.get("groups"), fixture_set.manifest["savegame"]["groups"])


@pytest.mark.parametrize("key", SG_SCALARS)
def test_savegame_field(fixture_set, key):
    sg = _savegame(fixture_set)
    check_eq("savegame field %s" % key, sg.get(key, "<missing>"), fixture_set.manifest["savegame"][key])


@pytest.mark.parametrize("slot", range(1, 8))
def test_savegame_character(fixture_set, slot):
    sg = _savegame(fixture_set)
    chars = sg.get("characters")
    if not isinstance(chars, list) or len(chars) != 7:
        fail("savegame characters must be a list of 7 records, got %s" % W.short(type(chars).__name__))
    check_eq("savegame character slot %d" % slot, chars[slot - 1],
             fixture_set.manifest["savegame"]["characters"][slot - 1])


def test_savegame_checksum_error(fixture_set):
    g = bytearray(fixture_set.read("GAME1"))
    off = fixture_set.manifest["savegame"]["offset"]
    g[off + 0x200] ^= 0x01
    expect_error("ChecksumError", "containers.decode_savegame", bytes(g), off, what="one payload byte flipped")


def test_savegame_bad_header(fixture_set):
    g = bytearray(fixture_set.read("GAME1"))
    off = fixture_set.manifest["savegame"]["offset"]
    g[off:off + 4] = b"msqX"
    expect_error("FormatError", "containers.decode_savegame", bytes(g), off, what="header msqX")


def test_savegame_encode_round_trip(fixture_set):
    sg = _savegame(fixture_set)
    off = fixture_set.manifest["savegame"]["offset"]
    want = fixture_set.read("GAME1")[off:off + 0x1206]
    got = call("containers.encode_savegame", sg, 0)
    check_bytes("encode_savegame(decode_savegame(block), disk 0)", got, want)


def test_character_round_trip(fixture_set):
    rec = fixture_set.read("GAME1")
    off = fixture_set.manifest["savegame"]["offset"]
    raw = C.rxor_decode_whole(rec, 0x800, off + 4)[0x100:0x200]
    c = call("containers.decode_character", raw)
    check_eq("decode_character of savegame slot 1", c, fixture_set.manifest["savegame"]["characters"][0])
    check_bytes("encode_character(decode_character(record))", call("containers.encode_character", c), raw)


# ---- shop list (SPEC-02 section 5) ------------------------------------------

def _shop(fx):
    s = call("containers.decode_shop_list", fx.read("GAME1"), fx.manifest["shopLists"][0]["offset"])
    if not isinstance(s, dict):
        fail("containers.decode_shop_list must return a dict, got %s" % type(s).__name__)
    return s


def test_shop_list_header(fixture_set):
    check_bytes("shop list header", _shop(fixture_set).get("header"), bytes.fromhex("606060003708F839"))


def test_shop_list_items(fixture_set):
    check_eq("shop list items (94 records)", _shop(fixture_set).get("items"),
             fixture_set.manifest["shopLists"][0]["items"])


def test_shop_list_encode_round_trip(fixture_set):
    off = fixture_set.manifest["shopLists"][0]["offset"]
    want = fixture_set.read("GAME1")[off:off + 766]
    got = call("containers.encode_shop_list", _shop(fixture_set)["items"], 0)
    check_bytes("encode_shop_list(items, disk 0)", got, want)


def test_shop_list_checksum_error(fixture_set):
    g = bytearray(fixture_set.read("GAME1"))
    off = fixture_set.manifest["shopLists"][0]["offset"]
    g[off + 100] ^= 0x10
    expect_error("ChecksumError", "containers.decode_shop_list", bytes(g), off, what="one payload byte flipped")


# ---- Huffman msq blocks (SPEC-02 section 2.2) --------------------------------

def test_msq_block_chain():
    a, b = bytes(range(128)) * 2, bytes(4032)
    blob = C.msqh_encode(a, 0) + C.msqh_encode(b, 1)
    p1 = call("huffman.decode_msq", blob, 0)
    check_bytes("first block payload", p1[0], a)
    check_eq("first block disk byte", p1[1], 0)
    p2 = call("huffman.decode_msq", blob, p1[2])
    check_bytes("second block payload", p2[0], b)
    check_eq("second block disk byte and next offset", [p2[1], p2[2]], [1, len(blob)])


def test_msq_block_signature(fixture_set):
    data = fixture_set.read("END.CPA")
    _, _, nxt = C.msqh_decode(data, 0)
    got = call("huffman.decode_msq", data, nxt, b"\x08\x67\x01")
    check_eq("END.CPA animation block disk byte", got[1], 0)
    expect_error("FormatError", "huffman.decode_msq", data, nxt, what="END.CPA animation block read with signature msq")


def test_msq_block_encode():
    payload = bytes(range(7)) * 10
    enc = call("huffman.encode_msq", payload, 1)
    try:
        out, disk, nxt = C.msqh_decode(bytes(enc), 0)
    except (ValueError, TypeError) as e:
        fail("huffman.encode_msq output rejected by the reference reader: %s" % e)
    check_eq("reference read of encode_msq(payload, disk 1)", [out.hex(), disk, nxt], [payload.hex(), 1, len(enc)])


# ---- tilesets (SPEC-02 section 6) -------------------------------------------

def test_tileset_count(fixture_set):
    ts = call("graphics.read_tilesets", fixture_set.path("ALLHTDS1"))
    check_eq("ALLHTDS1: number of tilesets and tiles", [len(ts), len(ts[0]) if ts else 0], [1, 32])


@pytest.mark.parametrize("tile", [0, 1, 7, 15, 31])
def test_tileset_tile(fixture_set, tile):
    ts = call("graphics.read_tilesets", fixture_set.path("ALLHTDS1"))
    if not ts or len(ts[0]) <= tile:
        fail("ALLHTDS1: tile %d missing" % tile)
    check_eq("ALLHTDS1 tile %d pixels (16 rows of 16)" % tile, ts[0][tile],
             fixture_set.manifest["tilesets"][0]["tiles"][tile])


def test_tileset_all_tiles(fixture_set):
    ts = call("graphics.read_tilesets", fixture_set.path("ALLHTDS1"))
    check_eq("ALLHTDS1 tileset 0", ts[0] if ts else None, fixture_set.manifest["tilesets"][0]["tiles"])


# ---- portraits (SPEC-02 section 7) ------------------------------------------

def _portrait(fx, raw):
    t = _tables(fx)
    off = call("graphics.portrait_offset", t, raw, 1)
    check_eq("portrait_offset(raw id %d, disk 1)" % raw, off, fx.manifest["portraits"][raw]["offset"])
    p = call("graphics.read_portrait", fx.path("ALLPICS1"), off)
    if not isinstance(p, dict):
        fail("graphics.read_portrait must return a dict, got %s" % type(p).__name__)
    return p


@pytest.mark.parametrize("raw", range(4))
def test_portrait_base(fixture_set, raw):
    p = _portrait(fixture_set, raw)
    check_bytes("portrait %d base image (4032 bytes after vertical XOR)" % raw, p.get("base"),
                bytes.fromhex(fixture_set.manifest["portraits"][raw]["base"]))


@pytest.mark.parametrize("raw", range(4))
def test_portrait_scripts(fixture_set, raw):
    p = _portrait(fixture_set, raw)
    check_eq("portrait %d scripts" % raw, p.get("scripts"), fixture_set.manifest["portraits"][raw]["scripts"])


@pytest.mark.parametrize("raw", range(4))
def test_portrait_updates(fixture_set, raw):
    p = _portrait(fixture_set, raw)
    ups = [[[o, bytes(d).hex() if isinstance(d, (bytes, bytearray)) else d] for o, d in u]
           for u in (p.get("updates") or [])]
    check_eq("portrait %d updates" % raw, ups, fixture_set.manifest["portraits"][raw]["updates"])


@pytest.mark.parametrize("raw", range(4))
def test_portrait_animation_loop(fixture_set, raw):
    p = _portrait(fixture_set, raw)
    m = fixture_set.manifest["portraits"][raw]
    base = bytes.fromhex(m["base"])
    upd = [[o, bytes.fromhex(d)] for o, d in m["updates"][0]]
    f1 = call("graphics.apply_portrait_update", base, upd)
    check_eq("portrait %d frame 1 sha256 (base with update 0 applied)" % raw, sha(f1), m["frames"][1]["sha256"])
    f2 = call("graphics.apply_portrait_update", f1, upd)
    check_eq("portrait %d frame 2 returns to the base (L-PT1)" % raw, sha(f2), m["frames"][0]["sha256"])


def test_portrait_invalid_id(fixture_set):
    t = _tables(fixture_set)
    check_eq("portrait_offset(raw id 9, disk 1): index 0x80 means invalid", call("graphics.portrait_offset", t, 9, 1), None)


# ---- sprites, font, cursors, title, ending (SPEC-02 section 8) --------------

def test_sprites_pixels(fixture_set):
    sp = call("graphics.read_sprites", fixture_set.path("IC0_9.WLF"), fixture_set.path("MASKS.WLF"))
    check_eq("IC0_9.WLF sprite pixels", [s.get("pixels") for s in sp], [s["pixels"] for s in fixture_set.manifest["sprites"]])


def test_sprites_masks(fixture_set):
    sp = call("graphics.read_sprites", fixture_set.path("IC0_9.WLF"), fixture_set.path("MASKS.WLF"))
    check_eq("MASKS.WLF transparency (1 = transparent)", [s.get("transparent") for s in sp],
             [s["transparent"] for s in fixture_set.manifest["sprites"]])


def test_sprites_count_mismatch(fixture_set, tmp_path):
    p = tmp_path / "MASKS.WLF"
    p.write_bytes(fixture_set.read("MASKS.WLF")[:-32])
    expect_error("FormatError", "graphics.read_sprites", fixture_set.path("IC0_9.WLF"), str(p),
                 what="10 sprites, 9 masks")


def test_font_glyphs(fixture_set):
    check_eq("COLORF.FNT glyph pixels", call("graphics.read_font", fixture_set.path("COLORF.FNT")),
             fixture_set.manifest["font"])


@pytest.mark.parametrize("code,want", [(0x20, 0), (0x21, 1), (0x3F, 31), (0x40, 0), (0x7A, 0), (0x0D, 0)])
def test_font_glyph_index(code, want):
    check_eq("glyph_index(0x%02X, 32 glyphs) (L-FN1)" % code, call("graphics.glyph_index", code, 32), want)


def test_cursors_pixels(fixture_set):
    cu = call("graphics.read_cursors", fixture_set.path("CURS"))
    check_eq("CURS pixels", [c.get("pixels") for c in cu], [c["pixels"] for c in fixture_set.manifest["cursors"]])


def test_cursors_visible(fixture_set):
    cu = call("graphics.read_cursors", fixture_set.path("CURS"))
    check_eq("CURS blue-plane mask (1 = visible)", [c.get("visible") for c in cu],
             [c["visible"] for c in fixture_set.manifest["cursors"]])


def test_title(fixture_set):
    t = call("graphics.read_title", fixture_set.path("TITLE.PIC"))
    if not isinstance(t, (bytes, bytearray)) or len(t) != 18432:
        fail("graphics.read_title must return 18432 bytes, got %s" % W.short(t, 60))
    check_eq("TITLE.PIC first pixel row", W.unpack4(bytes(t[:144]), 288)[0], fixture_set.manifest["title"]["firstRow"])
    check_eq("TITLE.PIC sha256 of the decoded image", sha(t), fixture_set.manifest["title"]["sha256"])


def test_ending_base(fixture_set):
    e = call("graphics.read_ending", fixture_set.path("END.CPA"))
    check_eq("END.CPA base image sha256", sha(e.get("base", b"")), fixture_set.manifest["ending"]["baseSha256"])


def test_ending_updates(fixture_set):
    e = call("graphics.read_ending", fixture_set.path("END.CPA"))
    ups = [[d, [[o, bytes(p).hex() if isinstance(p, (bytes, bytearray)) else p] for o, p in ps]]
           for d, ps in (e.get("updates") or [])]
    check_eq("END.CPA updates", ups, fixture_set.manifest["ending"]["updates"])


def test_ending_frames(fixture_set):
    e = call("graphics.read_ending", fixture_set.path("END.CPA"))
    img = bytes(e.get("base", b""))
    shas = [sha(img)]
    for _, ps in fixture_set.manifest["ending"]["updates"]:
        img = bytes(call("graphics.apply_ending_update", img, [[o, bytes.fromhex(p)] for o, p in ps]))
        shas.append(sha(img))
    check_eq("END.CPA frame sha256 after each update", shas, fixture_set.manifest["ending"]["frameSha256"])


# ---- string tables (SPEC-02 section 9, section 12.3) -------------------------

ST = {"ST-%d" % (i + 1): (case, enc) for i, (case, enc) in enumerate(zip(C.STR_TABLE_CASES, C._STR_TABLE_FROZEN))}


@pytest.mark.parametrize("vid", sorted(ST))
def test_string_table_decode(vid):
    case, enc = ST[vid]
    want = list(case) + [b""] * ((-len(case)) % 4)
    got = call("strings.decode_table", bytes.fromhex(enc.replace(" ", "")))
    check_eq("%s decoded strings" % vid, [bytes(x) for x in got] if isinstance(got, list) else got, want)


@pytest.mark.parametrize("vid", sorted(ST))
def test_string_table_encode(vid):
    case, _ = ST[vid]
    enc = call("strings.encode_table", C.STR_DICT, list(case))
    want = list(case) + [b""] * ((-len(case)) % 4)
    try:
        back = C.strtab_decode(bytes(enc))
    except (ValueError, IndexError, TypeError) as e:
        fail("%s: engine table rejected by the reference reader: %s" % (vid, e))
    check_eq("%s: reference decode of the engine encoding" % vid, back, want)


def test_string_table_bad_last_pointer():
    enc = bytearray(bytes.fromhex(C._STR_TABLE_FROZEN[2].replace(" ", "")))
    # ST-3 has two group pointers; point the second one past the end of the data.
    enc[62:64] = (0x7FF0).to_bytes(2, "little")
    got = call("strings.decode_table", bytes(enc))
    if not isinstance(got, list):
        fail("strings.decode_table must return a list, got %s" % type(got).__name__)
    check_eq("ST-3 with an out-of-range last pointer: the first four strings",
             [bytes(x) for x in got[:4]], [b"a\x0ab\x0ac\x0a", b"Read 12.\r", b"one", b"two"])


def test_labstr_tables(fixture_set):
    got = call("strings.read_labstr", fixture_set.path("LABSTR.BIN"))
    check_eq("LABSTR.BIN tables", got, fixture_set.manifest["stringTables"])


# ---- second fixture set, seed 20261022 (SPEC-07 section 5) -------------------

def test_alt_seed_tables(fixture_set_alt):
    check_eq("LABTABLES.BIN, fixture seed 20261022", _tables(fixture_set_alt), fixture_set_alt.manifest["tables"])


def test_alt_seed_savegame(fixture_set_alt):
    want = {k: v for k, v in fixture_set_alt.manifest["savegame"].items() if k not in ("offset", "tailAllZero")}
    sg = _savegame(fixture_set_alt)
    check_eq("savegame, fixture seed 20261022", {k: sg.get(k, "<missing>") for k in want}, want)


def test_alt_seed_shop_list(fixture_set_alt):
    check_eq("shop list items, fixture seed 20261022", _shop(fixture_set_alt).get("items"),
             fixture_set_alt.manifest["shopLists"][0]["items"])


def test_alt_seed_tiles(fixture_set_alt):
    ts = call("graphics.read_tilesets", fixture_set_alt.path("ALLHTDS1"))
    check_eq("ALLHTDS1 tileset 0, fixture seed 20261022", ts[0] if ts else None,
             fixture_set_alt.manifest["tilesets"][0]["tiles"])


def test_alt_seed_portraits(fixture_set_alt):
    for raw in range(4):
        p = _portrait(fixture_set_alt, raw)
        check_bytes("portrait %d base, fixture seed 20261022" % raw, p.get("base"),
                    bytes.fromhex(fixture_set_alt.manifest["portraits"][raw]["base"]))
