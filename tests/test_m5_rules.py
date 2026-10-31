"""M5: game rules (SPEC-04, lab rules v1). Table-driven cases whose expected
values come from the SPEC-04 formulas (restated independently in wl_support),
the worked examples of SPEC-04, and SPEC/scenario/rng-vectors.json; plus short
headless runs on the engine's compiled Dry Fork data, checked against values
derived from SPEC-04 and SPEC-05. API: SPEC-07 sections 2.7 to 2.9."""

from __future__ import annotations

import copy

import pytest

import wl_combat_ref as CR
import wl_support as W
from wl_support import (RefRng, call, check_bytes, check_eq, expect_error, fail, ref_ac, ref_advance_clock,
                        ref_buy_price, ref_check_need, ref_damage_member, ref_flee_need, ref_jam_chance,
                        ref_level_after, ref_max_hp, ref_melee_need, ref_monster_hp, ref_monster_need, ref_pay,
                        ref_ranged_need, ref_sell_price, ref_skill_check, ref_speed_order, ref_xp_threshold)

pytestmark = pytest.mark.milestone("M5")

VECTORS = W.load_json(W.SCENARIO / "rng-vectors.json")["vectors"]
VSEEDS = [v["seed"] for v in VECTORS]
C = W.codecs_oracle()


def table(argnames, cases, ids=None):
    """Run one test function over a table of cases inside a single test.

    Each SPEC-04 rule is one test; its table rows are checked in order and the
    failure message names the first failing row only."""
    names = [n.strip() for n in argnames.split(",")]

    def deco(fn):
        def wrapper():
            for case in cases:
                fn(**dict(zip(names, case if len(names) > 1 else (case,))))
        wrapper.__name__ = fn.__name__
        wrapper.__qualname__ = fn.__qualname__
        wrapper.__doc__ = fn.__doc__
        wrapper.__module__ = fn.__module__
        return wrapper
    return deco


def _rng(seed):
    r = call("rules.Rng", seed)
    return r


def _state(r):
    try:
        return r.state
    except NotImplementedError:
        fail("wlengine.rules.Rng.state: not implemented")
    except Exception as e:  # noqa: BLE001
        fail("wlengine.rules.Rng.state raised %s: %s" % (type(e).__name__, e))


def _m(obj, name, *args):
    fn = getattr(obj, name, None)
    if fn is None:
        fail("wlengine.rules.Rng has no method %r (SPEC-07 API)" % name)
    try:
        return fn(*args)
    except NotImplementedError:
        fail("wlengine.rules.Rng.%s: not implemented" % name)
    except Exception as e:  # noqa: BLE001
        fail("wlengine.rules.Rng.%s%r raised %s: %s" % (name, args, type(e).__name__, e))


# ---- LR-1, LR-2: generator --------------------------------------------------

@table("v", VECTORS, ids=["seed-%d" % s for s in VSEEDS])
def test_rng_seeding(v):
    check_eq("Rng(%d).state after seeding" % v["seed"], _state(_rng(v["seed"])), v["state_after_seeding"])


@table("v", VECTORS, ids=["seed-%d" % s for s in VSEEDS])
def test_rng_next(v):
    r = _rng(v["seed"])
    for i, want in enumerate(v["next_u32"]):
        check_eq("Rng(%d) next() call %d" % (v["seed"], i + 1), _m(r, "next"), want)


@table("v", VECTORS, ids=["seed-%d" % s for s in VSEEDS])
def test_rng_roll(v):
    r = _rng(v["seed"])
    for i, want in enumerate(v["roll_100"]):
        check_eq("Rng(%d) roll(100) call %d" % (v["seed"], i + 1), _m(r, "roll", 100), want)


@table("v", VECTORS, ids=["seed-%d" % s for s in VSEEDS])
def test_rng_d100(v):
    r = _rng(v["seed"])
    for i, want in enumerate(v["roll_100"][:5]):
        check_eq("Rng(%d) d100() call %d" % (v["seed"], i + 1), _m(r, "d100"), want)


@table("v", VECTORS, ids=["seed-%d" % s for s in VSEEDS])
def test_rng_dice(v):
    r = _rng(v["seed"])
    for i, want in enumerate(v["dice_2d6"]):
        check_eq("Rng(%d) dice(2, 6) call %d" % (v["seed"], i + 1), _m(r, "dice", 2, 6), want)


@table("v", VECTORS, ids=["seed-%d" % s for s in VSEEDS])
def test_rng_rnd(v):
    r = _rng(v["seed"])
    for n, want in zip((0, 1, 2, 12, 14, 255), v["rnd_of_0_1_2_12_14_255"]):
        check_eq("Rng(%d) rnd(%d) in the sequence rnd(0), rnd(1), rnd(2), rnd(12), rnd(14), rnd(255)"
                 % (v["seed"], n), _m(r, "rnd", n), want)


def test_rng_no_draw_cases():
    r = _rng(4242)
    before = _state(r)
    got = [_m(r, "rnd", 0), _m(r, "rnd", 1), _m(r, "dice", 0, 6)]
    check_eq("rnd(0), rnd(1), dice(0, 6)", got, [0, 1, 0])
    check_eq("generator state after draws that make no call (LR-2)", _state(r), before)


# ---- characters (LR-5 to LR-10) ---------------------------------------------

@table("seed", [20261021, 1, 7, 99])
def test_roll_attributes(seed):
    ref = RefRng(seed)
    want = [8 + ref.roll(10) for _ in range(6)]
    r = _rng(seed)
    check_eq("roll_attributes with seed %d (LR-7: STR IQ LCK SPD AGL CHA)" % seed, call("rules.roll_attributes", r), want)
    check_eq("generator state after roll_attributes with seed %d" % seed, _state(r), ref.state)


MAXHP = [(14, 1), (16, 1), (11, 1), (12, 1), (13, 2), (12, 2), (10, 2), (17, 1), (14, 2), (16, 2), (18, 5), (3, 3)]


@table("st,lvl", MAXHP, ids=["STR%d-L%d" % c for c in MAXHP])
def test_max_hp(st, lvl):
    check_eq("max_hp(strength=%d, level=%d) (LR-8, LR-46)" % (st, lvl), call("rules.max_hp", st, lvl), ref_max_hp(st, lvl))


ACS = [(14, 1, 0), (12, 1, 0), (15, 0, 0), (13, 0, 0), (14, 3, 0), (16, 0, 2), (4, 0, 0), (19, 3, 3)]


@table("agl,bonus,ev", ACS, ids=["AGL%d-A%d-E%d" % c for c in ACS])
def test_armour_class(agl, bonus, ev):
    check_eq("armour_class(agility=%d, armour_bonus=%d, evasion_level=%d) (LR-8)" % (agl, bonus, ev),
             call("rules.armour_class", agl, bonus, ev), ref_ac(agl, bonus, ev))


@table("lck", [3, 11, 18])
def test_starting_money(lck):
    check_eq("starting_money(luck=%d) (LR-9)" % lck, call("rules.starting_money", lck), 50 + 5 * lck)


def test_skill_table_reader(tmp_path):
    raw = bytes([0, 0]) + bytes(b for i in range(1, 36) for b in (((3 + i % 9) << 3) | (1 + i % 2), 0x0E + i % 7))
    p = tmp_path / "LABSKILL.BIN"
    p.write_bytes(raw)
    want = [[raw[2 * i] >> 3, raw[2 * i] & 7, raw[2 * i + 1]] for i in range(36)]
    check_eq("read_skill_table of a 72-byte table (LR-6)", call("rules.read_skill_table", str(p)), want)


# ---- checks (LR-13, LR-14) --------------------------------------------------

NEEDS = [(2, 15, 30, False, "worked example: Maro Quill at the storehouse"), (2, 11, 6, False, "Lookout 2, IQ 11, D 6"),
         (0, 13, 0, False, "unjam with Gunsmithing 0, IQ 13"), (1, 12, 35, True, "Scaling 1 with the rope coil"),
         (3, 18, 0, False, "need above 100"), (0, 3, 60, False, "need below 0")]


@table("lvl,attr,d,tool,what", NEEDS, ids=["need-%d" % i for i in range(len(NEEDS))])
def test_check_need(lvl, attr, d, tool, what):
    check_eq("check_need(level=%d, attribute=%d, difficulty=%d, tool=%s) (%s)" % (lvl, attr, d, tool, what),
             call("rules.check_need", lvl, attr, d, tool), ref_check_need(lvl, attr, d, tool))


SKILLCHECKS = [(20261021, 2, 15, 30, False), (1, 0, 13, 0, False), (5, 3, 18, 0, False), (6, 0, 3, 60, False),
               (77, 1, 12, 35, True), (12345, 2, 11, 6, False)]


@table("seed,lvl,attr,d,tool", SKILLCHECKS, ids=["check-%d" % i for i in range(len(SKILLCHECKS))])
def test_skill_check(seed, lvl, attr, d, tool):
    ref = RefRng(seed)
    want = ref_skill_check(ref, lvl, attr, d, tool)
    r = _rng(seed)
    got = call("rules.skill_check", r, lvl, attr, d, tool)
    check_eq("skill_check(seed %d, level=%d, attribute=%d, difficulty=%d, tool=%s)" % (seed, lvl, attr, d, tool),
             {k: (got or {}).get(k, "<missing>") for k in want} if isinstance(got, dict) else got, want)
    check_eq("generator state after that check (one d100 unless need >= 100 or <= 0)", _state(r), ref.state)


PICKS = [([(1, 0, 1, 13), (5, 0, 2, 11), (4, 0, 1, 15)], 5, "highest level"),
         ([(1, 0, 1, 13), (4, 0, 1, 15)], 4, "level tie: higher attribute"),
         ([(3, 0, 1, 12), (2, 0, 1, 12)], 2, "full tie: lower slot"),
         ([(5, 1, 3, 18), (1, 0, 0, 10)], 1, "unconscious member skipped"),
         ([(1, 0, 0, 10), (2, 0, 0, 14)], 2, "nobody has the skill"),
         ([(1, 2, 2, 10), (2, 1, 2, 14)], None, "nobody conscious")]


@table("cands,want,what", PICKS, ids=[p[2].replace(" ", "-").replace(":", "") for p in PICKS])
def test_pick_checker(cands, want, what):
    c = [{"slot": s, "cond": cd, "level": l, "attribute": a} for s, cd, l, a in cands]
    check_eq("pick_checker (%s, LR-14)" % what, call("rules.pick_checker", c), want)


# ---- time (LR-15 to LR-17) --------------------------------------------------

CLOCKS = [((1, 480, 0), 1, 0), ((1, 539, 0), 1, 0), ((1, 1435, 0), 10, 0), ((1, 600, 50), 0, 30),
          ((1, 659, 50), 0, 10), ((1, 1380, 0), 130, 0), ((1, 480, 0), 60, 0), ((3, 1439, 59), 0, 1)]


@table("start,mins,secs", CLOCKS, ids=["clock-%d" % i for i in range(len(CLOCKS))])
def test_advance_clock(start, mins, secs):
    clock = {"day": start[0], "minute": start[1], "second": start[2]}
    want_clock, want_hours = ref_advance_clock(clock, mins, secs)
    got = call("rules.advance_clock", dict(clock), mins, secs)
    if not (isinstance(got, (tuple, list)) and len(got) == 2):
        fail("advance_clock must return (clock, hours), got %s" % W.short(got))
    check_eq("advance_clock(%r, %d min, %d s): clock" % (clock, mins, secs), got[0], want_clock)
    check_eq("advance_clock(%r, %d min, %d s): hours crossed, in order" % (clock, mins, secs), got[1], want_hours)


# ---- experience (LR-45, LR-46) ----------------------------------------------

@table("lvl", [1, 2, 3, 4, 9])
def test_xp_threshold(lvl):
    check_eq("xp_threshold(%d) (LR-45)" % lvl, call("rules.xp_threshold", lvl), ref_xp_threshold(lvl))


LEVELS = [(1, 104), (1, 99), (2, 214), (1, 300), (1, 1000), (3, 599), (2, 300)]


@table("lvl,xp", LEVELS, ids=["L%d-xp%d" % c for c in LEVELS])
def test_level_after(lvl, xp):
    check_eq("level_after(level=%d, xp=%d) (LR-45)" % (lvl, xp), call("rules.level_after", lvl, xp), ref_level_after(lvl, xp))


# ---- shops (LR-53) ---------------------------------------------------------

PRICES = [(30, 1), (8, 1), (140, 0), (110, 1), (14, 1), (100, 7), (60, 0), (1, 5)]


@table("price,h", PRICES, ids=["p%d-h%d" % c for c in PRICES])
def test_buy_price(price, h):
    check_eq("buy_price(%d, haggling=%d) (LR-53)" % (price, h), call("rules.buy_price", price, h), ref_buy_price(price, h))


@table("price,h", [(15, 1), (100, 9), (60, 0), (140, 2), (1, 0)])
def test_sell_price(price, h):
    check_eq("sell_price(%d, haggling=%d) (LR-53)" % (price, h), call("rules.sell_price", price, h), ref_sell_price(price, h))


@table("moneys,first,price", [([120, 60, 80, 70], 1, 30), ([20, 60, 80, 70], 1, 50),
                                                ([10, 5], 2, 12), ([10, 5], 1, 16), ([10, 5], 1, 15),
                                                ([0, 0, 40], 2, 40)], ids=["pay-%d" % i for i in range(6)])
def test_pay(moneys, first, price):
    check_eq("pay(%r, first_slot=%d, price=%d) (LR-20)" % (moneys, first, price),
             call("rules.pay", list(moneys), first, price), ref_pay(moneys, first, price))


# ---- monsters and encounters (LR-26 to LR-28) --------------------------------

MOBS = W.load_json(W.SCENARIO / "encounters.json")["monsters"]


def _mob(js):
    return {"name": js["name"], "sturdiness": js["sturdiness"], "combatRating": js["combat_rating"],
            "randomDamage": js["random_damage"], "maxGroup": js["max_group"], "armorClass": js["armor_class"],
            "fixedDamage": js["fixed_damage"], "weaponType": js["weapon_type"], "type": js["type"],
            "portrait": js["portrait"]}


@table("js", MOBS, ids=[m["name"].replace(" ", "-") for m in MOBS])
def test_monster_values(js):
    m = _mob(js)
    want = {"to_hit_base": 20 + 5 * m["combatRating"], "speed": m["combatRating"], "ac": m["armorClass"],
            "ranged": m["weaponType"] >= 3, "xp": m["sturdiness"] * (m["armorClass"] + 1)}
    got = call("rules.monster_values", m)
    check_eq("monster_values(%s) (LR-27)" % m["name"], {k: (got or {}).get(k, "<missing>") for k in want}
             if isinstance(got, dict) else got, want)


@table("seed,st", [(20261021, 12), (1, 900), (7, 4), (99, 255), (5, 1), (3, 513)])
def test_monster_hp(seed, st):
    ref = RefRng(seed)
    want = ref_monster_hp(ref, st)
    r = _rng(seed)
    check_eq("monster_hp(seed %d, sturdiness %d) (SPEC-03 6.6, high byte drawn first)" % (seed, st),
             call("rules.monster_hp", r, st), want)
    check_eq("generator state after monster_hp(seed %d, sturdiness %d)" % (seed, st), _state(r), ref.state)


@table("seed,idx", [(11, 2), (12, 4), (13, 1)])
def test_monster_damage(seed, idx):
    m = _mob(MOBS[idx])
    ref = RefRng(seed)
    want = ref.dice(m["randomDamage"], 6) + m["fixedDamage"]
    check_eq("monster_damage(seed %d, %s) (LR-27)" % (seed, m["name"]), call("rules.monster_damage", _rng(seed), m), want)


def _scenario_encounters():
    out = []
    for f in ("map0-overworld.json", "map3-pumphouse.json"):
        mj = W.load_json(W.SCENARIO / f)
        mobs = [_mob(x) for x in mj["mobs"]]
        for i, r in enumerate(mj["records"].get("3", [])):
            out.append(("%s-enc%d" % (f.split("-")[0], i + 1), mobs, {"groups": r["groups"]}))
    out.append(("size0-uses-maxgroup", [_mob(MOBS[1])], {"groups": [[1, False, 0], [0, False, 0], [0, False, 0]]}))
    out.append(("random-size0", [_mob(MOBS[2])], {"groups": [[1, True, 0], [0, False, 0], [0, False, 0]]}))
    return out


ENCS = _scenario_encounters()


@table("name,mobs,rec,seed", [e + (s,) for e in ENCS for s in (20261021, 3)])
def test_build_groups(name, mobs, rec, seed):
    ref = RefRng(seed)
    want = W.ref_build_groups(ref, mobs, rec)
    r = _rng(seed)
    got = call("rules.build_groups", r, copy.deepcopy(mobs), copy.deepcopy(rec))
    check_eq("build_groups(%s, seed %d) (LR-26, LR-28)" % (name, seed), got, want)
    check_eq("generator state after build_groups(%s, seed %d)" % (name, seed), _state(r), ref.state)


# ---- combat formulas (LR-34, LR-35, LR-39, LR-40, LR-43) ---------------------

RANGED = [(2, 14, 1, 3), (5, 18, 0, 1), (0, 3, 9, 5), (1, 15, 1, 3), (2, 12, 1, 1), (2, 15, 1, 2)]


@table("args", RANGED, ids=["r%d" % i for i in range(len(RANGED))])
def test_ranged_need(args):
    check_eq("ranged_need(level, agility, target_ac, band)=%r (LR-34)" % (args,), call("rules.ranged_need", *args),
             ref_ranged_need(*args))


MELEE = [(1, 11, 1), (0, 10, 0), (9, 18, 0), (0, 3, 9)]


@table("args", MELEE, ids=["m%d" % i for i in range(len(MELEE))])
def test_melee_need(args):
    check_eq("melee_need(level, agility, target_ac)=%r (LR-35)" % (args,), call("rules.melee_need", *args),
             ref_melee_need(*args))


MONNEED = [(6, 3, 3), (6, 2, 3), (7, 3, 1), (7, 5, 1), (1, 9, 5), (20, 0, 1)]


@table("args", MONNEED, ids=["n%d" % i for i in range(len(MONNEED))])
def test_monster_need(args):
    check_eq("monster_need(combat_rating, member_ac, band)=%r (LR-34, LR-35)" % (args,),
             call("rules.monster_need", *args), ref_monster_need(*args))


FLEE = [(14, 6, 0), (10, 12, 2), (3, 20, 0), (20, 0, 5)]


@table("args", FLEE, ids=["f%d" % i for i in range(len(FLEE))])
def test_flee_need(args):
    check_eq("flee_need(best_member_speed, best_monster_speed, command_level)=%r (LR-43)" % (args,),
             call("rules.flee_need", *args), ref_flee_need(*args))


@table("gs", [0, 1, 2, 3, 5])
def test_jam_chance(gs):
    check_eq("jam_chance(gunsmithing=%d) (LR-34)" % gs, call("rules.jam_chance", gs), ref_jam_chance(gs))


@table("g", [0, 1, 2, 3, 4])
def test_unarmed_attacks(g):
    check_eq("unarmed_attacks(grappling=%d) (LR-35)" % g, call("rules.unarmed_attacks", g), 1 + g // 2)


@table("st", [3, 10, 11, 12, 17])
def test_melee_damage_bonus(st):
    check_eq("melee_damage_bonus(strength=%d) (LR-35)" % st, call("rules.melee_damage_bonus", st), max(0, (st - 10) // 2))


DMG = [(24, 5), (10, 10), (10, 14), (10, 15), (3, 20), (1, 1), (5, 0)]


@table("hp,d", DMG, ids=["hp%d-d%d" % c for c in DMG])
def test_damage_member(hp, d):
    got = call("rules.damage_member", hp, d)
    want = ref_damage_member(hp, d)
    check_eq("damage_member(hp=%d, damage=%d) (LR-40)" % (hp, d),
             {k: (got or {}).get(k, "<missing>") for k in want} if isinstance(got, dict) else got, want)


def _actors():
    return [{"side": "monsters", "speed": 7, "group": 1, "index": 3}, {"side": "party", "speed": 9, "slot": 6},
            {"side": "monsters", "speed": 7, "group": 1, "index": 2}, {"side": "party", "speed": 12, "slot": 1},
            {"side": "party", "speed": 7, "slot": 4}, {"side": "monsters", "speed": 7, "group": 2, "index": 1},
            {"side": "party", "speed": 7, "slot": 2}, {"side": "monsters", "speed": 13, "group": 2, "index": 2}]


def test_speed_order():
    got = call("rules.speed_order", _actors())
    check_eq("speed_order (LR-35: speed, members before monsters, slot, group, monster)", got,
             ref_speed_order(_actors()))


# ---- LABSTATE.BIN (LR-57) ---------------------------------------------------

LABSTATE = {"steps": 145, "day": 1, "seconds": 0, "rng_state": 2973743393,
            "cell_changes": [[1, 8, 17, 0, 0, 28], [0, 31, 41, 0, 0, 22], [0, 30, 41, 0, 0, 13], [2, 3, 1, 4, 1, 29]]}


def test_labstate_encode():
    check_bytes("encode_labstate (LR-57, cell changes sorted by location, y, x)",
                call("labstate.encode_labstate", copy.deepcopy(LABSTATE)), W.ref_encode_labstate(LABSTATE))


def test_labstate_decode():
    blob = W.ref_encode_labstate(LABSTATE)
    want = dict(LABSTATE, cell_changes=sorted(LABSTATE["cell_changes"], key=lambda c: (c[0], c[2], c[1])))
    got = call("labstate.decode_labstate", blob)
    check_eq("decode_labstate (LR-57)", {k: (got or {}).get(k, "<missing>") for k in want}
             if isinstance(got, dict) else got, want)


def test_labstate_bad_sum():
    blob = bytearray(W.ref_encode_labstate(LABSTATE))
    blob[-1] ^= 0x01
    expect_error("FormatError", "labstate.decode_labstate", bytes(blob), what="checksum off by one bit")


def test_labstate_bad_magic():
    blob = bytearray(W.ref_encode_labstate(LABSTATE))
    blob[7] = ord("2")
    expect_error("FormatError", "labstate.decode_labstate", bytes(blob), what="magic WLLABSV2")


# ===========================================================================
# Engine behaviour through headless runs on the compiled Dry Fork data
# ===========================================================================

SEED = 20261021


def prefix(walkthrough, upto: str) -> list:
    out = []
    for item in walkthrough["script"]:
        out.append(item)
        if isinstance(item, dict) and item.get("checkpoint") == upto:
            return out
    raise AssertionError("no checkpoint %s in walkthrough.json" % upto)


def opening_script(walkthrough) -> list:
    out = []
    for item in walkthrough["script"]:
        if isinstance(item, dict) and "repeat_until" in item:
            return out + ["A"]
        out.append(item)
    raise AssertionError("walkthrough.json has no repeat_until macro")


def ckpt(events, name):
    for e in events:
        if e.get("type") == "checkpoint" and e.get("name") == name:
            st = e.get("state")
            if not isinstance(st, dict):
                fail("checkpoint %s has no state object" % name)
            return st
    fail("the engine log has no checkpoint %r" % name)


def strip(e):
    return {k: v for k, v in e.items() if k != "seq"}


def between(events, a, b):
    ia = next((i for i, e in enumerate(events) if e.get("type") == "checkpoint" and e.get("name") == a), None)
    ib = next((i for i, e in enumerate(events) if e.get("type") == "checkpoint" and e.get("name") == b), None)
    if ia is None or ib is None:
        fail("the engine log lacks checkpoint %s or %s" % (a, b))
    return [strip(e) for e in events[ia + 1:ib]]


def subset(what, state, want):
    check_eq(what, {k: state.get(k, "<missing>") for k in want}, want)


def test_new_game(runner):
    ev, _ = runner.run("newgame", {"seed": SEED, "script": [{"checkpoint": "a"}]})
    check_eq("first two events of a new game (SPEC-06 6.1, LR-25)", [strip(e) for e in ev[:2]],
             [{"type": "new_game", "seed": SEED}, {"type": "paragraph", "n": 1}])
    subset("new-game snapshot (SPEC-05 section 2, LR-4)", ckpt(ev, "a"),
           {"location": 1, "x": 15, "y": 20, "steps": 0, "day": 1, "hour": 8, "minute": 0, "mode": "map",
            "cell_changes": [], "rng_state": SEED})


def test_seed_override(runner):
    ev, _ = runner.run("override", {"seed": SEED, "script": [{"checkpoint": "a"}]}, 77)
    check_eq("new_game with --seed 77 overriding the script seed", strip(ev[0]), {"type": "new_game", "seed": 77})
    check_eq("generator state at the start with seed 77", ckpt(ev, "a").get("rng_state"), 77)


def test_steps_clock_and_transition(runner):
    ev, _ = runner.run("exit", {"seed": SEED, "script": ["DOWN"] * 11 + [{"checkpoint": "a"}, "RIGHT",
                                                                         {"checkpoint": "b"}]})
    subset("after 11 steps out of Saltwell (LR-15, LR-16, L-TR5)", ckpt(ev, "a"),
           {"location": 0, "x": 10, "y": 41, "steps": 11, "day": 1, "hour": 8, "minute": 11})
    subset("one overworld step later (10 minutes per step)", ckpt(ev, "b"),
           {"location": 0, "x": 11, "y": 41, "steps": 12, "hour": 8, "minute": 21})
    types = [strip(e) for e in ev if e.get("type") in ("map_change", "paragraph", "message")]
    check_eq("paragraph and transition events on the way out (LR-25: no message event for a paragraph)", types,
             [{"type": "paragraph", "n": 1}, {"type": "paragraph", "n": 2},
              {"type": "map_change", "location": 0, "x": 10, "y": 41}])


def test_bump_is_not_a_step(runner):
    # Addendum 7 (2026-10-31): the frozen expectation read the map transposed ([x][y]); under the
    # map file's declared [y][x] convention row 20 is sand from x=4 to x=14 and the cactus
    # (tile 11, class 11) stands at x=3, so 13 LEFTs are 11 steps and two bumps at (3, 20).
    ev, _ = runner.run("bump", {"seed": SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    subset("after 11 steps west and two bumps (LR-15)", ckpt(ev, "a"),
           {"location": 1, "x": 4, "y": 20, "steps": 11, "hour": 8, "minute": 11})
    tail = [strip(e) for e in ev if e.get("type") != "checkpoint"][-2:]
    check_eq("events of the bump into the cactus at (3, 20)", tail,
             [{"type": "input", "key": "LEFT"}, {"type": "bump", "x": 3, "y": 20, "action_class": 11, "action": 0}])


def test_rest(runner):
    ev, _ = runner.run("rest", {"seed": SEED, "script": ["R", {"checkpoint": "a"}]})
    subset("after one rest (LR-17)", ckpt(ev, "a"), {"steps": 0, "day": 1, "hour": 9, "minute": 0, "rng_state": SEED})
    i = next((k for k, e in enumerate(ev) if e.get("type") == "input"), None)
    check_eq("events after the R token (full HP, no Foraging)",
             [strip(e) for e in ev[i:] if e.get("type") != "checkpoint"],
             [{"type": "input", "key": "R"}, {"type": "rest"}])


def test_win_hook_without_item(runner):
    ev, _ = runner.run("pump", {"seed": SEED, "script": ["UP"] * 9 + [{"checkpoint": "a"}]})
    tail = [strip(e) for e in ev if e.get("type") != "checkpoint"][-3:]
    check_eq("bumping the Saltwell pump without the valve (LR-18, LR-24)", tail,
             [{"type": "input", "key": "UP"}, {"type": "bump", "x": 15, "y": 11, "action_class": 11, "action": 0},
              {"type": "paragraph", "n": 4}])
    subset("mode after the pump bump", ckpt(ev, "a"), {"mode": "map", "steps": 8})


# ---- shop, equip, recruit (walkthrough to CP2 and CP3; no random draws) -----

ITEMS = {it["id"]: it for it in W.load_json(W.SCENARIO / "items.json")["items"]}
SHOPS = W.load_json(W.SCENARIO / "shops.json")["shops"]


def _cp2(runner, walkthrough):
    ev, _ = runner.run("cp2", {"seed": SEED, "script": prefix(walkthrough, "CP2")})
    return between(ev, "CP1", "CP2")


def test_shop_buy_list(runner, walkthrough):
    seg = _cp2(runner, walkthrough)
    p = next((e for e in seg if e.get("type") == "prompt" and e.get("prompt") == "buy_item"), None)
    want = sorted(int(k) for k, v in SHOPS[0]["stock"].items() if 1 <= v <= 255)
    check_eq("buy list of shop list 0 (LR-50, SPEC-06 6.1 prompt)", p and p.get("items"), want)


def test_shop_buy_prices(runner, walkthrough):
    seg = _cp2(runner, walkthrough)
    buys = [e for e in seg if e.get("type") == "buy"]
    check_eq("number of purchases before CP2", len(buys), 3)
    for b in buys:
        want = ref_buy_price(ITEMS[b.get("item", 0)]["price"] if b.get("item") in ITEMS else 0, 1)
        check_eq("price of item %r bought by member %r (LR-53, best Haggling 1)" % (b.get("item"), b.get("member")),
                 b.get("price"), want)
    money = [e for e in seg if e.get("type") == "money"]
    pay = [[m.get("member"), m.get("delta")] for m in money if m.get("delta", 0) < 0]
    check_eq("payments (LR-20, LR-51: the buyer pays first)", pay,
             [[b.get("member"), -b.get("price", 0)] for b in buys])


def test_ammo_stacking(runner, walkthrough):
    seg = _cp2(runner, walkthrough)
    ammo = [[e.get("member"), e.get("item"), e.get("slot"), e.get("status")] for e in seg
            if e.get("type") == "buy" and e.get("item") == 4]
    check_eq("pistol rounds bought by members 3 and 4 stack on their box in slot 2 (LR-51)", ammo,
             [[3, 4, 2, 2], [4, 4, 2, 2]])


def test_shop_sell(runner, walkthrough):
    seg = _cp2(runner, walkthrough)
    i = next((k for k, e in enumerate(seg) if e.get("type") == "sell"), None)
    if i is None:
        fail("no sell event before CP2")
    check_eq("sale of the pipe club and the money that follows (LR-52, LR-53, SPEC-06 6 order)", seg[i:i + 2],
             [{"type": "sell", "member": 2, "item": 1, "price": ref_sell_price(15, 1), "slot": 3},
              {"type": "money", "member": 2, "delta": ref_sell_price(15, 1), "total": 60 + ref_sell_price(15, 1)}])


def test_equip_ac(runner, walkthrough):
    seg = _cp2(runner, walkthrough)
    eq = [e for e in seg if e.get("type") == "equip"]
    check_eq("Tobin equips the hide vest (LR-8, LR-47)", eq,
             [{"type": "equip", "member": 2, "slot": 3, "item": 7, "ac": ref_ac(12, 1, 0)}])


def test_recruit(runner, walkthrough):
    ev, _ = runner.run("cp3", {"seed": SEED, "script": prefix(walkthrough, "CP3")})
    seg = between(ev, "CP2", "CP3")
    picks = [e for e in seg if e.get("type") in ("cell_change", "recruit")]
    check_eq("recruiting Orla Penn (LR-19, LR-22)", picks,
             [{"type": "cell_change", "location": 1, "x": 8, "y": 17, "action_class": 0, "action": 0, "image": 28},
              {"type": "recruit", "location": 1, "npc": 0, "slot": 5}])
    party = ckpt(ev, "CP3").get("party") or []
    if len(party) != 5:
        fail("CP3: expected 5 members after the recruit, got %d" % len(party))
    subset("CP3 slot 5 (SPEC-05 10.2, LR-8, LR-46 rank)", party[4],
           {"slot": 5, "name": "Orla Penn", "npc": 1, "level": 2, "xp": 200, "max_hp": ref_max_hp(13, 2),
            "hp": ref_max_hp(13, 2), "cond": 0, "money": 25, "ac": ref_ac(15, 0, 0), "rank": "Hand",
            "items": [[5, 8], [6, 2]], "weapon_slot": 1, "armour_slot": 0, "skill_points": 0})


# ---- the first fight (raiders at (30, 41)), seeded -------------------------

OPEN_SEEDS = [20261021, 1, 2, 3]


def _opening(runner, walkthrough, seed):
    ev, _ = runner.run("opening", {"seed": seed, "script": opening_script(walkthrough)}, seed)
    return ev, CR.opening(seed)


@pytest.mark.parametrize("seed", OPEN_SEEDS)
def test_encounter_start(runner, walkthrough, seed):
    ev, ref = _opening(runner, walkthrough, seed)
    got = next((strip(e) for e in ev if e.get("type") == "encounter_start"), None)
    check_eq("encounter_start of the road raiders, seed %d (LR-26, LR-28, LR-29)" % seed, got, ref["encounter"])


@pytest.mark.parametrize("seed", OPEN_SEEDS)
def test_surprise_check(runner, walkthrough, seed):
    ev, ref = _opening(runner, walkthrough, seed)
    i = next((k for k, e in enumerate(ev) if e.get("type") == "encounter_start"), None)
    got = next((strip(e) for e in ev[i or 0:] if e.get("type") == "check"), None)
    check_eq("surprise check after the raiders appear, seed %d (LR-14, LR-30)" % seed, got, ref["check"])


@pytest.mark.parametrize("seed", OPEN_SEEDS)
def test_surprise_round(runner, walkthrough, seed):
    ev, ref = _opening(runner, walkthrough, seed)
    surprised = any(e.get("type") == "surprised" for e in ev)
    check_eq("surprised event present, seed %d (LR-30)" % seed, surprised, ref["surprised"])
    if ref["surprised"]:
        got = CR.combat_window(ev, 0)
        if got is None:
            fail("seed %d: no round_start with round 0 after the failed surprise check" % seed)
        check_eq("surprise round attacks, seed %d (LR-30, LR-34)" % seed, got, ref["round0"])


@pytest.mark.parametrize("seed", OPEN_SEEDS)
def test_round1_phase1(runner, walkthrough, seed):
    ev, ref = _opening(runner, walkthrough, seed)
    orders = next((strip(e) for e in ev if e.get("type") == "round_orders"), None)
    check_eq("round 1 auto orders, seed %d (LR-33)" % seed, orders,
             {"type": "round_orders", "round": 1, "orders": {str(s): ["fire", 1] for s in range(1, 6)}})
    got = CR.combat_window(ev, 1)
    if got is None:
        fail("seed %d: no round_start with round 1" % seed)
    check_eq("round 1 phase 1 resolution, seed %d (LR-34: shots, monster fire, deaths)" % seed, got, ref["round1"])


FIGHT_SEEDS = [1, 2, 3, 4, 5]


def _fight(runner, walkthrough, seed):
    ev, _ = runner.run("cp4", {"seed": seed, "script": prefix(walkthrough, "CP4")}, seed)
    return ev


@pytest.mark.parametrize("cat", ["orders", "need", "target", "jam", "victory"])
def test_raider_fight_rules(runner, walkthrough, cat):
    for seed in FIGHT_SEEDS:
        ev = _fight(runner, walkthrough, seed)
        issues = [m for c, m in CR.consistency(ev) if c in (cat, "all")]
        if issues:
            fail("seed %d, %s: %s" % (seed, cat, issues[0]))


def test_victory_loot(runner, walkthrough):
    for seed in [SEED] + FIGHT_SEEDS[:2]:
        ev = _fight(runner, walkthrough, seed)
        i = next((k for k, e in enumerate(ev) if e.get("type") == "combat_end"), None)
        if i is None:
            fail("seed %d: no combat_end in the raider fight" % seed)
        got = [strip(e) for e in ev[i:] if e.get("type") in ("cell_change", "money")][:3]
        check_eq("seed %d: tail (5, 1) then loot of 75 coins after the victory (LR-44, SPEC-03 9.6)" % seed, got,
                 [{"type": "cell_change", "location": 0, "x": 30, "y": 41, "action_class": 5, "action": 1, "image": 13},
                  {"type": "money", "member": 1, "delta": 75, "total": 195},
                  {"type": "cell_change", "location": 0, "x": 30, "y": 41, "action_class": 0, "action": 0, "image": 13}])


# ---- locks, healer, key (walkthrough to CP6, CP7, CP9) -----------------------

@pytest.mark.parametrize("seed", [SEED, 1, 2])
def test_storehouse_lock(runner, walkthrough, seed):
    ev, _ = runner.run("cp6", {"seed": seed, "script": prefix(walkthrough, "CP6")}, seed)
    seg = between(ev, "CP5", "CP6")
    checks = [e for e in seg if e.get("type") == "check"]
    if not checks:
        fail("seed %d: no check event at the storehouse door" % seed)
    for c in checks:
        exp = {"type": "check", "member": 3, "skill": 14, "level": 2, "need": 50}
        check_eq("seed %d: storehouse check (LR-13, LR-14, worked example need 50)" % seed,
                 {k: c.get(k) for k in exp}, exp)
        if c.get("success") != (isinstance(c.get("roll"), int) and 1 <= c["roll"] <= 50):
            fail("seed %d: check roll %r with need 50 but success=%r" % (seed, c.get("roll"), c.get("success")))
    if any(c.get("success") for c in checks[:-1]) or not checks[-1].get("success"):
        fail("seed %d: the bumps must repeat until the first success (repeat_until cell:2,26,14)" % seed)
    i = seg.index(checks[-1])
    check_eq("seed %d: events after the successful check (LR-21 order)" % seed, seg[i + 1:i + 6],
             [{"type": "unlock", "x": 26, "y": 14},
              {"type": "cell_change", "location": 2, "x": 26, "y": 14, "action_class": 4, "action": 1, "image": 30},
              {"type": "cell_change", "location": 2, "x": 26, "y": 14, "action_class": 4, "action": 1, "image": 29},
              {"type": "xp", "member": 3, "delta": 10, "total": 114},
              {"type": "paragraph", "n": 12}])
    for c in checks[:-1]:
        j = seg.index(c)
        check_eq("seed %d: failed check is followed by the fail message (string 9)" % seed, seg[j + 1],
                 {"type": "message", "location": 2, "string": 9})


def test_healer(runner, walkthrough):
    ev, _ = runner.run("cp7", {"seed": SEED, "script": prefix(walkthrough, "CP7")})
    seg = between(ev, "CP6", "CP7")
    i = next((k for k, e in enumerate(seg) if e.get("type") == "bump" and e.get("x") == 25 and e.get("y") == 21), None)
    if i is None:
        fail("no bump of the Ninemile healer's cot (25, 21) before CP7")
    got = [e for e in seg[i:] if e.get("type") in ("prompt", "money", "heal_all")]
    check_eq("Ninemile healer (LR-20, LR-23)", got,
             [{"type": "prompt", "prompt": "heal", "price": 40}, {"type": "money", "member": 1, "delta": -40, "total": 51},
              {"type": "heal_all", "price": 40}])
    for m in ckpt(ev, "CP7").get("party") or []:
        if m.get("hp") != m.get("max_hp") or m.get("cond") != 0:
            fail("CP7 slot %r: hp %r of max %r, cond %r after the healer" % (m.get("slot"), m.get("hp"),
                                                                           m.get("max_hp"), m.get("cond")))


def test_key_lock(runner, walkthrough):
    ev, _ = runner.run("cp9", {"seed": SEED, "script": prefix(walkthrough, "CP9")})
    seg = between(ev, "CP8", "CP9")
    i = next((k for k, e in enumerate(seg) if e.get("type") == "bump" and e.get("x") == 16 and e.get("y") == 6), None)
    if i is None:
        fail("no bump of the vault gate (16, 6) before CP9")
    check_eq("vault gate opened with the Gate card (LR-21: key, no check, no experience)", seg[i + 1:i + 7],
             [{"type": "message", "location": 3, "string": 10}, {"type": "key_used", "member": 1, "item": 11},
              {"type": "unlock", "x": 16, "y": 6},
              {"type": "cell_change", "location": 3, "x": 16, "y": 6, "action_class": 4, "action": 4, "image": 39},
              {"type": "cell_change", "location": 3, "x": 16, "y": 6, "action_class": 4, "action": 4, "image": 37},
              {"type": "paragraph", "n": 21}])


# ---- save and load (LR-54 to LR-57) -----------------------------------------

def _saved(runner, walkthrough):
    script = prefix(walkthrough, "CP5-pre-save") + ["S"]
    return runner.run("saved", {"seed": SEED, "script": script})


def _payload(dd):
    t = call("containers.read_tables", str(dd / "LABTABLES.BIN"))
    g = (dd / "GAME1").read_bytes()
    off = t["savegameOffsets"][0]
    try:
        return C.rxor_decode_whole(g, 0x800, off + 4)
    except ValueError as e:
        fail("the saved GAME1 savegame block fails the reference checksum: %s" % e)


def test_save_labstate(runner, walkthrough):
    ev, dd = _saved(runner, walkthrough)
    st = ckpt(ev, "CP5-pre-save")
    p = dd / "LABSTATE.BIN"
    if not p.is_file():
        fail("no LABSTATE.BIN next to GAME1 after S (LR-54)")
    try:
        ls = W.ref_labstate(p.read_bytes())
    except ValueError as e:
        fail("LABSTATE.BIN does not follow LR-57: %s" % e)
    want_cc = sorted(st.get("cell_changes") or [], key=lambda c: (c[0], c[2], c[1]))
    check_eq("LABSTATE.BIN after the save (LR-57)", ls,
             {"steps": st.get("steps"), "day": st.get("day"), "seconds": 0, "pad": 0, "rng_state": st.get("rng_state"),
              "cell_changes": want_cc})


def test_save_savegame_fields(runner, walkthrough):
    ev, dd = _saved(runner, walkthrough)
    p = _payload(dd)
    got = {"order": list(p[1:8]), "x": p[8], "y": p[9], "map": p[10], "prevX": p[11], "prevY": p[12], "prevMap": p[13],
           "groups1to3": list(p[14:56]), "viewport": [p[0x78], p[0x79]], "members": [p[0x7D], p[0x80]],
           "party": p[0x7E], "location": p[0x7F], "extra": p[0x81], "clock": [p[0x83], p[0x84]], "scroll": p[0x85],
           "serial": int.from_bytes(p[0xF5:0xF9], "little")}
    want = {"order": [1, 2, 3, 4, 5, 0, 0], "x": 25, "y": 5, "map": 2, "prevX": 43, "prevY": 28, "prevMap": 0,
            "groups1to3": [0] * 42, "viewport": [25, 5], "members": [5, 5], "party": 0, "location": 2, "extra": 0,
            "clock": [28, 17], "scroll": 0, "serial": 1}
    check_eq("savegame payload after the save at CP5 (LR-55, L-TR4)", got, want)
    names = [bytes(p[0x100 * (s + 1):0x100 * (s + 1) + 14]).split(b"\x00")[0].decode("latin-1") for s in range(7)]
    check_eq("character record names (LR-55)", names, ["Hessa Brand", "Tobin Ash", "Maro Quill", "Dell Ostrow",
                                                       "Orla Penn", "", ""])
    check_eq("slots 6 and 7 all zero (LR-55)", any(p[0x600:0x800]), False)


def test_load_restores_state(runner, walkthrough):
    ev, dd = _saved(runner, walkthrough)
    want = ckpt(ev, "CP5-pre-save")
    ev2, _ = runner.run("reload", {"seed": 5, "script": ["O", "Y", {"checkpoint": "loaded"}]}, None, data_dir=dd)
    check_eq("a fresh run that loads the save sees the saved state (LR-4, LR-56)", ckpt(ev2, "loaded"), want)


def test_save_load_save(runner, walkthrough):
    _, dd1 = _saved(runner, walkthrough)
    p1 = _payload(dd1)
    l1 = (dd1 / "LABSTATE.BIN").read_bytes()
    _, dd2 = runner.run("saveloadsave", {"seed": SEED, "script": prefix(walkthrough, "CP5") + ["S"]})
    p2 = _payload(dd2)
    diff = [i for i in range(0x800) if p1[i] != p2[i]]
    if any(not (0xF5 <= i < 0xF9) for i in diff):
        j = next(i for i in diff if not (0xF5 <= i < 0xF9))
        fail("save, load, save: payload byte 0x%03X differs (%02X then %02X); only the serial may change (LR-56)"
             % (j, p1[j], p2[j]))
    check_eq("save, load, save: serial", int.from_bytes(p2[0xF5:0xF9], "little"),
             int.from_bytes(p1[0xF5:0xF9], "little") + 1)
    check_bytes("save, load, save: LABSTATE.BIN identical (LR-56)", (dd2 / "LABSTATE.BIN").read_bytes(), l1)


def test_load_bad_labstate(runner, walkthrough, tmp_path_factory):
    _, dd = _saved(runner, walkthrough)
    bad = tmp_path_factory.mktemp("badsave")
    import shutil
    shutil.copytree(dd, bad, dirs_exist_ok=True)
    b = bytearray((bad / "LABSTATE.BIN").read_bytes())
    b[-1] ^= 0x01
    (bad / "LABSTATE.BIN").write_bytes(bytes(b))
    expect_error("FormatError", "headless.run", str(bad), {"seed": SEED, "script": ["O", "Y"]}, None,
                 what="load with a wrong LABSTATE.BIN sum (LR-57, SPEC-06 exit code 3)")
