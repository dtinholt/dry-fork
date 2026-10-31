"""Game rules (SPEC-04).

This module holds the lab rules v1 of SPEC-04: the random generator, the
character formulas, skill checks, movement and time, encounters, combat and
the shop prices.  ``read_skill_table`` reads the 36-entry skill metadata table
of LABSKILL.BIN (SPEC-04 LR-6).
"""

from __future__ import annotations

from .errors import FormatError

SKILL_ENTRIES = 36
MASK32 = 0xFFFFFFFF
DEFAULT_SEED = 0x6D2B79F5


def read_skill_table(path: str) -> list:
    """36 x ``[minimum_iq, cost, attribute_offset]`` (SPEC-04 LR-6)."""
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 2 * SKILL_ENTRIES:
        raise FormatError("LABSKILL: %d bytes, expected at least %d"
                          % (len(data), 2 * SKILL_ENTRIES))
    out = []
    for i in range(SKILL_ENTRIES):
        b0, b1 = data[2 * i], data[2 * i + 1]
        out.append([b0 >> 3, b0 & 7, b1])
    return out


# ---------------------------------------------------------------------------
# LR-1, LR-2: the generator
# ---------------------------------------------------------------------------

class Rng:
    """xorshift32 generator of SPEC-04 LR-1 and LR-2."""

    def __init__(self, seed: int = 0) -> None:
        seed = int(seed) & MASK32
        self.state = seed if seed else DEFAULT_SEED

    def next(self) -> int:
        x = self.state
        x ^= (x << 13) & MASK32
        x ^= x >> 17
        x ^= (x << 5) & MASK32
        x &= MASK32
        self.state = x
        return x

    def roll(self, n: int) -> int:
        return 1 + self.next() % n

    def rnd(self, n: int) -> int:
        if n == 0:
            return 0
        if n == 1:
            return 1
        return self.roll(n)

    def dice(self, n: int, sides: int) -> int:
        total = 0
        for _ in range(n):
            total += self.roll(sides)
        return total

    def d100(self) -> int:
        return self.roll(100)


# ---------------------------------------------------------------------------
# LR-5 to LR-10: characters
# ---------------------------------------------------------------------------

def roll_attributes(rng: Rng) -> list:
    """LR-7: six draws, in the order STR, IQ, LCK, SPD, AGL, CHA."""
    return [8 + rng.roll(10) for _ in range(6)]


def max_hp(strength: int, level: int) -> int:
    """LR-8, LR-46."""
    return 10 + strength + (level - 1) * (2 + strength // 5)


def armour_class(agility: int, armour_bonus: int, evasion_level: int) -> int:
    """LR-8."""
    return agility // 5 + armour_bonus + evasion_level


def starting_money(luck: int) -> int:
    """LR-9."""
    return 50 + 5 * luck


# ---------------------------------------------------------------------------
# LR-13, LR-14: checks
# ---------------------------------------------------------------------------

def check_need(level: int, attribute: int, difficulty: int, tool: bool = False) -> int:
    """LR-13, unclamped."""
    return 20 + 15 * level + 2 * attribute - difficulty + (20 if tool else 0)


def skill_check(rng: Rng, level: int, attribute: int, difficulty: int, tool: bool = False) -> dict:
    """LR-13: one d100 unless the need is 100 or more, or 0 or less."""
    need = check_need(level, attribute, difficulty, tool)
    if need >= 100:
        return {"need": need, "roll": None, "success": True}
    if need <= 0:
        return {"need": need, "roll": None, "success": False}
    r = rng.d100()
    return {"need": need, "roll": r, "success": r <= need}


def pick_checker(candidates: list):
    """LR-14: highest level, then higher attribute, then lower slot."""
    best = None
    best_key = None
    for c in candidates:
        if c.get("cond", 0) != 0:
            continue
        key = (c.get("level", 0), c.get("attribute", 0), -c.get("slot", 0))
        if best_key is None or key > best_key:
            best_key = key
            best = c.get("slot")
    return best


# ---------------------------------------------------------------------------
# LR-15 to LR-17: movement and time
# ---------------------------------------------------------------------------

def advance_clock(clock: dict, minutes: int, seconds: int):
    """LR-16, LR-17: returns (clock, hours whose minute 0 was reached)."""
    day = clock.get("day", 1)
    minute = clock.get("minute", 0)
    second = clock.get("second", 0)
    total_s = second + seconds
    second = total_s % 60
    add_min = minutes + total_s // 60
    hours = []
    for _ in range(add_min):
        minute += 1
        if minute == 1440:
            minute = 0
        if minute % 60 == 0:
            h = minute // 60
            hours.append(h)
            if h == 0:
                day += 1
    return {"day": day, "minute": minute, "second": second}, hours


# ---------------------------------------------------------------------------
# LR-45, LR-46: experience
# ---------------------------------------------------------------------------

def xp_threshold(level: int) -> int:
    """LR-45."""
    return 50 * level * (level + 1)


def level_after(level: int, xp: int) -> int:
    """LR-45."""
    while xp >= xp_threshold(level):
        level += 1
    return level


# ---------------------------------------------------------------------------
# LR-20, LR-53: money and shops
# ---------------------------------------------------------------------------

def buy_price(price: int, haggling: int) -> int:
    """LR-53."""
    h = min(5, haggling)
    return price * (100 - 5 * h) // 100


def sell_price(price: int, haggling: int) -> int:
    """LR-53."""
    h = min(5, haggling)
    return price * (50 + 5 * h) // 100


def pay(moneys: list, first_slot: int, price: int):
    """LR-20: new money list, or None when the party cannot pay."""
    if sum(moneys) < price:
        return None
    out = list(moneys)
    order = [first_slot - 1] + [i for i in range(len(moneys)) if i != first_slot - 1]
    left = price
    for i in order:
        take = min(out[i], left)
        out[i] -= take
        left -= take
        if left == 0:
            break
    return out


# ---------------------------------------------------------------------------
# LR-26 to LR-28: monsters and encounters
# ---------------------------------------------------------------------------

def monster_values(mob: dict) -> dict:
    """LR-27."""
    cr = mob.get("combatRating", 0)
    ac = mob.get("armorClass", 0)
    st = mob.get("sturdiness", 0)
    return {"to_hit_base": 20 + 5 * cr, "speed": cr, "ac": ac,
            "ranged": mob.get("weaponType", 0) >= 3, "xp": st * (ac + 1)}


def monster_hp(rng: Rng, sturdiness: int) -> int:
    """SPEC-03 6.6, LR-26: the high byte is drawn first."""
    hi = rng.rnd(sturdiness >> 8)
    lo = rng.rnd(sturdiness & 0xFF)
    return sturdiness // 4 + ((hi << 8) | lo)


def monster_damage(rng: Rng, mob: dict) -> int:
    """LR-27."""
    return rng.dice(mob.get("randomDamage", 0), 6) + mob.get("fixedDamage", 0)


def build_groups(rng: Rng, mobs: list, record: dict) -> list:
    """LR-26, LR-28."""
    counts = []
    for entry in record.get("groups", []):
        mob_index, rnd_flag, size = entry[0], entry[1], entry[2]
        if mob_index == 0:
            continue
        mob = mobs[mob_index - 1]
        s = size if size else mob.get("maxGroup", 0)
        counts.append((mob_index, rng.rnd(s) if rnd_flag else s))
    out = []
    for mob_index, count in counts:
        if count <= 0:
            continue
        mob = mobs[mob_index - 1]
        hp = [monster_hp(rng, mob.get("sturdiness", 0)) for _ in range(count)]
        band = 3 if mob.get("weaponType", 0) >= 3 else 2
        out.append({"monster": mob_index, "count": count, "band": band, "hp": hp})
    return out


# ---------------------------------------------------------------------------
# LR-34, LR-35, LR-39, LR-40, LR-43: combat formulas
# ---------------------------------------------------------------------------

def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def ranged_need(level: int, agility: int, target_ac: int, band: int) -> int:
    """LR-34."""
    return _clamp(35 + 12 * level + agility - 6 * target_ac - 5 * (band - 1), 5, 95)


def melee_need(level: int, agility: int, target_ac: int) -> int:
    """LR-35."""
    return _clamp(35 + 12 * level + agility - 6 * target_ac, 5, 95)


def monster_need(combat_rating: int, member_ac: int, band: int) -> int:
    """LR-34, LR-35."""
    return _clamp(20 + 5 * combat_rating - 6 * member_ac - 5 * (band - 1), 5, 95)


def flee_need(best_member_speed: int, best_monster_speed: int, command_level: int) -> int:
    """LR-43."""
    return _clamp(40 + 5 * (best_member_speed - best_monster_speed) + 5 * command_level, 5, 95)


def jam_chance(gunsmithing_level: int) -> int:
    """LR-34."""
    return max(1, 4 - gunsmithing_level)


def unarmed_attacks(grappling_level: int) -> int:
    """LR-35."""
    return 1 + grappling_level // 2


def melee_damage_bonus(strength: int) -> int:
    """LR-35."""
    return max(0, (strength - 10) // 2)


def damage_member(hp: int, damage: int) -> dict:
    """LR-40."""
    prev = hp
    hp -= damage
    if hp > 0:
        return {"hp": hp, "cond": 0, "last_hp": None}
    over = damage - prev
    return {"hp": 0, "cond": 2 if over >= 5 else 1, "last_hp": prev}


def speed_order(actors: list) -> list:
    """LR-35: speed, members before monsters, slot, group, monster."""
    def key(a):
        party = a.get("side") == "party"
        return (-a.get("speed", 0), 0 if party else 1,
                a.get("slot", 0) if party else 0,
                0 if party else a.get("group", 0),
                0 if party else a.get("index", 0))
    return sorted(actors, key=key)


__all__ = ["Rng", "read_skill_table", "roll_attributes", "max_hp", "armour_class",
           "starting_money", "check_need", "skill_check", "pick_checker", "advance_clock",
           "xp_threshold", "level_after", "buy_price", "sell_price", "pay", "monster_values",
           "monster_hp", "monster_damage", "build_groups", "ranged_need", "melee_need",
           "monster_need", "flee_need", "jam_chance", "unarmed_attacks", "melee_damage_bonus",
           "damage_member", "speed_order"]
