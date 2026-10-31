#!/usr/bin/env python3
"""Oracle runner for the acceptance tests (SPEC-07 section 5).

Runs in its own process so that SPEC/reference/fixtures_gen.py (which puts
SPEC/reference on sys.path) never shares a process with the engine under test.

    python3 oracle_tool.py fixtures OUTDIR MANIFEST_DIR [SEED]
        Write the SPEC-02/SPEC-03 fixture set (default seed 19880101) into OUTDIR and
        move manifest.json into MANIFEST_DIR, away from the files the engine reads.

    python3 oracle_tool.py compiled DATA_DIR SCENARIO_DIR
        Decode the engine's compiled scenario files with the reference readers and
        build the expected decoded structures from the scenario JSON. Prints JSON:
        {"oracle": {...}, "expected": {...}, "errors": {section: message}}.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import traceback

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(HERE), "SPEC", "reference")
sys.path.insert(0, REF)
import codecs_ref as C  # noqa: E402
import fixtures_gen as FG  # noqa: E402


def cmd_fixtures(outdir: str, mandir: str, seed: int = FG.DEFAULT_SEED) -> int:
    FG.generate(outdir, seed)
    errs = FG.verify(outdir)
    if errs:
        print(json.dumps({"ok": False, "errors": errs[:20]}))
        return 1
    os.makedirs(mandir, exist_ok=True)
    shutil.move(os.path.join(outdir, "manifest.json"), os.path.join(mandir, "manifest.json"))
    print(json.dumps({"ok": True}))
    return 0


def _rd(d: str, name: str) -> bytes:
    with open(os.path.join(d, name), "rb") as fh:
        return fh.read()


def _js(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _plain(v):
    return json.loads(json.dumps(v, default=lambda o: o.hex() if isinstance(o, (bytes, bytearray)) else str(o)))


# ---- expected structures from the scenario JSON -------------------------

def conv_record(c: int, r: dict) -> dict:
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
        raise ValueError("no lab record for class %d" % c)
    d["newClass"], d["newAction"] = r["new_class"], r["new_action"]
    return FG._norm(c, d)


def char_from_json(p: dict, npc: int, catalog: dict, ranks: list[str]) -> dict:
    a = p["attrs"]
    level = p["level"]
    hp = 10 + a["STR"] + (level - 1) * (2 + a["STR"] // 5)
    bonus = 0
    if p["armour_slot"]:
        bonus = catalog[p["items"][p["armour_slot"] - 1][0]]["damage"]
    evasion = dict((s, l) for s, l in p["skills"]).get(11, 0)
    c = {"name": p["name"].encode("latin-1"), "strength": a["STR"], "intelligence": a["IQ"],
         "luck": a["LCK"], "speed": a["SPD"], "agility": a["AGL"], "dexterity": 0, "charisma": a["CHA"],
         "money": p["money"], "gender": p["gender"], "nationality": p["nationality"],
         "armorClass": a["AGL"] // 5 + bonus + evasion, "maxCon": hp, "curCon": hp,
         "weaponSlot": p["weapon_slot"], "skillPoints": 0, "experience": p["xp"], "level": level,
         "armorSlot": p["armour_slot"], "lastCon": 0, "afflictions": 0, "npc": npc,
         "itemRefuse": 0, "skillRefuse": 0, "attribRefuse": 0, "tradeRefuse": 0, "joinString": 0,
         "willingness": 0, "rank": ranks[min(level, 7) - 1].encode("latin-1"), "gameWon": 0,
         "specialPromotion": 0, "skills": [list(x) for x in p["skills"]], "items": [list(x) for x in p["items"]]}
    return FG.char_decode(FG.char_encode(c))


EMPTY_CHAR = None


def expected_from_json(sd: str) -> dict:
    scen = _js(os.path.join(sd, "scenario.json"))
    items = _js(os.path.join(sd, "items.json"))["items"]
    catalog = {it["id"]: it for it in items}
    ranks = scen["labstr_tables"]["3"]["strings"]
    out = {"maps": {}, "files": {}}
    for loc in scen["locations"]:
        m = _js(os.path.join(sd, loc["file"]))
        S = loc["size"]
        info = m["info"]
        mi = {"encounterFrequency": info["encounter_frequency"], "tileset": info["tileset"],
              "randomMonsterTypes": info["random_monster_types"],
              "maxRandomEncounters": info["max_random_encounters"], "borderImage": info["border_image"],
              "timePerStep": info["time_per_step"], "healRate": info["heal_rate"]}
        strings = list(m["strings"]) + [""] * ((-len(m["strings"])) % 4)
        mobs = []
        for mob in m["mobs"]:
            name = mob["name"].encode("latin-1")
            if mob.get("plural_suffix"):
                name += b"\x0a\x0a" + mob["plural_suffix"].encode("latin-1") + b"\x0a"
            md = {"name": name, "sturdiness": mob["sturdiness"], "combatRating": mob["combat_rating"],
                  "randomDamage": mob["random_damage"], "maxGroup": mob["max_group"],
                  "armorClass": mob["armor_class"], "fixedDamage": mob["fixed_damage"],
                  "weaponType": mob["weapon_type"], "type": mob["type"], "portrait": mob["portrait"]}
            mobs.append(FG.mob_decode(FG.mob_encode(md), name))
        out["maps"][str(loc["location"])] = {
            "size": S,
            "info": FG.mapinfo_decode(FG.mapinfo_encode(S, mi)),
            "cells": {"actionClass": m["action_class"], "action": m["action_value"],
                      "image": [[t + 10 for t in row] for row in m["tiles"]]},
            "actions": {str(c): [None] + [conv_record(int(c), r) for r in recs]
                        for c, recs in sorted(m["records"].items(), key=lambda kv: int(kv[0])) if recs},
            "npcs": [char_from_json(n, 1, catalog, ranks) for n in m["npcs"]],
            "mobs": mobs,
            "strings": strings,
        }
    party = _js(os.path.join(sd, "party.json"))["party"]
    st = scen["start"]
    chars = [char_from_json(p, 0, catalog, ranks) for p in party]
    empty = FG.char_decode(bytes(0x100))
    n = len(party)
    out["savegame"] = {
        "groups": [{"order": list(range(1, n + 1)) + [0] * (7 - n), "x": st["x"], "y": st["y"],
                    "map": st["location"], "prevX": 0, "prevY": 0, "prevMap": 0}]
        + [{"order": [0] * 7, "x": 0, "y": 0, "map": 0, "prevX": 0, "prevY": 0, "prevMap": 0}] * 3,
        "viewportX": st["x"], "viewportY": st["y"], "currentMembers": n, "currentParty": 0,
        "currentMap": st["location"], "totalMembers": n, "extraGroups": 0, "minute": 0,
        "hour": st["hour"], "combatScrollSpeed": 0, "serial": 0,
        "characters": chars + [empty] * (7 - n),
    }
    shops = _js(os.path.join(sd, "shops.json"))["shops"]
    out["shops"] = []
    for sh in shops:
        recs = []
        for i in range(94):
            it = catalog.get(i + 1)
            if it is None:
                recs.append({"price": 0, "stock": 0, "type": 0, "lowFlags": 0, "capacity": 0,
                             "skill": 0, "damage": 0, "ammo": 0})
            else:
                recs.append({"price": it["price"], "stock": sh["stock"].get(str(it["id"]), 0),
                             "type": it["type_byte"] >> 3, "lowFlags": it["type_byte"] & 7,
                             "capacity": it["capacity"], "skill": it["skill"], "damage": it["damage"],
                             "ammo": it["ammo"]})
        out["shops"].append({"header": "606060003708f839", "items": recs})
    strs = _js(os.path.join(sd, "strings.json"))["strings"]
    skills = _js(os.path.join(sd, "skills.json"))["skills"]

    def pad(lst):
        return list(lst) + [""] * ((-len(lst)) % 4)

    t1 = [""] * (max(s["id"] for s in strs) + 1)
    for s_ in strs:
        t1[s_["id"]] = s_["text"].replace("{name}", "\x0b").replace("{num}", "\x0f")
    t2 = [""] + [s_["name"] for s_ in sorted(skills, key=lambda k: k["id"])]
    t2 += [it["name"] for it in sorted(items, key=lambda k: k["id"])]
    lt = scen["labstr_tables"]
    out["labstr"] = [pad(lt["0"]["strings"]), pad(t1), pad(t2), pad(lt["3"]["strings"]),
                     pad(lt["4"]["strings"]), pad(lt["5"]["strings"])]
    e0 = _js(os.path.join(sd, "skills.json"))["entry0"]
    lsk = [[(e0["iq_req"] << 3) | e0["cost"], e0["attr_offset"]]]
    for s_ in sorted(skills, key=lambda k: k["id"]):
        lsk.append(list(s_["labskill_bytes"]))
    out["labskill"] = lsk
    out["hooks"] = _js(os.path.join(sd, "hooks.json"))
    out["paragraphs"] = _js(os.path.join(sd, "paragraphs.json"))
    return out


# ---- reference decoding of the compiled files ----------------------------

def oracle_compiled(dd: str, errors: dict) -> dict:
    o: dict = {}

    def section(name, fn):
        try:
            o[name] = _plain(fn())
        except Exception as e:  # noqa: BLE001
            errors[name] = "%s: %s" % (type(e).__name__, e)

    t = {}

    def tables():
        t.update(FG.labtables_decode(_rd(dd, "LABTABLES.BIN")))
        return t

    section("tables", tables)
    if not t:
        return o
    game = None
    try:
        game = _rd(dd, "GAME1")
    except OSError as e:
        errors["game"] = str(e)
    if game is not None:
        for loc in range(50):
            code = t["locationMapping"][loc]
            if code >> 6 != 2:
                continue
            idx = code & 0x3F

            def mp(idx=idx, loc=loc):
                return FG.map_decode(game, t["mapOffsets"][idx], t["mapSizes"][loc], t["tileMapOffsets"][loc])
            section("map%d" % loc, mp)
        section("savegame", lambda: FG.savegame_decode(game, t["savegameOffsets"][0]))
        base = t["savegameOffsets"][0] + t["savegameSize"]
        for i in range(t["shopListCounts"][0]):
            section("shop%d" % i, lambda i=i: FG.shop_decode(game, base + t["shopListRelOffsets"][i]))
        o["gameLength"] = len(game)
    section("labstr", lambda: [[FG.s(x) for x in tb] for tb in FG.labstr_decode(_rd(dd, "LABSTR.BIN"))])

    def tiles():
        ah = _rd(dd, "ALLHTDS1")
        out, off = [], 0
        while off < len(ah):
            payload, disk, off = C.msqh_decode(ah, off)
            out.append([FG.unpack4(C.vxor_decode(payload[i:i + 128], 8), 16) for i in range(0, len(payload), 128)])
        return {"tilesets": out, "size": len(ah)}
    section("tilesets", tiles)

    def portraits():
        ap = _rd(dd, "ALLPICS1")
        res = {}
        for raw in range(80):
            ci = t["portraitIndices1"][raw]
            if ci == 0x80:
                continue
            off = t["portraitOffsets1"][ci]
            b, _, o2 = C.msqh_decode(ap, off)
            anim, _, _ = C.msqh_decode(ap, o2)
            sc, up = FG.portrait_anim_decode(anim)
            res[str(raw)] = {"offset": off, "base": C.vxor_decode(b, 48).hex(), "scripts": sc, "updates": up}
        return res
    section("portraits", portraits)
    section("labskill", lambda: list(_rd(dd, "LABSKILL.BIN")))
    files = {}
    for name in sorted(os.listdir(dd)):
        p = os.path.join(dd, name)
        if os.path.isfile(p):
            files[name] = os.path.getsize(p)
    o["files"] = files
    return o


def cmd_compiled(dd: str, sd: str) -> int:
    errors: dict = {}
    try:
        expected = _plain(expected_from_json(sd))
    except Exception:  # noqa: BLE001
        print(json.dumps({"fatal": traceback.format_exc()}))
        return 1
    oracle = oracle_compiled(dd, errors)
    print(json.dumps({"oracle": oracle, "expected": expected, "errors": errors}))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["fixtures"] and len(a) in (3, 4):
        sys.exit(cmd_fixtures(a[1], a[2], int(a[3]) if len(a) == 4 else FG.DEFAULT_SEED))
    if a[:1] == ["compiled"] and len(a) == 3:
        sys.exit(cmd_compiled(a[1], a[2]))
    print(__doc__)
    sys.exit(2)
