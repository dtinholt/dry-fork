"""M3: maps (SPEC-03). Oracle: the fixture maps and manifest from
SPEC/reference/fixtures_gen.py; lab-rule semantics from SPEC-03 section 9.
API: SPEC-07 section 2.6."""

from __future__ import annotations

import copy

import pytest

import wl_support as W
from wl_support import call, check_eq, expect_error, fail

pytestmark = pytest.mark.milestone("M3")

C = W.codecs_oracle()
FIELDS = ["size", "bodySize", "encryptedPrefixLength", "centralDirectory", "info", "cells.actionClass",
          "cells.action", "cells.image", "actions", "npcs", "mobs", "strings"]


def _get(d, dotted):
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            fail("decoded map has no field %r" % dotted)
        d = d[k]
    return d


def _decode(fx, i):
    m = fx.manifest["maps"][i]
    got = call("maps.decode_map", fx.read("GAME1"), m["offset"], m["size"], m["tileMapOffset"])
    if not isinstance(got, dict):
        fail("maps.decode_map must return a dict, got %s" % type(got).__name__)
    return got


def _want(fx, i, dotted):
    d = fx.manifest["maps"][i]
    for k in dotted.split("."):
        d = d[k]
    return d


# ---- decoding (SPEC-03 sections 3 to 7) -------------------------------------

@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("i", [0, 1, 2])
def test_decode_map_field(fixture_set, i, field):
    got = _decode(fixture_set, i)
    check_eq("map %d %s" % (i, field), _get(got, field), _want(fixture_set, i, field))


@pytest.mark.parametrize("loc", [0, 1, 2])
def test_load_map_through_tables(fixture_set, loc):
    got = call("maps.load_map", str(fixture_set.dir), loc)
    if not isinstance(got, dict):
        fail("maps.load_map must return a dict, got %s" % type(got).__name__)
    want = {k: v for k, v in fixture_set.manifest["maps"][loc].items()
            if k in ("size", "bodySize", "encryptedPrefixLength", "centralDirectory", "info", "cells",
                     "actions", "npcs", "mobs", "strings")}
    check_eq("load_map(location %d)" % loc, {k: got.get(k) for k in want}, want)


def test_decode_map_bad_header(fixture_set):
    m = fixture_set.manifest["maps"][1]
    g = bytearray(fixture_set.read("GAME1"))
    g[m["offset"]:m["offset"] + 4] = b"xyz0"
    expect_error("FormatError", "maps.decode_map", bytes(g), m["offset"], m["size"], m["tileMapOffset"],
                 what="block header xyz0")


def test_decode_map_wrong_size(fixture_set):
    m = fixture_set.manifest["maps"][1]
    expect_error("FormatError", "maps.decode_map", fixture_set.read("GAME1"), m["offset"], 64, m["tileMapOffset"],
                 what="32 x 32 map read as 64 x 64")


def test_decode_map_prefix_mismatch(fixture_set):
    """L-EN2: in lab data the encrypted prefix must end exactly at stringsOffset."""
    m = fixture_set.manifest["maps"][1]
    g = fixture_set.read("GAME1")
    off, tmo = m["offset"], m["tileMapOffset"]
    body, plen = C.rxor_decode_prefix(g, tmo - 7, off + 4)
    so = m["centralDirectory"]["stringsOffset"]
    cd = 3 * 32 * 32 // 2
    body = bytearray(body)
    body[cd:cd + 2] = (so + 8).to_bytes(2, "little")
    prefix = bytes(body[:so])
    if not C.rxor_prefix_is_unambiguous(prefix):
        fail("test setup: crafted prefix is ambiguous (report to the spec owner)")
    block = g[off:off + 4] + C.rxor_encode(prefix) + bytes(body[so:]) + g[off + tmo - 1:]
    expect_error("FormatError", "maps.decode_map", block, 0, 32, tmo,
                 what="stringsOffset moved 8 bytes past the end of the encrypted prefix")


# ---- lab-rule semantics on decoded maps (SPEC-03 section 9) -----------------

RECORD_CELLS = {0: [(5, 5, 4), (6, 5, 4), (10, 10, 10), (12, 10, 6), (14, 10, 5), (16, 10, 1), (18, 10, 3),
                    (20, 10, 11)],
                1: [(10, 21, 10), (20, 20, 10), (5, 8, 10)],
                2: [(32, 33, 10), (40, 40, 3), (50, 12, 3), (20, 50, 5)]}
RC = [(i, x, y, c) for i, cells in RECORD_CELLS.items() for (x, y, c) in cells]


@pytest.mark.parametrize("i,x,y,c", RC, ids=["map%d-%d,%d" % (i, x, y) for i, x, y, _ in RC])
def test_record_at(fixture_set, i, x, y, c):
    m = copy.deepcopy(fixture_set.manifest["maps"][i])
    a = m["cells"]["action"][y][x]
    got = call("maps.record_at", m, x, y)
    check_eq("map %d record_at(%d, %d) (class %d, action byte %d, L-AC2)" % (i, x, y, c, a), got,
             m["actions"][str(c)][a])


def test_record_at_no_record(fixture_set):
    m = copy.deepcopy(fixture_set.manifest["maps"][0])
    check_eq("map 0 record_at(0, 0): blocked border, action byte 0 (L-AC3)", call("maps.record_at", m, 0, 0), None)
    check_eq("map 0 record_at(3, 3): walkable, action byte 0", call("maps.record_at", m, 3, 3), None)


def test_record_at_action_out_of_range(fixture_set):
    m = copy.deepcopy(fixture_set.manifest["maps"][0])
    m["cells"]["action"][10][16] = 9
    expect_error("FormatError", "maps.record_at", m, 16, 10, what="class 1 cell with action byte 9 (L-AC5)")


def test_record_at_null_pointer(fixture_set):
    m = copy.deepcopy(fixture_set.manifest["maps"][0])
    m["cells"]["action"][10][16] = 0
    expect_error("FormatError", "maps.record_at", m, 16, 10, what="class 1 cell with action byte 0 (L-AC5)")


PASS = [(0, 0, False, "blocked border"), (-1, 5, False, "x = -1"), (32, 5, False, "x = 32"),
        (5, 32, False, "y = 32"), (3, 3, True, "walkable"), (5, 5, True, "open door"),
        (6, 5, False, "locked door"), (10, 10, True, "transition"), (12, 10, True, "shop"),
        (14, 10, True, "loot"), (16, 10, True, "paragraph trigger"), (18, 10, True, "encounter"),
        (20, 10, False, "blocked with message")]


@pytest.mark.parametrize("x,y,want,what", PASS, ids=[p[3].replace(" ", "-") for p in PASS])
def test_is_passable(fixture_set, x, y, want, what):
    m = copy.deepcopy(fixture_set.manifest["maps"][0])
    check_eq("map 0 is_passable(%d, %d) (%s; SPEC-03 9.1, 9.6, L-MV1, L-MV2)" % (x, y, what),
             call("maps.is_passable", m, x, y), want)


def test_is_passable_reserved_class(fixture_set):
    m = copy.deepcopy(fixture_set.manifest["maps"][0])
    m["cells"]["actionClass"][3][3] = 7
    check_eq("map 0 is_passable(3, 3) with reserved class 7 (L-AC1)", call("maps.is_passable", m, 3, 3), True)


TAILS = [({"newClass": 0, "newAction": 0}, [0, 0]), ({"newClass": 255, "newAction": 0}, None),
         ({"newClass": 4, "newAction": 1}, [4, 1]), ({"newClass": 200, "newAction": 0}, None),
         ({"newClass": 15, "newAction": 3}, [15, 3])]


@pytest.mark.parametrize("tail,want", TAILS, ids=["tail-%d" % t["newClass"] for t, _ in TAILS])
def test_apply_tail(tail, want):
    rec = dict({"message": 0}, **tail)
    check_eq("apply_tail(newClass %d, newAction %d) (L-TL1)" % (tail["newClass"], tail["newAction"]),
             call("maps.apply_tail", rec), want)


TRANS = [(0, 10, 10, [1, 10, 20], "absolute"), (1, 10, 21, [0, 11, 10], "absolute back"),
         (1, 20, 20, [2, 32, 32], "shared location 130"), (1, 5, 8, [1, 7, 8], "relative +2,0"),
         (2, 32, 33, [0, 11, 12], "previous location")]


@pytest.mark.parametrize("i,x,y,want,what", TRANS, ids=[t[4].replace(" ", "-") for t in TRANS])
def test_resolve_transition(fixture_set, i, x, y, want, what):
    t = call("containers.read_tables", fixture_set.path("LABTABLES.BIN"))
    m = fixture_set.manifest["maps"][i]
    rec = copy.deepcopy(m["actions"]["10"][m["cells"]["action"][y][x]])
    got = call("maps.resolve_transition", t, rec, x, y, [0, 11, 12])
    check_eq("map %d transition at (%d, %d), %s, previous (0, 11, 12) (L-TR2, L-TR3)" % (i, x, y, what), got, want)


def test_resolve_transition_relative_negative(fixture_set):
    t = call("containers.read_tables", fixture_set.path("LABTABLES.BIN"))
    rec = {"relative": True, "confirm": False, "message": 0, "x": -3, "y": 2, "location": 1,
           "newClass": 255, "newAction": 0}
    check_eq("relative transition -3,+2 from (5, 8) (L-TR3, signed bytes)",
             call("maps.resolve_transition", t, rec, 5, 8, [0, 0, 0]), [1, 2, 10])


def test_resolve_transition_unused_location(fixture_set):
    t = call("containers.read_tables", fixture_set.path("LABTABLES.BIN"))
    rec = {"relative": False, "confirm": False, "message": 0, "x": 1, "y": 1, "location": 7,
           "newClass": 255, "newAction": 0}
    expect_error("FormatError", "maps.resolve_transition", t, rec, 3, 3, [0, 0, 0], what="location 7 has code 0 (L-TR2)")


def test_resolve_transition_outside_target(fixture_set):
    t = call("containers.read_tables", fixture_set.path("LABTABLES.BIN"))
    rec = {"relative": False, "confirm": False, "message": 0, "x": 40, "y": 1, "location": 1,
           "newClass": 255, "newAction": 0}
    expect_error("FormatError", "maps.resolve_transition", t, rec, 3, 3, [0, 0, 0],
                 what="target (40, 1) outside the 32 x 32 map (L-TR5)")


@pytest.mark.parametrize("x,y,want", [(3, 3, None), (-1, 0, 10), (5, 40, 10), (0, 0, 10)])
def test_image_at(fixture_set, x, y, want):
    m = copy.deepcopy(fixture_set.manifest["maps"][0])
    if want is None:
        want = m["cells"]["image"][y][x]
    check_eq("map 0 image_at(%d, %d) (SPEC-03 7, L-MI5)" % (x, y), call("maps.image_at", m, x, y), want)


# ---- second fixture set, seed 20261022 (SPEC-07 section 5) -------------------

@pytest.mark.parametrize("loc", [0, 1, 2])
def test_alt_seed_map(fixture_set_alt, loc):
    got = call("maps.load_map", str(fixture_set_alt.dir), loc)
    if not isinstance(got, dict):
        fail("maps.load_map must return a dict, got %s" % type(got).__name__)
    want = {k: v for k, v in fixture_set_alt.manifest["maps"][loc].items()
            if k in ("size", "bodySize", "encryptedPrefixLength", "centralDirectory", "info", "cells",
                     "actions", "npcs", "mobs", "strings")}
    check_eq("load_map(location %d), fixture seed 20261022" % loc, {k: got.get(k) for k in want}, want)
