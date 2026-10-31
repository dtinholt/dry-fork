"""SPEC-04 LR-26 to LR-46: combat resolution for the headless driver.

The engine keeps ``self.combat`` as a dict while a fight is running:

    {"round": int,            # 0 while the surprise round is pending
     "groups": [...],         # LR-26 groups, each with "hp" per monster
     "band": int,             # LR-28 range band (1 = melee)
     "surprised": bool,
     "kills": int,
     "fired": set(),          # slots that fired in phase 1
     "pending_monsters": [[int]],   # phase 1 damage per group/index
     "pending_members": {slot: int},
     "over": bool,
     "last_death_round": int}

This module is a mixin: ``wlengine.headless.Engine`` inherits from
``CombatMixin`` so the combat methods can use the engine's helpers
(``emit``, ``item_record``, ``skill_level``, ``rng`` ...).
"""

from __future__ import annotations

from . import maps, rules

RANGED_SKILLS = (4, 5, 12)
GUNSMITHING = 22
LOOKOUT = 18
SALVAGE = 26
RANKS = ["Drifter", "Hand", "Outrider", "Warden", "Steward", "Marshal", "Old hand"]


def _alive(member):
    return member.get("hp", 0) > 0 and not member.get("cond")


def weapon_dice(rec):
    """(n, s) of a weapon's damage: high nibble dice, low nibble sides."""
    if rec is None:
        return 1, 6
    if "damage_n" in rec:
        return rec.get("damage_n", 1), rec.get("damage_s", 6)
    byte = rec.get("damage", 0) or 0
    n = (byte >> 4) & 0x0F
    s = byte & 0x0F
    if n <= 0:
        n = 1
    if s <= 0:
        s = 6
    return n, s


class CombatMixin:
    # -- inventory helpers -------------------------------------------------

    def member_weapon(self, member):
        """The equipped weapon: item slot 1 (LR-33)."""
        items = member.get("items") or []
        if not items:
            return None, 0
        iid = items[0][0]
        return self.item_record(iid), iid

    def weapon_ammo(self, member):
        """LR-38: the weapon item's status byte (bits 0-6) is the load."""
        items = member.get("items") or []
        if not items:
            return 0
        return items[0][1] & 0x7F

    def weapon_jammed(self, member):
        """LR-38: bit 7 of the weapon item's status byte is the jam flag."""
        items = member.get("items") or []
        if not items:
            return False
        return bool(items[0][1] & 0x80)

    def set_weapon_status(self, member, value):
        items = member.get("items") or []
        if items:
            items[0][1] = value & 0xFF

    def ammo_boxes(self, member):
        """LR-38: the boxes of the weapon's ammunition the member carries.

        An ammunition item is one whose class is ammo (type 3); its status byte
        holds a count of boxes.  The weapon's record names its ammunition item
        id, so prefer that when it is set.
        """
        rec, _iid = self.member_weapon(member)
        want = rec.get("ammo", 0) if rec else 0
        total = 0
        for iid, count in (member.get("items") or [])[1:]:
            irec = self.item_record(iid)
            if not irec or irec.get("type") != 3:
                continue
            if want and iid != want:
                continue
            total += count
        return total

    def spend_ammo(self, member):
        items = member.get("items") or []
        if not items:
            return
        items[0][1] = (items[0][1] & 0x80) | max(0, (items[0][1] & 0x7F) - 1)

    def reload(self, member):
        """LR-33: one ammunition item refills the weapon to capacity."""
        rec, _iid = self.member_weapon(member)
        cap = rec.get("capacity", 0) if rec else 0
        want = rec.get("ammo", 0) if rec else 0
        items = member.get("items") or []
        for idx in range(1, len(items)):
            iid, count = items[idx]
            irec = self.item_record(iid)
            if not irec or irec.get("type") != 3 or count <= 0:
                continue
            if want and iid != want:
                continue
            items[idx] = [iid, count - 1]
            self.set_weapon_status(member, cap)
            return cap
        return 0

    # -- orders (LR-33) ----------------------------------------------------

    def auto_orders(self):
        c = self.combat
        orders = {}
        any_alive = any(hp > 0 for g in c["groups"] for hp in g["hp"])
        band = self.combat_band()
        for i, m in enumerate(self.party):
            slot = str(i + 1)
            if not _alive(m):
                orders[slot] = ["dead"]
                continue
            if not any_alive:
                orders[slot] = ["wait"]
                continue
            if self.weapon_jammed(m):
                orders[slot] = ["unjam"]
                continue
            rec, _iid = self.member_weapon(m)
            if rec is not None and rec.get("skill") in RANGED_SKILLS:
                if self.weapon_ammo(m) > 0:
                    orders[slot] = ["fire", 1]
                    continue
                if self.ammo_boxes(m) > 0:
                    orders[slot] = ["reload"]
                    continue
                orders[slot] = ["unarmed", 1] if band == 1 else ["advance", 1]
                continue
            if rec is not None and self.item_is_melee(rec):
                orders[slot] = ["melee", 1] if band == 1 else ["advance", 1]
                continue
            orders[slot] = ["unarmed", 1] if band == 1 else ["advance", 1]
        return orders

    def item_is_melee(self, rec):
        """LR-33: item class 1 is a melee weapon (SPEC-02 4.4 type byte)."""
        if "type" in rec:
            return rec.get("type") == 1
        return (rec.get("type_byte", 0) >> 3) == 1

    # -- targeting ---------------------------------------------------------

    def pick_monster_target(self, pending=None):
        """LR-34 step 4: first monster that is still standing after pending damage."""
        c = self.combat
        if pending is None:
            pending = c.get("pending_monsters")
        band = self.combat_band()
        for gi, g in enumerate(c["groups"]):
            pend = pending[gi] if pending else [0] * len(g["hp"])
            for mi, hp in enumerate(g["hp"]):
                if hp > 0 and hp - pend[mi] > 0:
                    return {"group": gi, "index": mi, "ac": g["mob"].get("armorClass", 0),
                            "band": band}
        for gi, g in enumerate(c["groups"]):
            for mi, hp in enumerate(g["hp"]):
                if hp > 0:
                    return {"group": gi, "index": mi, "ac": g["mob"].get("armorClass", 0),
                            "band": band}
        return None

    def combat_band(self):
        """LR-28: the range band in force, taken from the living groups.

        ``headless.end_of_round`` lowers each melee group's own ``band`` and
        emits ``group_closes``; the need formulas must use that band, not a
        separate global counter that only ``advance`` touches.
        """
        c = self.combat
        if c is None:
            return 1
        bands = [g.get("band", c.get("band", 1)) for g in c["groups"]
                 if any(hp > 0 for hp in g["hp"])]
        if not bands:
            bands = [g.get("band", c.get("band", 1)) for g in c["groups"]]
        if not bands:
            return c.get("band", 1)
        return min(bands)

    def pick_random_member(self):
        """LR-34: a conscious member chosen uniformly."""
        conscious = [i + 1 for i, m in enumerate(self.party) if _alive(m)]
        if not conscious:
            return None
        slot = conscious[self.rng.roll(len(conscious)) - 1]
        return {"slot": slot, "ac": self.party[slot - 1].get("ac", 0)}

    # -- phase 1 (LR-34) ---------------------------------------------------

    def party_phase1(self):
        c = self.combat
        if c is None:
            return
        fired = c.setdefault("fired", set())
        pend = c["pending_monsters"]
        orders = c.get("orders") or {}
        for i, m in enumerate(self.party):
            if not _alive(m):
                continue
            order = orders.get(str(i + 1)) or []
            # LR-34: only members with a ranged or burst attack order fire in
            # phase 1; a member ordered to reload or unjam does nothing here.
            if not order or order[0] != "fire":
                continue
            rec, _iid = self.member_weapon(m)
            if rec is None or rec.get("skill") not in RANGED_SKILLS:
                continue
            if self.weapon_ammo(m) <= 0:
                self.emit("click", member=i + 1)
                continue
            roll = self.rng.d100()
            jam = rules.jam_chance(self.skill_level(m, GUNSMITHING))
            if roll <= jam:
                m["jammed"] = True
                self.set_weapon_status(m, 0x80 | self.weapon_ammo(m))
                self.emit("jam", member=i + 1, roll=roll, chance=jam)
                continue
            self.spend_ammo(m)
            fired.add(i + 1)
            target = self.pick_monster_target(pend)
            if target is None:
                continue
            need = rules.ranged_need(self.skill_level(m, rec.get("skill", 0)),
                                     (m.get("attrs") or {}).get("AGL", 0),
                                     target["ac"], self.combat_band())
            roll = self.rng.d100()
            hit = roll <= need
            ev = {"side": "party", "member": i + 1, "group": target["group"] + 1,
                  "target": target["index"] + 1, "need": need, "roll": roll, "hit": hit}
            if hit:
                n, s = weapon_dice(rec)
                dmg = self.rng.dice(n, s)
                ev["damage"] = dmg
                pend[target["group"]][target["index"]] += dmg
            self.emit("attack", **ev)

    def monster_phase1(self):
        c = self.combat
        if c is None:
            return
        pend = c["pending_members"]
        conscious = [i + 1 for i, m in enumerate(self.party) if _alive(m)]
        for gi, g in enumerate(c["groups"]):
            mob = g["mob"]
            if mob.get("weaponType", 0) < 3:
                continue
            for mi, hp in enumerate(g["hp"]):
                if hp <= 0:
                    continue
                if not conscious:
                    break
                t = conscious[self.rng.roll(len(conscious)) - 1]
                m = self.party[t - 1]
                need = rules.monster_need(mob.get("combatRating", 0), m.get("ac", 0),
                                          self.combat_band())
                roll = self.rng.d100()
                hit = roll <= need
                ev = {"side": "monsters", "group": gi + 1, "attacker": mi + 1, "member": t,
                      "need": need, "roll": roll, "hit": hit}
                if hit:
                    dmg = self.rng.dice(mob.get("randomDamage", 0), 6) + mob.get("fixedDamage", 0)
                    ev["damage"] = dmg
                    pend[t] = pend.get(t, 0) + dmg
                self.emit("attack", **ev)

    def apply_phase1(self):
        c = self.combat
        for gi, g in enumerate(c["groups"]):
            pend = c["pending_monsters"][gi]
            for mi in range(len(g["hp"])):
                if g["hp"][mi] > 0 and pend[mi]:
                    g["hp"][mi] -= pend[mi]
                    if g["hp"][mi] <= 0:
                        c["kills"] += 1
                        c["last_death_round"] = c["round"]
                        self.emit("monster_dies", group=gi + 1, index=mi + 1)
        for slot in sorted(c["pending_members"]):
            dmg = c["pending_members"][slot]
            if dmg and _alive(self.party[slot - 1]):
                self.apply_member_damage(slot, dmg)
        # LR-34: the pending damage is spent once it has been applied; phase 2
        # targets the first monster that is *now* alive.
        c["pending_monsters"] = [[0] * len(g["hp"]) for g in c["groups"]]
        c["pending_members"] = {}

    def apply_member_damage(self, slot, dmg):
        m = self.party[slot - 1]
        res = rules.damage_member(m.get("hp", 0), dmg)
        m["hp"] = res["hp"]
        if res.get("cond"):
            m["cond"] = res["cond"]
            self.emit("death" if res["cond"] == 2 else "unconscious", member=slot)

    # -- phase 2 (LR-35) ---------------------------------------------------

    def phase2(self):
        c = self.combat
        actors = []
        orders = c.get("orders") or {}
        for i, m in enumerate(self.party):
            if not _alive(m):
                continue
            order = orders.get(str(i + 1)) or []
            # LR-35: actors are the members with a phase 2 order. A member whose
            # order was a phase 1 attack (fire) does not act in phase 2 even if
            # it jammed or ran dry during phase 1.
            if not order or order[0] in ("fire", "wait", "dead", "flee"):
                continue
            actors.append({"side": "party", "slot": i + 1, "speed": self.member_speed(m)})
        for gi, g in enumerate(c["groups"]):
            if g["mob"].get("weaponType", 0) >= 3:
                continue
            for mi, hp in enumerate(g["hp"]):
                if hp <= 0:
                    continue
                actors.append({"side": "monster", "group": gi, "index": mi,
                               "speed": g["mob"].get("combatRating", 0)})
        for a in rules.speed_order(actors):
            if c.get("over"):
                return
            if a["side"] == "party":
                self.member_phase2(a["slot"])
            else:
                # LR-35: an actor that died earlier in the phase is skipped.
                if c["groups"][a["group"]]["hp"][a["index"]] <= 0:
                    continue
                self.monster_phase2(a["group"], a["index"])
            if self.check_end():
                return

    def member_speed(self, member):
        return (member.get("attrs") or {}).get("SPD", 0)

    def member_phase2(self, slot):
        m = self.party[slot - 1]
        if not _alive(m):
            return
        order = (self.combat.get("orders") or {}).get(str(slot)) or []
        kind = order[0] if order else None
        if kind == "reload":
            cap = self.reload(m)
            if cap:
                self.emit("reload", member=slot, status=cap)
            return
        if kind == "unjam" or m.get("jammed"):
            self.unjam(slot)
            return
        rec, _iid = self.member_weapon(m)
        if kind == "fire" and rec is not None and self.weapon_ammo(m) > 0:
            self.fire(slot, rec)
            return
        if kind == "advance":
            self.advance()
            return
        if self.combat_band() <= 1:
            self.melee_attack(slot)
        else:
            self.advance()

    def fire(self, slot, rec):
        m = self.party[slot - 1]
        target = self.pick_monster_target()
        if target is None:
            return
        self.spend_ammo(m)
        need = rules.ranged_need(self.skill_level(m, rec.get("skill", 0)),
                                 (m.get("attrs") or {}).get("AGL", 0),
                                 target["ac"], self.combat_band())
        roll = self.rng.d100()
        hit = roll <= need
        ev = {"side": "party", "member": slot, "group": target["group"] + 1,
              "target": target["index"] + 1, "need": need, "roll": roll, "hit": hit}
        if hit:
            n, s = weapon_dice(rec)
            dmg = self.rng.dice(n, s)
            ev["damage"] = dmg
        self.emit("attack", **ev)
        if hit:
            self.damage_monster(target["group"], target["index"], dmg)

    def melee_attack(self, slot):
        m = self.party[slot - 1]
        target = self.pick_monster_target()
        if target is None:
            return
        rec, _iid = self.member_weapon(m)
        level = self.skill_level(m, rec.get("skill", 0)) if rec else 0
        # LR-35: the melee need uses AGL (the damage bonus uses STR).
        need = rules.melee_need(level, (m.get("attrs") or {}).get("AGL", 0), target["ac"])
        roll = self.rng.d100()
        hit = roll <= need
        ev = {"side": "party", "member": slot, "group": target["group"] + 1,
              "target": target["index"] + 1, "need": need, "roll": roll, "hit": hit}
        if hit:
            if rec is not None:
                n, s = weapon_dice(rec)
            else:
                n, s = 1, 2
            dmg = self.rng.dice(n, s) + rules.melee_damage_bonus(
                (m.get("attrs") or {}).get("STR", 0))
            ev["damage"] = dmg
        self.emit("attack", **ev)
        if hit:
            self.damage_monster(target["group"], target["index"], dmg)

    def monster_phase2(self, gi, mi):
        c = self.combat
        g = c["groups"][gi]
        mob = g["mob"]
        target = self.pick_random_member()
        if target is None:
            return
        m = self.party[target["slot"] - 1]
        need = rules.monster_need(mob.get("combatRating", 0), m.get("ac", 0),
                                  self.combat_band())
        roll = self.rng.d100()
        hit = roll <= need
        ev = {"side": "monsters", "group": gi + 1, "attacker": mi + 1, "member": target["slot"],
              "need": need, "roll": roll, "hit": hit}
        if hit:
            dmg = self.rng.dice(mob.get("randomDamage", 0), 6) + mob.get("fixedDamage", 0)
            ev["damage"] = dmg
            self.apply_member_damage(target["slot"], dmg)
        self.emit("attack", **ev)

    def unjam(self, slot):
        m = self.party[slot - 1]
        level = self.skill_level(m, GUNSMITHING)
        res = rules.skill_check(self.rng, level, (m.get("attrs") or {}).get("IQ", 0), 0)
        self.emit("check", member=slot, skill=GUNSMITHING, level=level, **res)
        if res.get("success"):
            m["jammed"] = False
            # LR-39: success sets the weapon status to 0 (empty, so a reload
            # follows on the next round).
            self.set_weapon_status(m, 0)
            self.emit("unjammed", member=slot)

    def advance(self):
        c = self.combat
        band = self.combat_band()
        new = max(1, band - 1)
        for g in c["groups"]:
            if any(hp > 0 for hp in g["hp"]):
                g["band"] = min(g.get("band", band), new)
        c["band"] = new
        self.emit("advance", band=new)

    def damage_monster(self, gi, mi, dmg):
        c = self.combat
        g = c["groups"][gi]
        if g["hp"][mi] <= 0:
            return
        g["hp"][mi] -= dmg
        if g["hp"][mi] <= 0:
            c["kills"] += 1
            c["last_death_round"] = c["round"]
            self.emit("monster_dies", group=gi + 1, index=mi + 1)

    # -- rounds ------------------------------------------------------------

    def reset_phase(self):
        c = self.combat
        c["fired"] = set()
        c["pending_monsters"] = [[0] * len(g["hp"]) for g in c["groups"]]
        c["pending_members"] = {}

    def check_end(self):
        c = self.combat
        if c is None or c.get("over"):
            return True
        if not any(hp > 0 for g in c["groups"] for hp in g["hp"]):
            self.victory()
            return True
        if not any(_alive(m) for m in self.party):
            self.defeat()
            return True
        return False

    def combat_round(self):
        c = self.combat
        if c is None:
            return
        rnd = c["round"] if c["round"] else 1
        c["round"] = rnd
        orders = self.auto_orders()
        c["orders"] = orders
        self.emit("round_orders", round=rnd, orders=orders)
        self.emit("round_start", round=rnd)
        self.reset_phase()
        self.party_phase1()
        self.monster_phase1()
        self.apply_phase1()
        if self.check_end():
            return
        self.phase2()
        if self.check_end():
            return
        self.end_of_round()

    def surprise_round(self):
        c = self.combat
        if c is None:
            return
        c["round"] = 0
        self.emit("round_start", round=0)
        self.reset_phase()
        self.monster_phase1()
        self.apply_phase1()
        if self.check_end():
            return
        self.end_of_round()

    # -- victory and defeat (LR-44 to LR-46) -------------------------------

    def victory(self):
        c = self.combat
        if c is None or c.get("over"):
            return
        c["over"] = True
        rounds = c.get("last_death_round") or c["round"]
        self.emit("combat_end", result="victory", rounds=rounds)
        total = 0
        for gi, g in enumerate(c["groups"]):
            mob = g["mob"]
            killed = sum(1 for hp in g["hp"] if hp <= 0)
            total += killed * mob.get("sturdiness", 0) * (mob.get("armorClass", 0) + 1)
        alive = [i + 1 for i, m in enumerate(self.party) if not m.get("cond") == 2]
        share = total // len(alive) if alive else 0
        for slot in range(1, len(self.party) + 1):
            m = self.party[slot - 1]
            m["xp"] = m.get("xp", 0) + share
            self.emit("xp", member=slot, delta=share, total=m["xp"])
            lvl0 = m.get("level", 1)
            lvl = rules.level_after(lvl0, m["xp"])
            if lvl > lvl0:
                m["level"] = lvl
                m["max_hp"] = rules.max_hp((m.get("attrs") or {}).get("STR", 0), lvl)
                # LR-46: curHP rises by the same amount unless the member is dead.
                if m.get("cond") != 2:
                    m["hp"] = m.get("hp", 0) + (m["max_hp"] - rules.max_hp(
                        (m.get("attrs") or {}).get("STR", 0), lvl0))
                # LR-46: unspent skill points rise by 2 per level and the rank
                # string becomes LABSTR table 3 string min(level, 7) - 1.
                m["skill_points"] = m.get("skill_points", 0) + 2 * (lvl - lvl0)
                m["rank"] = RANKS[min(lvl, 7) - 1]
                self.emit("promote", member=slot, level=lvl, max_hp=m["max_hp"],
                          rank=RANKS[min(lvl, 7) - 1])
        money = 5 * self.best_salvage() * c["kills"]
        if money:
            self.party[0]["money"] = self.party[0].get("money", 0) + money
            self.emit("money", member=1, delta=money, total=self.party[0]["money"])
        rec = c.get("rec")
        self.combat = None
        self.mode = "map"
        # LR-44: after the victory the encounter cell's tail is applied; if that
        # turns the cell into a LOOT cell, the loot fires at once (and its own
        # tail is applied afterwards).
        if rec is not None:
            self.apply_tail(rec, self.x, self.y)
            cls, _a = self.cell_class_action(self.x, self.y)
            if cls == 5:
                lrec = maps.record_at(self.sc.map(self.location), self.x, self.y)
                if lrec is not None:
                    self.apply_loot(lrec, self.x, self.y)

    def best_salvage(self):
        best = 0
        for m in self.party:
            if m.get("cond") == 2 or m.get("hp", 0) <= 0:
                continue
            best = max(best, self.skill_level(m, SALVAGE))
        return best

    def defeat(self):
        c = self.combat
        if c is None or c.get("over"):
            return
        c["over"] = True
        self.emit("combat_end", result="defeat")
        self.emit("game_over")
        self.combat = None
        self.mode = "gameover"
