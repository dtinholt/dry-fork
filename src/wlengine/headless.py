"""Headless driver (SPEC-06 section 5, SPEC-07 API).

The headless driver runs the engine over a compiled data directory with a
scripted list of input tokens and returns the event log plus the final state.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from . import containers, labstate, maps, rules, strings
from .combat import CombatMixin
from .errors import FormatError, RepeatLimitError, ScriptError

# SPEC-06 section 1: a token is one of these names or a single printable
# ASCII character.  Anything else is a malformed script (exit code 4).
NAMED_TOKENS = ("UP", "DOWN", "LEFT", "RIGHT", "ESC", "ENTER")


def is_token(key):
    if not isinstance(key, str):
        return False
    if key in NAMED_TOKENS:
        return True
    return len(key) == 1 and 0x20 <= ord(key) <= 0x7E

# ---------------------------------------------------------------------------
# scenario loading
# ---------------------------------------------------------------------------


def _load_scenario(data_dir):
    from . import scenario as scenario_mod
    loader = getattr(scenario_mod, "load", None)
    if loader is not None:
        return loader(data_dir)
    cls = getattr(scenario_mod, "Scenario", None)
    if cls is not None:
        for name in ("from_dir", "read", "load"):
            fn = getattr(cls, name, None)
            if fn is not None:
                return fn(data_dir)
        return cls(data_dir)
    raise FormatError("wlengine.scenario has no loader")


# ---------------------------------------------------------------------------
# engine
# ---------------------------------------------------------------------------


class Engine(CombatMixin):
    """One engine instance driven by a script of input tokens."""

    def __init__(self, data_dir, seed=None, options=None):
        self.data_dir = data_dir
        self.options = dict(options or {})
        self.sc = _load_scenario(data_dir)
        self.events = []
        self._seq = 0
        self.mode = "map"
        self.location = 0
        self.x = 0
        self.y = 0
        self.steps = 0
        self.day = 1
        self.hour = 0
        self.minute = 0
        self.prev_x = 0
        self.prev_y = 0
        self.prev_location = 0
        self.cell_changes = []
        self.rng = None
        self.seed = seed
        self.party = []
        self.serial = 0
        self.paragraph = 0
        self.shop = None
        self.pending = None
        self.pending_member = None
        self.pending_item = None
        self.pending_hook = None
        self.pending_cell = (0, 0)
        self.combat = None
        self.saved = {}
        self.script_seed = None
        self._items = None

    # -- event log ---------------------------------------------------------

    def emit(self, type_, **kw):
        ev = {"seq": self._seq, "type": type_}
        ev.update(kw)
        self._seq += 1
        self.events.append(ev)
        return ev

    def checkpoint(self, name):
        self.emit("checkpoint", name=name, state=self.snapshot())

    def snapshot(self):
        return {
            "location": self.location,
            "x": self.x,
            "y": self.y,
            "steps": self.steps,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "mode": self.mode,
            "cell_changes": self.sorted_cell_changes(),
            "rng_state": self.rng.state if self.rng is not None else None,
            "party": [self.member_snapshot(i + 1)
                      for i in range(len(self.party))],
        }

    def sorted_cell_changes(self):
        """SPEC-06 2.4: the snapshot's cell changes are sorted by
        (location, x, y) and a cell that changed more than once keeps only its
        last change.  (LABSTATE.BIN re-sorts by (location, y, x), LR-57.)"""
        last = {}
        for c in self.cell_changes:
            last[(c[0], c[1], c[2])] = list(c)
        return [last[k] for k in sorted(last, key=lambda k: (k[0], k[1], k[2]))]

    def member_snapshot(self, member):
        m = self.party[member - 1]
        return {
            "slot": member,
            "name": m.get("name", ""),
            "npc": m.get("npc", 0),
            "level": m.get("level", 1),
            "xp": m.get("xp", 0),
            "max_hp": m.get("max_hp", 0),
            "hp": m.get("hp", 0),
            "cond": m.get("cond", 0),
            "money": m.get("money", 0),
            "ac": m.get("ac", 0),
            "rank": m.get("rank", 0),
            "skill_points": m.get("skill_points", 0),
            "items": [list(it) for it in m.get("items", [])],
            "weapon_slot": m.get("weapon_slot", -1),
            "armour_slot": m.get("armour_slot", -1),
        }

    # -- item table --------------------------------------------------------

    def item_table(self):
        if self._items is not None:
            return self._items
        tbl = getattr(self.sc, "items", None)
        if tbl is None:
            fn = getattr(self.sc, "item_table", None)
            if fn is not None:
                tbl = fn()
        if tbl is None:
            tbl = {}
        if isinstance(tbl, list):
            tbl = {i + 1: v for i, v in enumerate(tbl)}
        self._items = tbl
        return tbl

    def item(self, iid):
        return self.item_table().get(iid, {})

    def item_price(self, iid):
        it = self.item(iid)
        if isinstance(it, dict):
            return it.get("price", 0)
        return 0

    def item_name(self, iid):
        it = self.item(iid)
        if isinstance(it, dict):
            return it.get("name", "")
        return ""

    # -- new game ----------------------------------------------------------

    def new_game(self, seed):
        self.seed = seed
        self.rng = rules.Rng(seed)
        start = self.sc.start
        self.location = start["location"]
        self.x = start["x"]
        self.y = start["y"]
        self.hour = start.get("hour", 8)
        self.minute = start.get("minute", 0)
        self.day = start.get("day", 1)
        self.steps = 0
        self.cell_changes = []
        self.mode = "map"
        self.party = self.sc.premade_party()
        self.emit("new_game", seed=seed)
        self.paragraph = start.get("paragraph", 1)
        self.emit("paragraph", n=self.paragraph)

    # -- script ------------------------------------------------------------

    def run_script(self, script):
        for item in script:
            if isinstance(item, dict):
                if "checkpoint" in item:
                    self.checkpoint(item["checkpoint"])
                elif "repeat_until" in item:
                    self.run_repeat(item)
                else:
                    raise ScriptError("unknown script item %r" % (item,))
            else:
                if not is_token(item):
                    raise ScriptError("unknown script token %r" % (item,))
                self.input(item)
        return self.events

    def run_repeat(self, item):
        raise ScriptError("repeat_until not supported yet")

    def input(self, key):
        self.emit("input", key=key)
        if not self.dispatch(str(key)):
            self.emit("ignored", key=key)

    def dispatch(self, key):
        low = key.lower()
        if self.pending == "look":
            self.pending = None
            if key in ("UP", "DOWN", "LEFT", "RIGHT"):
                self.do_look(key)
                return True
            return False
        if self.pending == "char_member" and key.isdigit():
            member = int(key)
            if 1 <= member <= len(self.party):
                self.pending = None
                self.pending_member = member
                self.mode = "char"
                self.emit("char_open", member=member)
                return True
            return False
        if self.mode == "shop":
            return self.shop_key(key, low)
        if self.mode == "char":
            return self.char_key(key, low)
        if self.mode == "combat":
            return self.combat_key(key, low)
        handler = getattr(self, "key_" + low, None)
        if handler is None:
            return False
        return handler() is not False

    # -- look (SPEC-06 section 3) ------------------------------------------

    def _pos(self):
        x = getattr(self, "x", None)
        y = getattr(self, "y", None)
        if x is None or y is None:
            x = getattr(self, "px", x)
            y = getattr(self, "py", y)
        return x, y

    def key_l(self):
        self.pending = "look"
        return True

    def do_look(self, direction):
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1),
                  "LEFT": (-1, 0), "RIGHT": (1, 0)}[direction]
        x, y = self._pos()
        nx, ny = x + dx, y + dy
        m = self.sc.map(self.location)
        cells = m.get("cells", {})
        images = cells.get("image") or []
        classes = cells.get("actionClass") or []
        img = None
        cls = 0
        if 0 <= ny < len(images) and 0 <= nx < len(images[ny]):
            img = images[ny][nx]
        if 0 <= ny < len(classes) and 0 <= nx < len(classes[ny]):
            cls = classes[ny][nx]
        if img is None:
            img = self.border_image()
        self.emit("look", x=nx, y=ny, image=img, action_class=cls)

    def border_image(self):
        m = self.sc.map(self.location)
        info = m.get("info") or {}
        for key in ("border", "border_image", "borderImage"):
            if key in info and info[key] is not None:
                return info[key]
        return 0

    # -- inventory ---------------------------------------------------------

    def member_items(self, member):
        return self.party[member - 1].setdefault("items", [])

    def add_item(self, member, iid, count=1):
        items = self.member_items(member)
        for entry in items:
            if entry[0] == iid:
                entry[1] += count
                return entry
        items.append([iid, count])
        return items[-1]

    def add_item_status(self, member, iid, status):
        """LR-49: loot goes into the first free item slot with its status."""
        items = self.member_items(member)
        items.append([iid, status])
        return items[-1]

    def remove_item(self, member, iid, count=1):
        items = self.member_items(member)
        for i, entry in enumerate(items):
            if entry[0] == iid:
                entry[1] -= count
                if entry[1] <= 0:
                    items.pop(i)
                return True
        return False

    def item_slot(self, member, iid):
        for i, entry in enumerate(self.member_items(member)):
            if entry[0] == iid:
                return i
        return -1

    # -- shop --------------------------------------------------------------

    def shop_items(self):
        if self.shop is None:
            return []
        return list(self.shop.get("items", []))

    def shop_recs(self):
        if self.shop is None:
            return []
        return self.shop.get("recs", [])

    def item_record(self, iid):
        recs = self.shop_recs()
        if not recs:
            recs = self.sc.shops[0]["items"] if self.sc.shops else []
        if 1 <= iid <= len(recs):
            return recs[iid - 1]
        return None

    def best_skill(self, skill):
        best = 0
        for m in self.party:
            if m.get("hp", 0) <= 0:
                continue
            best = max(best, self.skill_level(m, skill))
        return best

    def haggling(self):
        return min(5, self.best_skill(20))

    def buy_price(self, price):
        h = self.haggling()
        return price * (100 - 5 * h) // 100

    def sell_price(self, price):
        h = self.haggling()
        return price * (50 + 5 * h) // 100

    def shop_key(self, key, low):
        if self.pending == "buy_item" and low.isalpha():
            idx = ord(low) - ord("a")
            items = self.shop_items()
            if 0 <= idx < len(items):
                self.pending_item = items[idx]
                self.pending = "buy_member"
                self.emit("prompt", prompt="member")
                return True
            return False
        if self.pending == "buy_member" and low.isdigit():
            member = int(low)
            if 1 <= member <= len(self.party):
                self.pending = None
                self.shop_buy(member, self.pending_item)
                return True
            return False
        if self.pending == "sell_member" and low.isdigit():
            member = int(low)
            if 1 <= member <= len(self.party):
                self.pending_member = member
                self.pending = "sell_item"
                self.emit("prompt", prompt="item_slot")
                return True
            return False
        if self.pending == "sell_item" and low.isalpha():
            idx = ord(low) - ord("a")
            items = self.member_items(self.pending_member)
            if 0 <= idx < len(items):
                self.pending = None
                self.shop_sell(self.pending_member, items[idx][0])
                return True
            return False
        if self.pending == "char_member" and low.isdigit():
            member = int(low)
            if 1 <= member <= len(self.party):
                self.pending = None
                self.pending_member = member
                self.mode = "char"
                self.emit("char_open", member=member)
                return True
            return False
        if low == "b":
            self.pending = "buy_item"
            self.emit("prompt", prompt="buy_item", items=self.shop_items())
            return True
        if low == "s":
            self.pending = "sell_member"
            self.emit("prompt", prompt="member")
            return True
        if low == "c":
            self.pending = "char_member"
            self.emit("prompt", prompt="member")
            return True
        if low == "x":
            self.mode = "map"
            self.shop = None
            self.pending = None
            self.emit("shop_close")
            return True
        return False

    def shop_buy(self, member, iid):
        rec = self.item_record(iid) or {}
        price = self.buy_price(rec.get("price", 0))
        m = self.party[member - 1]
        m["money"] = m.get("money", 0) - price
        self.emit("money", member=member, delta=-price, total=m["money"])
        items = self.member_items(member)
        itype = rec.get("type", 0)
        if itype == 3:  # ammunition stacks
            for i, entry in enumerate(items):
                if entry[0] == iid and entry[1] < 127:
                    entry[1] += 1
                    self.emit("buy", member=member, item=iid, price=price,
                              slot=i + 1, status=entry[1])
                    return
        status = 1 if itype == 3 else (rec.get("capacity", 0) if itype == 5 else 0)
        slot = None
        for i, entry in enumerate(items):
            if entry[0] == 0:
                slot = i
                break
        if slot is None:
            if len(items) >= 30:
                self.emit("message", location=self.location, string=3)
                return
            items.append([iid, status])
            slot = len(items) - 1
        else:
            items[slot] = [iid, status]
        self.emit("buy", member=member, item=iid, price=price, slot=slot + 1,
                  status=status)

    def shop_sell(self, member, iid):
        rec = self.item_record(iid) or {}
        if rec.get("type", 0) == 7:
            self.emit("message", location=self.location, string=31)
            return
        price = self.sell_price(rec.get("price", 0))
        slot = self.item_slot(member, iid)
        self.emit("sell", member=member, item=iid, price=price, slot=slot + 1)
        items = self.member_items(member)
        if 0 <= slot < len(items):
            items[slot] = [0, 0]
        m = self.party[member - 1]
        if m.get("armour_slot", 0) == slot + 1:
            m["armour_slot"] = 0
            self.recompute_ac(member)
        if m.get("weapon_slot", 0) == slot + 1:
            m["weapon_slot"] = 0
        m["money"] = m.get("money", 0) + price
        self.emit("money", member=member, delta=price, total=m["money"])

    def recompute_ac(self, member):
        m = self.party[member - 1]
        attrs = m.get("attrs") or {}
        agl = attrs.get("AGL", m.get("agility", 0))
        bonus = 0
        aslot = m.get("armour_slot", 0)
        items = m.get("items", [])
        if aslot and 0 <= aslot - 1 < len(items):
            rec = self.item_record(items[aslot - 1][0])
            if rec:
                bonus = rec.get("damage", 0)
        evasion = self.skill_level(m, 11)
        m["ac"] = agl // 5 + bonus + evasion

    # -- character screen --------------------------------------------------

    def char_key(self, key, low):
        if low == "e":
            self.pending = "equip_item"
            self.emit("prompt", prompt="item_slot")
            return True
        if low == "x":
            self.mode = "map"
            self.pending = None
            self.emit("char_close")
            return True
        if self.pending == "equip_item" and low.isalpha():
            idx = ord(low) - ord("a")
            items = self.member_items(self.pending_member)
            if 0 <= idx < len(items):
                self.pending = None
                self.equip(self.pending_member, idx, items[idx][0])
                return True
            return False
        return False

    def equip(self, member, slot, iid):
        self.party[member - 1]["armour_slot"] = slot + 1
        self.recompute_ac(member)
        ac = self.party[member - 1]["ac"]
        self.emit("equip", member=member, slot=slot + 1, item=iid, ac=ac)

    # -- combat ------------------------------------------------------------

    def combat_key(self, key, low):
        if low == "a":
            self.combat_round()
            return True
        if low == "f":
            self.flee()
            return True
        return False

    def build_groups(self, rec):
        """LR-26, LR-28: groups from the map's monster table and the record."""
        m = self.sc.map(self.location)
        mobs = list((m or {}).get("mobs", []))
        groups = rules.build_groups(self.rng, mobs, rec or {})
        for g in groups:
            mob = mobs[g["monster"] - 1]
            name = mob.get("name", b"")
            if isinstance(name, bytes):
                name = name.split(b"\x0a")[0].decode("latin-1")
            else:
                name = str(name).split("\n")[0]
            g["mob"] = mob
            g["monster"] = name
        return groups

    def group_event(self, g):
        out = {k: (list(v) if isinstance(v, list) else v) for k, v in g.items() if k != "mob"}
        return out

    ATTR_ORDER = ("STR", "IQ", "LCK", "SPD", "AGL", "CHA")
    ATTR_OFFSETS = {14: 0, 15: 1, 16: 2, 17: 3, 18: 4, 20: 5}

    def attr_value(self, member, skill):
        """LR-13: the member's value of the attribute linked to ``skill``."""
        idx = self.skill_attribute(skill)
        attrs = member.get("attrs") or {}
        return attrs.get(self.ATTR_ORDER[idx], 0)

    # -- movement ----------------------------------------------------------

    def key_down(self):
        self.move(0, 1)

    def key_up(self):
        self.move(0, -1)

    def key_left(self):
        self.move(-1, 0)

    def key_right(self):
        self.move(1, 0)

    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        m = self.sc.map(self.location)
        size = m["size"]
        if not (0 <= nx < size and 0 <= ny < size):
            self.emit("blocked", x=nx, y=ny)
            return
        cls, _action = self.cell_class_action(nx, ny)
        if cls == 11 or not maps.is_passable(m, nx, ny):
            self.bump(nx, ny)
            return
        ox, oy = self.x, self.y
        self.x, self.y = nx, ny
        self.steps += 1
        self.emit("move", location=self.location, x=self.x, y=self.y, steps=self.steps)
        self.advance_time(self.step_minutes())
        self.after_move(ox, oy)

    def step_minutes(self):
        m = self.sc.map(self.location)
        tp = m["info"].get("timePerStep", 256)
        return tp >> 8

    def cell_class_action(self, x, y):
        m = self.sc.map(self.location)
        size = m["size"]
        if not (0 <= x < size and 0 <= y < size):
            return 0, 0
        return m["cells"]["actionClass"][y][x], m["cells"]["action"][y][x]

    def show_message(self, index):
        if not index:
            return
        text = self.sc.map_string(self.location, index)
        if text.startswith("Read paragraph ") and text.endswith("."):
            body = text[len("Read paragraph "):-1]
            if body.isdigit():
                self.emit("paragraph", n=int(body))
                return
        self.emit("message", location=self.location, string=index)

    def advance_time(self, minutes):
        before_hour = self.hour
        self.minute += minutes
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        rolled = 0
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
            rolled += 1
        # SPEC-04 LR-16: the hour's natural healing is emitted before the day
        # rollover event.
        if self.hour != before_hour:
            self.natural_heal()
        for _ in range(rolled):
            self.emit("day", day=self.day)

    def natural_heal(self):
        healed = []
        for i, m in enumerate(self.party):
            if m.get("cond", 0) != 0:
                continue
            if m.get("hp", 0) < m.get("max_hp", 0):
                m["hp"] = m.get("hp", 0) + 1
                healed.append(i + 1)
        if healed:
            self.emit("natural_heal", members=healed)

    def after_move(self, ox=None, oy=None):
        m = self.sc.map(self.location)
        cls, action = self.cell_class_action(self.x, self.y)
        rec = maps.record_at(m, self.x, self.y)
        if cls == 10:
            self.transition(rec, ox, oy)
        elif cls == 6:
            self.open_shop(rec)
        elif cls == 3:
            self.start_encounter(rec)
        elif cls == 1 and rec is not None:
            for msg in rec.get("messages", []):
                self.show_message(msg)
            self.apply_tail(rec, self.x, self.y)
        elif cls == 5 and rec is not None:
            self.apply_loot(rec, self.x, self.y)
        elif cls == 4 and rec is not None and not rec.get("impassable"):
            # SPEC-03 9.6: set the cell image to r.tile, move, show r.message,
            # apply tail.  The image change is logged even when it is a no-op.
            tile = rec.get("tile")
            if tile is not None:
                m["cells"]["image"][self.y][self.x] = tile
                self.cell_change(self.x, self.y, cls, action, tile)
            self.show_message(rec.get("message", 0))
            self.apply_tail(rec, self.x, self.y)

    def transition(self, rec, ox=None, oy=None):
        loc, x, y = maps.resolve_transition(self.sc.tables, rec, self.x, self.y,
                                            (self.location, self.x, self.y))
        if rec.get("location", 0) != 255:
            self.prev_location = self.location
            self.prev_x = self.x if ox is None else ox
            self.prev_y = self.y if oy is None else oy
        self.location, self.x, self.y = loc, x, y
        self.emit("map_change", location=loc, x=x, y=y)

    def bump(self, nx, ny):
        m = self.sc.map(self.location)
        rec = maps.record_at(m, nx, ny)
        cls, action = self.cell_class_action(nx, ny)
        self.emit("bump", x=nx, y=ny, action_class=cls, action=action)
        self.bump_effect(rec, nx, ny, cls)

    def bump_effect(self, rec, nx, ny, cls=None):
        if cls is None:
            cls, _a = self.cell_class_action(nx, ny)
        if cls == 11:
            self.bump_blocked(rec, nx, ny)
        elif cls == 4:
            if rec is not None and rec.get("impassable"):
                self.show_message(rec.get("message", 0))
                if self.sc.hook(self.location, nx, ny):
                    self.run_hook_at(nx, ny)
                else:
                    self.apply_tail(rec, nx, ny)
            elif rec is not None:
                self.show_message(rec.get("message", 0))
                self.apply_tail(rec, nx, ny)
        elif cls == 3:
            self.start_encounter(rec)

    def bump_blocked(self, rec, nx, ny):
        if rec is not None:
            self.show_message(rec.get("message", 0))
            self.apply_tail(rec, nx, ny)
        self.run_hook_at(nx, ny)

    def run_hook_at(self, nx, ny):
        hook = self.sc.hook(self.location, nx, ny)
        if hook:
            self.run_hook(hook, nx, ny)

    def apply_tail(self, rec, x, y):
        tail = maps.apply_tail(rec)
        if tail is None:
            return
        m = self.sc.map(self.location)
        m["cells"]["actionClass"][y][x] = tail[0]
        m["cells"]["action"][y][x] = tail[1]
        img = maps.image_at(m, x, y)
        self.cell_change(x, y, tail[0], tail[1], img)
        newrec = maps.record_at(m, x, y)
        if newrec is not None and "tile" in newrec:
            newimg = newrec["tile"]
            if newimg != img:
                m["cells"]["image"][y][x] = newimg
                self.cell_change(x, y, tail[0], tail[1], newimg)

    def apply_loot(self, rec, x, y):
        for item in rec.get("items", []):
            if isinstance(item, (list, tuple)):
                iid = item[0]
                fixed = bool(item[1]) if len(item) > 1 else True
                amount = item[2] if len(item) > 2 else 0
            else:
                iid, fixed, amount = item, True, 0
            status = amount if fixed else self.rng.rnd(amount)
            placed = False
            for i, m in enumerate(self.party):
                if len(m.get("items", [])) < 30:
                    self.add_item_status(i + 1, iid, status)
                    slot = self.item_slot(i + 1, iid) + 1
                    self.emit("item_gain", member=i + 1, item=iid, slot=slot,
                              status=status)
                    placed = True
                    break
            if not placed:
                self.emit("item_lost", item=iid)
        cash = rec.get("cash")
        if cash:
            if isinstance(cash, (list, tuple)):
                fixed = bool(cash[0]) if len(cash) > 1 else True
                amount = cash[1] if len(cash) > 1 else cash[0]
            else:
                fixed, amount = True, cash
            amount = amount if fixed else self.rng.rnd(amount)
            m = self.party[0]
            m["money"] = m.get("money", 0) + amount
            self.emit("money", member=1, delta=amount, total=m["money"])
        self.apply_tail(rec, x, y)

    # -- cell changes ------------------------------------------------------

    def cell_change(self, x, y, action_class, action, image):
        self.cell_changes.append([self.location, x, y, action_class, action,
                                  image])
        self.emit("cell_change", location=self.location, x=x, y=y,
                  action_class=action_class, action=action, image=image)

    # -- hooks -------------------------------------------------------------

    def run_hook(self, hook, nx, ny):
        kind = hook.get("kind")
        if kind == "win":
            self.hook_win(hook, nx, ny)
        elif kind == "recruit":
            self.hook_recruit(hook, nx, ny)
        elif kind == "healer":
            self.hook_healer(hook, nx, ny)
        elif kind == "lock":
            self.bump_lock(None, nx, ny)

    def hook_win(self, hook, nx, ny):
        item = hook.get("item")
        if item is not None and not self.party_has(item):
            para = self.hook_get(hook, "not_yet_paragraph", "not_yet")
            if para:
                self.emit("paragraph", n=para)
            return
        para = self.hook_get(hook, "win_paragraph", "win_para")
        if para:
            self.emit("paragraph", n=para)
        self.mode = "won"
        self.emit("win", steps=self.steps, day=self.day,
                  minutes=self.hour * 60 + self.minute)

    def hook_get(self, hook, *names):
        for name in names:
            if name in hook and hook[name] is not None:
                return hook[name]
        return None

    def hook_recruit(self, hook, nx, ny):
        para = self.hook_get(hook, "paragraph")
        if para:
            self.emit("paragraph", n=para)
        self.pending = "recruit"
        self.pending_hook = hook
        self.pending_cell = (nx, ny)
        self.emit("prompt", prompt="recruit")

    def hook_healer(self, hook, nx, ny):
        self.pending = "heal"
        self.pending_hook = hook
        self.pending_cell = (nx, ny)
        self.emit("prompt", prompt="heal", price=hook.get("price", 0))

    # -- locks -------------------------------------------------------------

    def bump_lock(self, rec, nx, ny):
        hook = self.sc.hook(self.location, nx, ny)
        if hook is None:
            return
        key_item = hook.get("key_item")
        if key_item is not None:
            member = self.member_with_item(key_item)
            if member is not None:
                self.emit("key_used", member=member, item=key_item)
                self.unlock(nx, ny, hook, member, xp=0)
                return
        member = self.pick_member(hook.get("skill", 0))
        skill = hook.get("skill", 0)
        level = self.skill_level(self.party[member - 1], skill)
        attr = self.attr_value(self.party[member - 1], skill)
        need = rules.check_need(level, attr, hook.get("difficulty", 0),
                                bool(hook.get("tool_item")))
        roll = self.rng.d100()
        success = roll <= need
        self.emit("check", member=member, skill=skill, level=level, need=need,
                  roll=roll, success=success)
        if success:
            self.unlock(nx, ny, hook, member)
        else:
            self.show_message(hook.get("fail_message", 0))

    def unlock(self, nx, ny, hook, member, xp=10):
        self.emit("unlock", x=nx, y=ny)
        m = self.sc.map(self.location)
        rec = maps.record_at(m, nx, ny)
        img = maps.image_at(m, nx, ny)
        tail = maps.apply_tail(rec) if rec is not None else None
        if tail is None:
            tail = (0, 0)
        m["cells"]["actionClass"][ny][nx] = tail[0]
        m["cells"]["action"][ny][nx] = tail[1]
        self.cell_change(nx, ny, tail[0], tail[1], img)
        newimg = img
        newrec = maps.record_at(m, nx, ny)
        if newrec is not None and "tile" in newrec:
            newimg = newrec["tile"]
            m["cells"]["image"][ny][nx] = newimg
        self.cell_change(nx, ny, tail[0], tail[1], newimg)
        if xp:
            mm = self.party[member - 1]
            mm["xp"] = mm.get("xp", 0) + xp
            self.emit("xp", member=member, delta=xp, total=mm["xp"])
        self.show_message(hook.get("success_message", 0))

    def member_with_item(self, item):
        """LR-21: the lowest-slot member who is not dead and carries the item.

        Carrying is presence in the item list; the status byte is irrelevant
        (a key card sits in the list with status 0).
        """
        for i, m in enumerate(self.party):
            if m.get("cond", 0) == 2:
                continue
            for it in m.get("items", []):
                if it[0] == item:
                    return i + 1
        return None

    def pick_member(self, skill):
        idx = self.skill_attribute(skill)
        best = 1
        best_key = None
        for i, m in enumerate(self.party):
            if m.get("cond", 0) != 0:
                continue
            lvl = self.skill_level(m, skill)
            attrs = m.get("attrs") or {}
            a = attrs.get(self.ATTR_ORDER[idx], 0)
            key = (lvl, a, -i)
            if best_key is None or key > best_key:
                best_key = key
                best = i + 1
        return best

    def skill_attribute(self, skill):
        """LR-6: LABSKILL byte 1 is a record offset; map it to an attribute."""
        tbl = getattr(self.sc, "skill_table", None)
        if tbl:
            try:
                off = tbl[skill][2]
            except Exception:  # noqa: BLE001
                off = None
            if off in self.ATTR_OFFSETS:
                return self.ATTR_OFFSETS[off]
        return 1

    def attr_value(self, member, skill):
        """The member's value for the attribute that governs ``skill``."""
        idx = self.skill_attribute(skill)
        attrs = member.get("attrs") or {}
        return attrs.get(self.ATTR_ORDER[idx], 0)

    def end_of_round(self):
        """LR-36: living melee groups above band 1 close in, then round += 1."""
        c = self.combat
        if c is None:
            return
        for i, g in enumerate(c["groups"]):
            mob = g.get("mob") or {}
            melee = mob.get("weaponType", 0) < 3
            if melee and g["band"] > 1 and any(h > 0 for h in g["hp"]):
                g["band"] -= 1
                self.emit("group_closes", group=i + 1, band=g["band"])
        c["round"] += 1

    def party_has(self, item):
        for m in self.party:
            for it in m.get("items", []):
                if it[0] == item:
                    return True
        return False

    def skill_level(self, member, skill):
        for sid, lvl in member.get("skills", []):
            if sid == skill:
                return lvl
        return 0

    # -- shops -------------------------------------------------------------

    def open_shop(self, rec):
        n = rec.get("shop", 0)
        self.show_message(rec.get("message", 0))
        self.mode = "shop"
        recs = self.sc.shops[n]["items"] if n in self.sc.shops else []
        items = [i + 1 for i, it in enumerate(recs) if 1 <= it.get("stock", 0) <= 255]
        self.shop = {"number": n, "recs": recs, "items": items}
        self.emit("shop_open", shop=n)

    def key_b(self):
        if self.mode != "shop":
            return False
        self.pending = "buy_item"
        self.emit("prompt", prompt="buy_item", items=list(self.shop["items"]))

    def key_s(self):
        if self.mode == "shop":
            self.pending = "sell_member"
            self.emit("prompt", prompt="member")
            return
        self.serial += 1
        self.save_game()

    def key_c(self):
        self.pending = "char_member"
        self.emit("prompt", prompt="member")

    def key_e(self):
        if self.mode != "char":
            return False
        self.pending = "equip_item"
        self.emit("prompt", prompt="item_slot")

    def key_x(self):
        if self.mode == "shop":
            self.mode = "map"
            self.shop = None
            self.pending = None
            self.emit("shop_close")
            return
        if self.mode == "char":
            self.mode = "map"
            self.pending = None
            self.emit("char_close")
            return
        return False

    def key_o(self):
        self.emit("prompt", prompt="load")
        self.pending = "load"

    def key_y(self):
        if self.pending == "load":
            self.pending = None
            self.load_game()
            return
        if self.pending == "recruit":
            self.pending = None
            self.do_recruit()
            return
        if self.pending == "heal":
            self.pending = None
            self.do_heal()
            return
        return False

    def key_n(self):
        if self.pending in ("recruit", "heal", "load"):
            self.pending = None
            return
        return False

    def do_recruit(self):
        hook = self.pending_hook
        nx, ny = self.pending_cell
        m = self.sc.map(self.location)
        img = self.hook_get(hook, "cleared_image", "image")
        m["cells"]["actionClass"][ny][nx] = 0
        m["cells"]["action"][ny][nx] = 0
        m["cells"]["image"][ny][nx] = img
        self.cell_change(nx, ny, 0, 0, img)
        slot = len(self.party) + 1
        idx = hook.get("npc", 0) or 0
        npcs = m.get("npcs", [])
        ch = npcs[idx] if 0 <= idx < len(npcs) else {}
        self.party.append(self.member_from_character(ch, slot))
        self.emit("recruit", location=self.location, npc=idx, slot=slot)

    def member_from_character(self, ch, slot):
        aff = ch.get("afflictions", 0)
        cond = 2 if aff & 2 else (1 if aff & 1 else 0)
        return {
            "slot": slot, "name": ch.get("name", ""), "npc": ch.get("npc", 0),
            "level": ch.get("level", 1), "xp": ch.get("experience", 0),
            "max_hp": ch.get("maxCon", 0), "hp": ch.get("curCon", 0),
            "cond": cond, "money": ch.get("money", 0),
            "ac": ch.get("armorClass", 0), "rank": ch.get("rank", ""),
            "skill_points": ch.get("skillPoints", 0),
            "items": [list(x) for x in ch.get("items", [])],
            "skills": [list(x) for x in ch.get("skills", [])],
            "weapon_slot": ch.get("weaponSlot", 0),
            "armour_slot": ch.get("armorSlot", 0),
            "attrs": {"STR": ch.get("strength", 0), "IQ": ch.get("intelligence", 0),
                      "LCK": ch.get("luck", 0), "SPD": ch.get("speed", 0),
                      "AGL": ch.get("agility", 0), "CHA": ch.get("charisma", 0)},
            "gender": ch.get("gender", 0), "nationality": ch.get("nationality", 0),
            "game_won": ch.get("gameWon", 0),
        }

    def do_heal(self):
        hook = self.pending_hook
        price = hook.get("price", 0)
        m = self.party[0]
        m["money"] = m.get("money", 0) - price
        self.emit("money", member=1, delta=-price, total=m["money"])
        for mm in self.party:
            mm["hp"] = mm.get("max_hp", 0)
        self.emit("heal_all", price=price)

    # -- rest --------------------------------------------------------------

    def key_r(self):
        self.advance_time(60)
        self.emit("rest")

    # -- save / load -------------------------------------------------------

    def save_game(self):
        self.emit("save", serial=self.serial)
        self.saved[self.serial] = self.snapshot()
        try:
            self.write_save_files()
        except Exception:  # noqa: BLE001
            pass

    def write_save_files(self):
        dd = Path(self.data_dir)
        # LABSTATE.BIN next to GAME1 (LR-54, LR-57)
        cc = self.sorted_cell_changes()
        blob = labstate.encode_labstate({
            "steps": self.steps, "day": self.day, "seconds": 0, "pad": 0,
            "rng_state": self.rng.state if self.rng is not None else 0,
            "cell_changes": cc,
        })
        try:
            (dd / "LABSTATE.BIN").write_bytes(blob)
        except OSError:
            pass
        # GAME1 savegame block (LR-55)
        try:
            block = self.build_savegame_payload()
            path = dd / "GAME1"
            data = bytearray(path.read_bytes())
            off = self.sc.tables["savegameOffsets"][0]
            data[off:off + len(block)] = block
            path.write_bytes(bytes(data))
        except Exception:  # noqa: BLE001
            pass

    def build_savegame_payload(self):
        order = [m.get("slot", i + 1) for i, m in enumerate(self.party)]
        order = order + [0] * (7 - len(order))
        chars = [self.character_dict(m) for m in self.party]
        sg = {
            "groups": [{
                "order": order[:7], "x": self.x, "y": self.y, "map": self.location,
                "prevX": self.prev_x, "prevY": self.prev_y, "prevMap": self.prev_location,
            }],
            "viewportX": self.x, "viewportY": self.y,
            "currentMembers": len(self.party), "currentParty": 0,
            "currentMap": self.location, "totalMembers": len(self.party),
            "extraGroups": 0, "minute": self.minute, "hour": self.hour,
            "combatScrollSpeed": 0, "serial": self.serial,
            "characters": chars,
        }
        return containers.encode_savegame(sg, 0)

    def character_dict(self, m):
        attrs = m.get("attrs", {})
        return {
            "name": m.get("name", ""),
            "strength": attrs.get("STR", 0), "intelligence": attrs.get("IQ", 0),
            "luck": attrs.get("LCK", 0), "speed": attrs.get("SPD", 0),
            "agility": attrs.get("AGL", 0), "charisma": attrs.get("CHA", 0),
            "money": m.get("money", 0), "gender": m.get("gender", 0),
            "nationality": m.get("nationality", 0), "armorClass": m.get("ac", 0),
            "maxCon": m.get("max_hp", 0), "curCon": m.get("hp", 0),
            "weaponSlot": m.get("weapon_slot", 0), "skillPoints": m.get("skill_points", 0),
            "experience": m.get("xp", 0), "level": m.get("level", 1),
            "armorSlot": m.get("armour_slot", 0), "afflictions": m.get("cond", 0),
            "npc": m.get("npc", 0), "rank": m.get("rank", ""),
            "gameWon": m.get("game_won", 0),
            "skills": [list(x) for x in m.get("skills", [])],
            "items": [list(x) for x in m.get("items", [])],
        }

    def load_game(self):
        dd = Path(self.data_dir)
        ls_path = dd / "LABSTATE.BIN"
        if ls_path.is_file():
            st = labstate.decode_labstate(ls_path.read_bytes())
            self.steps = st.get("steps", self.steps)
            self.day = st.get("day", self.day)
            if self.rng is not None:
                self.rng.state = st.get("rng_state", self.rng.state)
            self.cell_changes = [tuple(c) for c in st.get("cell_changes", [])]
        try:
            data = (dd / "GAME1").read_bytes()
            off = self.sc.tables["savegameOffsets"][0]
            sg = containers.decode_savegame(data, off)
            g = sg["groups"][0]
            self.x = g["x"]
            self.y = g["y"]
            self.location = g["map"]
            self.prev_x = g["prevX"]
            self.prev_y = g["prevY"]
            self.prev_location = g["prevMap"]
            self.minute = sg["minute"]
            self.hour = sg["hour"]
            self.serial = sg["serial"]
            self.restore_party(sg)
        except Exception:  # noqa: BLE001
            pass
        self.emit("load", serial=self.serial)

    def restore_party(self, sg):
        order = sg["groups"][0]["order"]
        chars = sg["characters"]
        party = []
        for slot in order:
            if not slot:
                continue
            ch = chars[slot - 1]
            if not ch.get("name"):
                continue
            party.append(self.member_from_character(ch, slot))
        if party:
            self.party = party

    # -- combat ------------------------------------------------------------

    def start_encounter(self, rec):
        self.mode = "combat"
        groups = self.build_groups(rec)
        self.combat = {"groups": groups, "round": 0, "rec": rec, "surprised": False,
                       "band": 3, "kills": 0, "fired": set(),
                       "pending_monsters": [[0] * len(g["hp"]) for g in groups],
                       "pending_members": {}, "over": False, "last_death_round": None}
        self.emit("encounter_start", groups=[self.group_event(g) for g in groups])
        msg = (rec or {}).get("message", 0)
        if msg:
            self.show_message(msg)
        if (rec or {}).get("friendly"):
            self.emit("combat_end", result="friendly")
            self.mode = "map"
            self.apply_tail(rec, self.x, self.y)
            return
        if not groups:
            self.emit("combat_end", result="victory", rounds=0)
            self.mode = "map"
            self.apply_tail(rec, self.x, self.y)
            return
        d_max = max(g["mob"].get("combatRating", 0) for g in groups)
        skill = 18
        member = self.pick_member(skill)
        level = self.skill_level(self.party[member - 1], skill)
        attr = self.attr_value(self.party[member - 1], skill)
        res = rules.skill_check(self.rng, level, attr, d_max)
        self.emit("check", member=member, skill=skill, level=level, **res)
        if not res["success"]:
            self.combat["surprised"] = True
            self.emit("surprised")
            self.surprise_round()

    def key_a(self):
        if self.mode != "combat":
            return False
        self.combat_round()
        return True

    # -- repeat ------------------------------------------------------------

    def run_repeat(self, item):
        spec = item["repeat_until"]
        if isinstance(spec, dict):
            script = spec.get("script")
            if script is None:
                script = spec.get("keys", [])
            until = spec.get("until")
            if until is None:
                until = spec.get("condition")
            limit = spec.get("limit", spec.get("max", 200))
        else:
            script = item.get("keys", [])
            until = spec
            limit = item.get("max", item.get("limit", 200))
        for _ in range(limit):
            self.run_script(script)
            if until is None or self._until_met(until):
                return
        raise RepeatLimitError("repeat_until %r not met after %d rounds" % (until, limit))

    def _until_met(self, until):
        if isinstance(until, str):
            if until.startswith("mode:"):
                return self.mode == until[len("mode:"):]
            if until.startswith("cell:"):
                parts = until[len("cell:"):].split(",")
                if len(parts) == 3:
                    loc, x, y = (int(p) for p in parts)
                    return any(c[0] == loc and c[1] == x and c[2] == y
                               for c in self.cell_changes)
                return False
            return any(e.get("type") == until for e in self.events)
        if isinstance(until, dict):
            for e in self.events:
                if all(e.get(k) == v for k, v in until.items()):
                    return True
        return False


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def first_frame_state(data_dir, seed=None):
    """The state the curses front end draws for the first frame (SPEC-06 7).

    Starts a new game with the scenario's premade party and returns the state
    the screen model needs: the status line fields, the map's current image
    array (image = tile + 10, SPEC-06 2.3), the border image and the party.
    The headless driver has no paragraph pop-up (SPEC-06 2.5), so the frame is
    the map view straight away.
    """
    eng = Engine(data_dir, seed=seed)
    eng.new_game(seed if seed is not None else 1)
    m = eng.sc.map(eng.location)
    return {
        "location": eng.location,
        "location_name": eng.sc.location_name(eng.location),
        "x": eng.x,
        "y": eng.y,
        "steps": eng.steps,
        "day": eng.day,
        "hour": eng.hour,
        "minute": eng.minute,
        "mode": eng.mode,
        "tiles": m["cells"]["image"],
        "border_image": m["info"]["borderImage"],
        "party": eng.party,
    }


def run(data_dir, options=None, seed=None, *args, **kwargs):
    if isinstance(options, str):
        try:
            options = json.loads(options)
        except ValueError:
            options = {"script": [options]}
    if isinstance(options, (list, tuple)):
        options = {"script": list(options)}
    options = dict(options or {})
    if seed is None:
        seed = kwargs.get("seed", options.get("seed"))
    eng = Engine(data_dir, seed=seed, options=options)
    eng.new_game(seed)
    eng.run_script(options.get("script", []))
    return eng.events
