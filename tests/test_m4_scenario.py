"""M4: scenario compiler (SPEC-05 section 13). The engine compiles
SPEC/scenario into data files; the tests read them back through the engine's
own loaders and through the reference readers of SPEC/reference, and compare
both with the scenario JSON. API: SPEC-07 sections 2.4 to 2.8."""

from __future__ import annotations

import json

import pytest

import wl_support as W
from wl_support import call, check_eq, fail

pytestmark = pytest.mark.milestone("M4")

LOCS = [0, 1, 2, 3]
MAP_FIELDS = ["size", "info", "cells.image", "cells.actionClass", "cells.action", "actions", "npcs", "mobs",
              "strings"]
REQUIRED_FILES = ["GAME1", "LABTABLES.BIN", "LABSTR.BIN", "LABSKILL.BIN", "LABHOOKS.JSON", "PARAGRAPHS.JSON",
                  "ALLHTDS1", "ALLPICS1", "IC0_9.WLF", "MASKS.WLF", "COLORF.FNT", "CURS", "TITLE.PIC", "END.CPA"]


def _get(d, dotted, what):
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            fail("%s has no field %r" % (what, dotted))
        d = d[k]
    return d


@pytest.fixture(scope="module")
def loaded(compiled):
    return {}


def _map(compiled, loaded, loc):
    if loc not in loaded:
        dd = compiled.need()
        loaded[loc] = call("maps.load_map", str(dd), loc)
    m = loaded[loc]
    if not isinstance(m, dict):
        fail("maps.load_map must return a dict, got %s" % type(m).__name__)
    return m


def test_compiled_file_set(compiled):
    dd = compiled.need()
    missing = [f for f in REQUIRED_FILES if not (dd / f).is_file()]
    if missing:
        fail("compile output is missing %s (SPEC-05 section 13, SPEC-02 section 12.1)" % ", ".join(missing))


# ---- maps through the engine's own loaders ----------------------------------

@pytest.mark.parametrize("field", MAP_FIELDS)
@pytest.mark.parametrize("loc", LOCS)
def test_map_round_trip(compiled, loaded, expected_view, loc, field):
    m = _map(compiled, loaded, loc)
    check_eq("location %d %s (engine loader vs map JSON)" % (loc, field), _get(m, field, "load_map(%d)" % loc),
             _get(expected_view["maps"][str(loc)], field, "expected"))


@pytest.mark.parametrize("loc", LOCS)
def test_map_reference_reader(oracle_view, loc):
    """The compiled block must also decode with the SPEC-03 reference reader."""
    got = oracle_view.oracle("map%d" % loc)
    want = oracle_view.expected("maps")[str(loc)]
    for k in ("cells", "actions", "npcs", "mobs", "strings", "info"):
        check_eq("location %d %s (reference reader vs map JSON)" % (loc, k), got[k], want[k])
    check_eq("location %d encrypted prefix ends at stringsOffset (L-EN2)" % loc,
             [got["encryptedPrefixLength"], got["wllibPrefixLength"]],
             [got["centralDirectory"]["stringsOffset"]] * 2)


# ---- tables, savegame, shops ------------------------------------------------

def test_tables_values(compiled):
    t = call("containers.read_tables", str(compiled.need() / "LABTABLES.BIN"))
    got = {k: t.get(k) for k in ("mapCounts", "shopListCounts", "savegameSize")}
    got["locationMapping"] = (t.get("locationMapping") or [])[:6]
    got["mapSizes"] = (t.get("mapSizes") or [])[:6]
    got["savegameOffsets[1]"] = (t.get("savegameOffsets") or [None, None])[1]
    want = {"mapCounts": [4, 0], "shopListCounts": [3, 0], "savegameSize": 0x1206,
            "locationMapping": [0x80, 0x81, 0x82, 0x83, 0, 0], "mapSizes": [64, 32, 32, 32, 0, 0],
            "savegameOffsets[1]": 0xFFFFFFFF}
    check_eq("LABTABLES.BIN of the compiled scenario", got, want)


def test_tables_reference_reader(oracle_view):
    t = oracle_view.oracle("tables")
    files = oracle_view.oracle("files")
    end = t["savegameOffsets"][0] + t["savegameSize"] + 3 * 766
    check_eq("GAME1 length = savegame offset + 0x1206 + 3 shop lists (L-TB3)", files.get("GAME1"), end)
    check_eq("map offsets strictly increasing, savegame after the last map",
             [t["mapOffsets"][i] < t["mapOffsets"][i + 1] for i in range(3)] + [t["mapOffsets"][3] < t["savegameOffsets"][0]],
             [True] * 4)


def _savegame(compiled):
    dd = compiled.need()
    t = call("containers.read_tables", str(dd / "LABTABLES.BIN"))
    sg = call("containers.decode_savegame", (dd / "GAME1").read_bytes(), t["savegameOffsets"][0])
    if not isinstance(sg, dict):
        fail("containers.decode_savegame must return a dict, got %s" % type(sg).__name__)
    return sg


def test_savegame_header_fields(compiled, expected_view):
    sg = _savegame(compiled)
    want = {k: v for k, v in expected_view["savegame"].items() if k != "characters"}
    check_eq("new-game savegame fields (SPEC-04 LR-55)", {k: sg.get(k) for k in want}, want)


@pytest.mark.parametrize("slot", range(1, 8))
def test_savegame_party(compiled, expected_view, slot):
    sg = _savegame(compiled)
    chars = sg.get("characters") or []
    if len(chars) != 7:
        fail("savegame characters must be a list of 7 records, got %d" % len(chars))
    check_eq("new-game savegame character slot %d (party.json, LR-8, LR-55)" % slot, chars[slot - 1],
             expected_view["savegame"]["characters"][slot - 1])


def test_savegame_reference_reader(oracle_view):
    got = oracle_view.oracle("savegame")
    want = oracle_view.expected("savegame")
    check_eq("savegame through the reference reader", {k: got[k] for k in want}, want)
    check_eq("savegame reserved tail is zero (L-SG2)", got["tailAllZero"], True)


@pytest.mark.parametrize("n", [0, 1, 2])
def test_shop_list(compiled, expected_view, n):
    dd = compiled.need()
    t = call("containers.read_tables", str(dd / "LABTABLES.BIN"))
    off = t["savegameOffsets"][0] + t["savegameSize"] + t["shopListRelOffsets"][n]
    s = call("containers.decode_shop_list", (dd / "GAME1").read_bytes(), off)
    want = expected_view["shops"][n]
    check_eq("shop list %d header" % n, bytes(s.get("header", b"")).hex(), want["header"])
    check_eq("shop list %d records" % n, s.get("items"), want["items"])


def test_shop_lists_reference_reader(oracle_view):
    want = oracle_view.expected("shops")
    for n in range(3):
        got = oracle_view.oracle("shop%d" % n)
        check_eq("shop list %d through the reference reader" % n, got, want[n])


# ---- strings, skills, hooks, paragraphs --------------------------------------

@pytest.mark.parametrize("table", range(6))
def test_labstr_table(compiled, expected_view, table):
    got = call("strings.read_labstr", str(compiled.need() / "LABSTR.BIN"))
    if not isinstance(got, list) or len(got) != 6:
        fail("LABSTR.BIN must hold 6 tables (SPEC-05 section 11), got %s" % W.short(len(got) if isinstance(got, list) else got))
    check_eq("LABSTR.BIN table %d" % table, got[table], expected_view["labstr"][table])


def test_labstr_reference_reader(oracle_view):
    check_eq("LABSTR.BIN through the reference reader", oracle_view.oracle("labstr"), oracle_view.expected("labstr"))


def test_labskill_bytes(oracle_view):
    raw = oracle_view.oracle("labskill")
    want = [b for pair in oracle_view.expected("labskill") for b in pair]
    check_eq("LABSKILL.BIN bytes (SPEC-05 section 8)", raw, want)


def test_labskill_engine_reader(compiled, expected_view):
    got = call("rules.read_skill_table", str(compiled.need() / "LABSKILL.BIN"))
    want = [[b0 >> 3, b0 & 7, b1] for b0, b1 in expected_view["labskill"]]
    check_eq("read_skill_table: (minimum IQ, cost, attribute offset) per entry", got, want)


def test_hooks_file(compiled, expected_view):
    p = compiled.need() / "LABHOOKS.JSON"
    try:
        got = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fail("LABHOOKS.JSON is not readable JSON: %s" % e)
    check_eq("LABHOOKS.JSON (copy of hooks.json)", got, expected_view["hooks"])


def test_paragraphs_file(compiled, expected_view):
    p = compiled.need() / "PARAGRAPHS.JSON"
    try:
        got = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fail("PARAGRAPHS.JSON is not readable JSON: %s" % e)
    check_eq("PARAGRAPHS.JSON (copy of paragraphs.json)", got, expected_view["paragraphs"])


# ---- graphics files -----------------------------------------------------------

def test_tileset(compiled, oracle_view):
    ts = call("graphics.read_tilesets", str(compiled.need() / "ALLHTDS1"))
    ref = oracle_view.oracle("tilesets")["tilesets"]
    check_eq("ALLHTDS1: tilesets and tile counts", [len(x) for x in ts], [32])
    check_eq("ALLHTDS1 tiles (engine reader vs reference reader)", ts, ref)


def test_tileset_tables(oracle_view):
    t = oracle_view.oracle("tables")
    size = oracle_view.oracle("tilesets")["size"]
    check_eq("tilesetOffsets[0] and tilesetSizes[0] for one tileset", [t["tilesetOffsets"][0], t["tilesetSizes"][0]],
             [0, size])


def test_portrait_index(oracle_view):
    t = oracle_view.oracle("tables")
    idx = t["portraitIndices1"]
    check_eq("raw portrait ids with a portrait (SPEC-05 section 4, L-TB2)",
             [r for r in range(80) if idx[r] != 0x80], [1, 2, 3, 4])


@pytest.mark.parametrize("raw", [1, 2, 3, 4])
def test_portrait(compiled, oracle_view, raw):
    dd = compiled.need()
    t = call("containers.read_tables", str(dd / "LABTABLES.BIN"))
    off = call("graphics.portrait_offset", t, raw, 1)
    p = call("graphics.read_portrait", str(dd / "ALLPICS1"), off)
    ref = oracle_view.oracle("portraits").get(str(raw))
    if ref is None:
        fail("reference reader found no portrait for raw id %d" % raw)
    check_eq("portrait %d base (engine vs reference reader)" % raw, bytes(p.get("base", b"")).hex(), ref["base"])
    check_eq("portrait %d script (placeholder: (20, 0), (20, 0))" % raw, p.get("scripts"), [[[20, 0], [20, 0]]])
    ups = [[[o, bytes(d).hex()] for o, d in u] for u in (p.get("updates") or [])]
    check_eq("portrait %d update (placeholder: 8 bytes at 2000 XOR FF)" % raw, ups, [[[2000, "ff" * 8]]])


def test_sprites(compiled):
    dd = compiled.need()
    sp = call("graphics.read_sprites", str(dd / "IC0_9.WLF"), str(dd / "MASKS.WLF"))
    check_eq("IC0_9.WLF and MASKS.WLF sprite count (SPEC-02 12.1)", len(sp), 10)


def test_font_cursors_title_ending(compiled):
    dd = compiled.need()
    f = call("graphics.read_font", str(dd / "COLORF.FNT"))
    if not f:
        fail("COLORF.FNT holds no glyphs")
    cu = call("graphics.read_cursors", str(dd / "CURS"))
    if not cu:
        fail("CURS holds no cursors")
    t = call("graphics.read_title", str(dd / "TITLE.PIC"))
    check_eq("TITLE.PIC decoded size", len(t), 18432)
    e = call("graphics.read_ending", str(dd / "END.CPA"))
    check_eq("END.CPA base image size", len(e.get("base", b"")), 18432)
