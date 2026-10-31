# SPEC-04: game rules

Status: draft for freeze with PREREG-W1, version 1, 21 Oct 2026.
Scope: everything the engine does at play time that SPEC-01 to SPEC-03 leave
open: the random number generator, characters, skills and checks, movement and
time, the lab cell hooks, the paragraph book, encounters, combat, experience,
items, shops, and save and load. The front end and the headless driver are
SPEC-06. The Dry Fork scenario data is SPEC-05.

## 1. Status of these rules

Public, general knowledge of the 1988 game informed the shape of the system:
the attribute names, the existence of skills with an IQ requirement and a
linked attribute, turn-based combat in which ranged attacks resolve together
and melee goes in speed order, experience and levels, ammunition and jamming.
No formula, table, number, name or text below comes from the game. Every rule
in this file is labelled "lab rule v1 (non-parity)", is numbered LR-n, and was
chosen to be deterministic and testable. The parity milestone replaces
these rules with measured ones and keeps the decoders of SPEC-01 to SPEC-03.

These rules sit on top of SPEC-03 section 9. Where SPEC-03 fixes a behaviour
(passability by class, trigger order, record tails, transitions, the paragraph
trigger text, group sizes from encounter records, the documented monster hit
point and experience formulas), this file uses it and does not restate it as a
lab rule. Section 15 lists two places where this file needs a small amendment
to SPEC-02 and SPEC-03; both are flagged there.

Conventions: integers only; `div` is floor division of non-negative integers;
`clamp(v, lo, hi)` bounds `v`; slots are numbered from 1 in events and in
savegames; "member" is any party member, PC or NPC; "conscious" means
condition 0 (section 3.5).

## 2. Random numbers

**LR-1, lab rule v1 (non-parity). Generator.** One xorshift32 generator holds a
32-bit state `x`. `next()` computes, in this order and modulo 2^32:
`x ^= x << 13; x ^= x >> 17; x ^= x << 5;` and returns the new `x`. Seeding
sets `x = seed`; a seed of 0 is replaced by 0x6D2B79F5. The state is never 0.

**LR-2, lab rule v1 (non-parity). Derived draws.**

```text
roll(n)  = 1 + next() mod n                         n >= 1, one call
rnd(n)   = 0 if n = 0; 1 if n = 1 (no call); roll(n) if n >= 2
dice(N, S) = roll(S) called N times, summed in order (N = 0 gives 0, no call)
d100     = roll(100)
```

`rnd` is the SPEC-03 section 6.6 function. Modulo bias is accepted.

**LR-3, lab rule v1 (non-parity). One stream, documented order.** The engine
owns exactly one generator. Nothing else may call it: the front end, the
renderer and the headless driver draw no random numbers. Every rule below
names its draws in the order they happen; an implementation that draws in any
other order fails the replay tests.

**LR-4, lab rule v1 (non-parity). Seed and persistence.** A new game seeds the
generator from the command line or the script (`seed`), else from the
scenario start record. The state is saved in LABSTATE.BIN (section 13.3) and
restored on load, so a loaded game continues the same stream.

Test vectors for seeds 20261021, 1 and 0 are in `SPEC/scenario/rng-vectors.json`.
For seed 20261021 the first three `next()` values are 553487182, 2736026372,
2213040766, and the first five `roll(100)` values are 83, 73, 67, 54, 40.

## 3. Characters

### 3.1 Attributes

**LR-5, lab rule v1 (non-parity). Six attributes.** The rules use six
attributes: STR, IQ, LCK, SPD, AGL and CHA, stored at character record offsets
0x0E, 0x0F, 0x10, 0x11, 0x12 and 0x14 (SPEC-02 section 4.4). The dexterity
byte at 0x13 is written as 0 in lab data and is never read by these rules.

### 3.2 The skill table

**LR-6, lab rule v1 (non-parity). LABSKILL.BIN.** A 72-byte lab file with 36
entries of 2 bytes in the WL.EXE skill-metadata format of SPEC-02 section 3.3:
byte 0 = `(minimum IQ << 3) | cost`, byte 1 = record offset of the linked
attribute. Entry 0 is a dummy (both bytes 0). Entries 1 to 35 are the skills
with ids 1 to 35. Skill names are LABSTR table 2, strings 1 to 35. Skill slot id
0 means "unused", so a 36-entry table holds 35 skills.

The Dry Fork skill set is in the table below. "Barrier" means the engine
effect is exactly this: a lock hook (section 6.2) may name the skill, and the
check uses it. Every other effect is defined in the rule it names.

| Id | Name | Min IQ | Attribute | Cost | Engine effect |
| --- | --- | --- | --- | --- | --- |
| 1 | Bludgeon | 3 | STR | 1 | weapon skill for items with skill byte 1 (LR-34) |
| 2 | Edged arms | 3 | AGL | 1 | weapon skill for items with skill byte 2 |
| 3 | Grappling | 3 | STR | 1 | unarmed weapon skill; unarmed attacks per action = 1 + level div 2 (LR-35) |
| 4 | Handgun | 5 | AGL | 1 | weapon skill for items with skill byte 4 |
| 5 | Longarm | 6 | AGL | 1 | weapon skill for items with skill byte 5 |
| 6 | Spreadgun | 6 | AGL | 1 | weapon skill for items with skill byte 6 |
| 7 | Autofire | 9 | AGL | 2 | weapon skill for items with skill byte 7 |
| 8 | Hurling | 4 | AGL | 1 | weapon skill for items with skill byte 8 |
| 9 | Tube launcher | 10 | AGL | 2 | weapon skill for items with skill byte 9 |
| 10 | Archery | 6 | AGL | 1 | weapon skill for items with skill byte 10 |
| 11 | Evasion | 8 | AGL | 2 | adds its level to AC (LR-8) |
| 12 | First aid | 10 | IQ | 1 | medical items heal 2 x level more (LR-47) |
| 13 | Bonesetting | 14 | IQ | 2 | revives an unconscious member (LR-48) |
| 14 | Tumblers | 9 | AGL | 1 | barrier (locks) |
| 15 | Strongbox | 12 | IQ | 2 | barrier (safes) |
| 16 | Scaling | 3 | STR | 1 | barrier (climbing) |
| 17 | Fording | 3 | STR | 1 | barrier (water) |
| 18 | Lookout | 8 | IQ | 1 | surprise check (LR-30) |
| 19 | Trailcraft | 8 | IQ | 1 | barrier (tracks); random encounters are absent in v1 (SPEC-03 L-MI3) |
| 20 | Haggling | 7 | CHA | 1 | shop prices (LR-53) |
| 21 | Smooth talk | 9 | CHA | 1 | lowers recruit CHA requirement (LR-22) |
| 22 | Gunsmithing | 10 | IQ | 1 | jam chance and unjam check (LR-39) |
| 23 | Circuitry | 12 | IQ | 2 | barrier (wired locks) |
| 24 | Blasting | 11 | IQ | 2 | barrier (charges) |
| 25 | Engines | 11 | IQ | 2 | barrier (machinery) |
| 26 | Salvage | 7 | LCK | 1 | victory money (LR-44) |
| 27 | Quiet foot | 8 | AGL | 1 | barrier (sneaking); random encounters are absent in v1 |
| 28 | Foraging | 6 | IQ | 1 | rest heals extra (LR-17) |
| 29 | Terminals | 13 | IQ | 2 | barrier (consoles) |
| 30 | Signals | 12 | IQ | 2 | barrier (radios) |
| 31 | Mapcraft | 8 | IQ | 1 | barrier (route finding) |
| 32 | Beast lore | 7 | IQ | 1 | barrier (animals) |
| 33 | Dice and cards | 6 | LCK | 1 | barrier (games of chance) |
| 34 | Old script | 11 | IQ | 1 | barrier (inscriptions) |
| 35 | Command | 12 | CHA | 2 | flee chance (LR-43) |

The byte values of LABSKILL.BIN are listed in SPEC-05 section 8.

### 3.3 Character creation

**LR-7, lab rule v1 (non-parity). Rolling.** A created character draws, in the
order STR, IQ, LCK, SPD, AGL, CHA, one `8 + roll(10)` each (range 9 to 18).
A reroll repeats the six draws in the same order and replaces all six values.
Name (1 to 13 printable characters), gender (0 or 1) and nationality (0 to 4)
are chosen and draw nothing.

**LR-8, lab rule v1 (non-parity). Derived values.**

```text
maxHP  = 10 + STR + (level - 1) x (2 + STR div 5)        (level 1: 10 + STR)
curHP  = maxHP at creation
AC     = AGL div 5 + armour bonus of the equipped armour + level of Evasion (11)
```

The armour bonus is the damage byte of the equipped armour item (section 11).
AC is recomputed after every equip, unequip, sale of an equipped item,
promotion and load, and written to record offset 0x1A. maxHP and curHP are the
record's maximum and current constitution (0x1B, 0x1D).

**LR-9, lab rule v1 (non-parity). Starting money and kit.** Money = 50 + 5 x
LCK. A created character starts with no items, weapon slot 0 and armour slot 0.

**LR-10, lab rule v1 (non-parity). Starting skills.** A created character
receives skill points equal to IQ. Buying one level of skill `s` costs
`cost(s)` points and is allowed when IQ is at least the skill's minimum IQ, the
current level is below 3, and enough points remain. A new skill takes the
first free skill slot. Unspent points are stored at record offset 0x20.
Level 1, experience 0, rank string from LABSTR table 3 string 0.

A new game in Dry Fork uses the premade party of SPEC-05 instead; creation is
offered by the front end (SPEC-06 section 4.1) and tested on its own.

### 3.4 Party

**LR-11, lab rule v1 (non-parity). Party shape.** One party group (group 0 of
the savegame), 1 to 7 members in slots 1 to 7. Slot 1 is the leader. The
"active member" is the conscious member with the lowest slot. Recruited NPCs
take the next free slot. Dismissing a member (allowed for an NPC, or for any
dead member, never for the last member) removes it and moves every later
member up one slot.

### 3.5 Condition

**LR-12, lab rule v1 (non-parity). Condition.** Condition 0 = conscious,
1 = unconscious, 2 = dead. In the record, the afflictions byte 0x28 holds bit 0
for unconscious and bit 1 for dead; curHP is 0 in both cases; 0x26 holds the HP
the member had before the blow that dropped it, and is set to 0 when the member
is revived. Unconscious and dead members take no actions, are never targeted,
and do not heal naturally.

## 4. Skill checks

**LR-13, lab rule v1 (non-parity). The check formula.** A check of member `m`
with skill `s` against difficulty `D`:

```text
L    = m's level in s (0 if m lacks s)
A    = m's value of the attribute linked to s
need = 20 + 15 x L + 2 x A - D + bonus           bonus = 20 with a tool (LR-21), else 0
need >= 100: success, no draw
need <= 0:   failure, no draw
otherwise:   r = d100; success when r <= need
```

The engine emits one `check` event with `member, skill, level, need, roll`
(`roll` is null when no draw was made) and `success`.

**LR-14, lab rule v1 (non-parity). Who checks.** A party check picks the
conscious member with the highest level in the skill; ties go to the higher
linked attribute, then to the lower slot. A member check (unjam, Bonesetting)
uses the acting member.

Worked example: Maro Quill (Tumblers 2, AGL 15) at the Ninemile storehouse
(difficulty 30): need = 20 + 30 + 30 - 30 = 50.

## 5. Movement and time

The order of a move is SPEC-03 section 9.6. This section adds what happens
around it.

**LR-15, lab rule v1 (non-parity). Steps.** A move that changes the party's
cell increases the step counter by 1, including the step onto a transition
cell; arriving on the target of a transition is not a step. A bump (class 11,
or class 4 impassable), a blocked move, a look or an interaction is not a step
and takes no time.

**LR-16, lab rule v1 (non-parity). Clock.** After each step the engine adds
the time per step of the map the step started on (SPEC-03 L-MI2: high byte
minutes, low byte seconds) to the clock. Seconds carry into minutes. The clock
is a day number from 1 and a time of day in minutes from 0 to 1439. A new game
starts on day 1 at the scenario's start hour, minute 0, second 0.

**LR-17, lab rule v1 (non-parity). Natural healing, days and rest.** Each time
an advance of the clock crosses a full hour, every conscious member below maxHP
gains 1 HP (one `natural_heal` event listing the slots that gained, omitted if
none), and if the new hour is 0 the day number increases by 1 (`day` event).
Several hours crossed in one advance are processed one by one, in order. The
rest command advances the clock by 60 minutes with these effects, then every
conscious member gains HP equal to the best Foraging (28) level among conscious
members, capped at maxHP. Rest is allowed in map mode only and is not a step.
The map-info heal rate is not used (SPEC-03 L-MI4).

## 6. Lab cell hooks

SPEC-03 lab data has no records for skill checks, recruits, healers or winning
(it reserves class 2 and the others). The lab adds these as hooks keyed by
cell, in LABHOOKS.JSON, compiled from `SPEC/scenario/hooks.json`.

**LR-18, lab rule v1 (non-parity). Where hooks run.** A hook belongs to one
cell `(location, x, y)` whose current class is 11, or 4 with an impassable
record. When the party bumps that cell (or interacts with it, SPEC-06 section
3), the engine first does exactly what SPEC-03 section 9.6 says for the class
(show the record message, apply a BLOCKED tail), then runs the hook. A hook on
a cell whose current class is anything else does nothing. At most one hook per
cell.

**LR-19, lab rule v1 (non-parity). Cell changes.** The engine keeps a table of
cell changes: for a cell `(location, x, y)`, its current class, action byte and
image. Applying a record tail (SPEC-03 L-TL1), setting a DOOR image, a lock's
remote change and a recruit's change all write to this table and emit one
`cell_change` event with the full new triple. The base map files are never
modified (SPEC-03 L-TL2); the table is saved in LABSTATE.BIN.

### 6.1 Payments

**LR-20, lab rule v1 (non-parity). Paying.** A payment of `p` coins with a
first payer `f` fails, changing nothing, when the party's total money is below
`p`. Otherwise it takes as much as it can from `f`, then from the other members
in slot order, until `p` is paid, emitting one `money` event per member whose
money changed.

### 6.2 Lock

**LR-21, lab rule v1 (non-parity). Lock hook.** Fields: `skill`,
`difficulty`, `key_item`, `tool_item`, `success_message`, `fail_message`,
`remote`.

1. If `key_item` is non-zero and a member who is not dead carries it, the lock
   opens with no draw (`key_used` event).
2. Else, if `skill` is non-zero, the party check of LR-14 runs with LR-13; the
   bonus is 20 when the checking member carries `tool_item`.
3. Else the lock stays shut.

The checking member is the one LR-14 picks, whether or not it carries the
tool. `key_used` names the lowest-slot carrier. On success, in this order: emit
`unlock`; apply the DOOR record's tail to the cell (one `cell_change`, image
unchanged); if the cell is now class 4 with a passable record, set its image to
that record's tile (a second `cell_change`); if `remote` is set, write `remote.new_class` and `remote.new_action` to
the remote cell on the same map and set its image the same way; award 10
experience to the checking member when a check was made (none for a key); show
`success_message`. On failure: show `fail_message`. Every bump retries; a retry
draws again.

### 6.3 Recruit

**LR-22, lab rule v1 (non-parity). Recruit hook.** Fields: `npc` (0-based index
into the map's NPC section), `min_leader_cha`, `refuse_message`,
`cleared_image`.

1. Party full (7 members): show UI string 1, stop.
2. `need = min_leader_cha - 2 x (leader's Smooth talk level)`. If the leader's
   CHA is below `need`: show `refuse_message`, stop.
3. Prompt yes or no. On yes: copy the NPC record into the next slot with
   condition 0 and the NPC flag set; set the cell to class 0, action 0, image
   `cleared_image`; emit `recruit`. On no: `cancel`.

The record's maxHP and curHP are used as stored; the scenario writes both as
LR-8 gives them.

### 6.4 Healer

**LR-23, lab rule v1 (non-parity). Healer hook.** Field: `price`. Prompt yes
or no. On yes, pay `price` with slot 1 as first payer (LR-20); on failure show
UI string 2; on success every member who is not dead goes to maxHP and
condition 0 (`heal_all`). Dead members stay dead.

### 6.5 Win

**LR-24, lab rule v1 (non-parity). Win hook.** Fields: `item`,
`win_paragraph`, `not_yet_paragraph`. If a member who is not dead carries
`item`: show paragraph `win_paragraph`, set the game-won byte (0x4B) of every
member to 1, enter mode `won` (all later input is ignored), emit `win`. Else
show paragraph `not_yet_paragraph`.

## 7. Paragraph book

**LR-25, lab rule v1 (non-parity). Paragraphs.** The paragraph book is
`PARAGRAPHS.JSON`, a list of numbered entries. Showing a map string whose whole
text matches `Read paragraph N.` (decimal N, no other characters) emits one
`paragraph` event with `n = N` in place of a `message` event, and the front end
shows entry N. A new game shows the scenario's start paragraph after
`new_game`. Showing a paragraph draws nothing, takes no time and in headless
mode waits for no key.

## 8. Encounters

An encounter starts when the party steps onto a class 3 cell (SPEC-03 section
9.6). Random encounters do not exist in v1 (SPEC-03 L-MI3).

**LR-26, lab rule v1 (non-parity). Building the groups.** For the three group
slots of the record in order, skipping monster index 0: `s = size`, or the
monster's maximum group nibble when `size` is 0; the count is `rnd(s)` when the
random flag is set, else `s` (SPEC-03 L-MB2). After all counts are known, for
each group with a count above 0 in slot order and each monster in it in order,
hit points are `sturdiness div 4 + ((rnd(sturdiness >> 8) << 8) | rnd(sturdiness & 0xFF))`
(SPEC-03 section 6.6), drawing the high-byte `rnd` first. Groups with count 0
are dropped. If no monster remains, the encounter is a victory with 0
experience.

**LR-27, lab rule v1 (non-parity). Monster combat values.** From the monster
record (SPEC-03 section 6.6):

```text
to-hit base  = 20 + 5 x combat rating
speed        = combat rating
AC           = armor class nibble
damage       = dice(random damage, 6) + fixed damage nibble
ranged       = weapon type nibble >= 3      (0 to 2 melee)
experience   = sturdiness x (armor class + 1)   (documented in SPEC-03 6.6)
```

Type and portrait are display data. Visible and hit distance, proper name and
immobile are ignored (SPEC-03 L-MB3).

**LR-28, lab rule v1 (non-parity). Range bands.** Each group stands in a band
from 1 (adjacent) to 5. A ranged group starts in band 3, a melee group in
band 2. Melee attacks reach only band 1. A ranged attack at band `b` takes
`-5 x (b - 1)` to its need.

**LR-29, lab rule v1 (non-parity). Start sequence.** Build the groups (LR-26),
emit `encounter_start` with each group's monster name, count, band and hit
points, show the record's message. If the record's friendly bit is set, emit
`combat_end` with result `friendly`, apply the tail and stop.

**LR-30, lab rule v1 (non-parity). Surprise.** Then the party check of LR-14
runs with Lookout (18) against `D` = the highest combat rating among the
groups. On failure the engine emits `surprised` and resolves one surprise round
(round 0) in which only monsters act: no `round_orders` event, then
`round_start` with round 0, phase 1 and phase 2 with no party actors, and the
end of round of LR-36 (melee groups do close in), after which the round number
is still 1. On success,
or after the surprise round, combat waits for round 1 orders.

## 9. Combat

### 9.1 Rounds and orders

**LR-31, lab rule v1 (non-parity). Round structure.** A round is: orders,
`round_start`, phase 1 (ranged), phase 2 (speed order), end of round. After
phase 1 and after every single attack in phase 2, the end check of LR-42 runs;
if it ends the fight, the rest of the round is skipped.

**LR-32, lab rule v1 (non-parity). Orders.** Each conscious member gets one
order, chosen in slot order (SPEC-06 section 4.6 for keys):

| Order | Phase | Effect |
| --- | --- | --- |
| attack, group g | 1 with a ranged or burst weapon, else 2 | LR-34, LR-35 |
| reload | 2 | LR-38 |
| unjam | 2 | LR-39 |
| close in, group g | 2 | the group's band falls by 1, minimum 1 (`advance`) |
| use item or Bonesetting | 2 | LR-47, LR-48 |
| wait | 2 | nothing (`wait`) |
| flee (whole party, first order only) | replaces the round | LR-43 |

Group letters name living groups only, in group order.

**LR-33, lab rule v1 (non-parity). Auto orders.** The auto key gives every
conscious member, in slot order, this order, using the state at order time:

1. No living group: wait.
2. Ranged or burst weapon whose status byte has bit 7 set: unjam.
3. Ranged or burst weapon with load above 0: attack the lowest-numbered
   living group.
4. Ranged or burst weapon with load 0: reload if the member carries a box of
   its ammunition; otherwise continue as unarmed.
5. Melee weapon, or unarmed: attack the lowest-numbered living group in band 1
   if there is one, else close in on the lowest-numbered living group.

The engine emits `round_orders` with each slot's order and group (1-based).

### 9.2 Phase 1: ranged attacks resolve together

**LR-34, lab rule v1 (non-parity). Ranged resolution.** Damage in phase 1 is
pending until the phase ends, so every combatant alive at the start of the
phase fires even if it is hit.

Party, in slot order, each member with a ranged or burst attack order; a burst
weapon fires 3 shots, any other 1; per shot:

1. If the load (status & 0x7F) is 0: `click`, no more shots this round.
2. Jam draw: `r = d100`; jam chance `j = max(1, 4 - Gunsmithing level)`. If
   `r <= j`: the status byte becomes 0x80 (jammed, rounds lost), `jam` event,
   no more shots.
3. Load falls by 1.
4. Target: the first monster of the ordered group whose HP minus its pending
   damage is above 0; if none, the first living monster of the group.
5. `need = clamp(35 + 12 x L + AGL - 6 x targetAC - 5 x (band - 1), 5, 95)`,
   with `L` the member's level in the weapon's skill byte. `r = d100`; hit when
   `r <= need`.
6. On a hit, damage = `dice(N, S)` from the weapon's damage byte (high nibble
   N, low nibble S), added to the target's pending damage.

Monsters, in group order then monster order, each living ranged monster:
target = the `roll(k)`-th of the `k` members conscious at the start of the
phase, counted in slot order; `need = clamp(to-hit base - 6 x memberAC -
5 x (band - 1), 5, 95)`; `r = d100`; on a hit, damage per LR-27 is pending on
that member. Monsters never jam.

For each monster attack the `roll(k)` target draw comes before the `d100`.
Then pending monster damage applies in (group, monster) order, emitting
`monster_dies` for each monster reaching 0 HP, and pending member damage
applies in slot order through LR-40, each member's phase 1 hits summed into one
damage value `d`.

Worked example: Hessa Brand (Handgun 2, AGL 14) at a raider (AC 1) in band 3:
need = 35 + 24 + 14 - 6 - 10 = 57. A raider at Hessa (AC 3) in band 3:
need = 50 - 18 - 10 = 22.

### 9.3 Phase 2: speed order

**LR-35, lab rule v1 (non-parity). Speed order and melee.** Actors are the
members with a phase 2 order and the living melee monsters. They act in order
of speed (member SPD, monster speed per LR-27), highest first; ties put members
before monsters, then lower slot, then lower group and monster number. At its
turn an actor that is no longer conscious (member) or alive (monster) is
skipped.

A member's melee attack: if its group is dead or not in band 1, it switches to
the lowest-numbered living group in band 1; if there is none, `no_target`.
With a melee weapon it makes 1 attack using the weapon's skill byte and damage
byte; unarmed it makes `1 + Grappling level div 2` attacks using Grappling (3)
and damage 1d3; the sequence stops early when the group has no living monster.
Each attack: target = first living monster of the group;
`need = clamp(35 + 12 x L + AGL - 6 x targetAC, 5, 95)`; `r = d100`; on a hit,
damage = dice from the damage byte + `max(0, (STR - 10) div 2)`, applied at
once.

A melee monster in band 1 attacks: target = the `roll(k)`-th of the `k`
members conscious now, in slot order; `need = clamp(to-hit base - 6 x
memberAC, 5, 95)`; `r = d100`; on a hit, damage per LR-27, applied at once
through LR-40. A melee monster in a band above 1 does nothing at its turn.

**LR-36, lab rule v1 (non-parity). End of round.** Each living melee group in
a band above 1 moves 1 band closer (`group_closes`). The round number then
increases by 1 (the surprise round does not count).

### 9.4 Armour, ammunition and jams

**LR-37, lab rule v1 (non-parity). Armour.** Armour works only through AC
(LR-8) in the need formulas. It absorbs no damage.

**LR-38, lab rule v1 (non-parity). Ammunition and reload.** A ranged weapon's
item status byte holds its load in bits 0 to 6 (SPEC-02 section 4.4). An
ammunition item's status byte holds a count of boxes. A reload takes the first
item slot, in slot order, holding the weapon's ammo item id with a status
above 0, lowers that count by 1 (the slot empties at 0), and sets the weapon
load to its capacity byte (`reload` event). With no such box: UI string 32 and
nothing else. A weapon that is acquired, bought or looted is empty unless the
record or loot sets its status.

**LR-39, lab rule v1 (non-parity). Jams.** A jam (LR-34 step 2) sets the
weapon status to 0x80. A jammed weapon cannot fire. Unjam is a member check
with Gunsmithing (22) at difficulty 0; success sets the status to 0 (empty, so
a reload follows) and emits `unjammed`. Jams persist outside combat and through
save and load; the character screen offers the same unjam action outside
combat, taking no time.

### 9.5 Wounds, end, flight and victory

**LR-40, lab rule v1 (non-parity). Damage to members.** `prev = HP; HP -= d`.
If HP falls to 0 or below: `over = d - prev`, HP = 0, record 0x26 = `prev`;
condition becomes dead when `over >= 5` (`death`), else unconscious
(`unconscious`).

**LR-41, lab rule v1 (non-parity). Monster death.** A monster at 0 HP is dead
and counts toward the kill total of the fight.

**LR-42, lab rule v1 (non-parity). End check.** If no monster is alive: victory
(LR-44). Else, if no member is conscious: defeat; emit `combat_end` with result
`defeat` and `game_over`, and enter mode `gameover`.

**LR-43, lab rule v1 (non-parity). Flight.** Flee replaces the party's orders
for the round. `need = clamp(40 + 5 x (highest SPD among conscious members -
highest speed among living monsters) + 5 x (leader's Command level), 5, 95)`;
`r = d100`; emit `flee` with need, roll and success. On success: `combat_end`
with result `fled`; the party returns to the cell it occupied before stepping
onto the encounter cell; the tail is not applied; no experience. On failure:
the round runs with no party orders.

**LR-44, lab rule v1 (non-parity). Victory.** Emit `combat_end` with result
`victory` and `rounds` = the number of the round in which the last monster
died (before the LR-36 increment). Experience: the sum over all monsters of
LR-27 experience, divided (div) equally among members who are not dead, each
share awarded in slot order with LR-45. Money: `5 x (best Salvage level among
conscious members) x (monsters killed)` to the active member, if above 0. Then
the mode returns to `map`, the encounter record's tail is applied, and if the
cell is now class 5 with a record, that loot fires at once (SPEC-03 section 9.6
loot rule, then its tail), with no step.

## 10. Experience and promotion

**LR-45, lab rule v1 (non-parity). Thresholds.** A member at level `L`
advances when experience reaches `50 x L x (L + 1)` (100, 300, 600, 1000, ...).
Several levels can follow from one award; each is processed in turn.

**LR-46, lab rule v1 (non-parity). Promotion.** Each level gained: maxHP rises
by `2 + STR div 5`, curHP rises by the same unless dead, unspent skill points
rise by 2, the rank string becomes LABSTR table 3 string `min(level, 7) - 1`
(`promote` event). Spending: on the character screen, raising a skill one level
costs its cost in points; requires IQ at least the skill's minimum IQ and a
current level below 10; a new skill takes the first free skill slot.

Other experience: 10 for the member whose check opens a lock (LR-21).

## 11. Items

**LR-47, lab rule v1 (non-parity). Item catalogue and use.** Item id N (1 to
94) is described by record N - 1 of shop list 0 (SPEC-02 section 5): price,
type, capacity, skill, damage, ammo. Lab item types (`type byte >> 3`): 1 melee,
2 ranged, 3 ammunition, 4 armour, 5 medical, 6 tool, 7 quest, 8 burst
(ranged, 3 shots). Equip puts a melee, ranged or burst item in the weapon slot
(0x1F, 1-based) or an armour item in the armour slot (0x25); any other type
shows UI string 5. A medical item used on a conscious member heals
`dice(N, S)` from its damage byte plus 2 x the user's First aid level, capped
at maxHP; its status (uses) falls by 1 and the slot empties at 0. Using it on a
member who is not conscious shows UI string 33. A tool works only as a lock
tool (LR-21). A quest item cannot be sold.

**LR-48, lab rule v1 (non-parity). Bonesetting.** A conscious member with
Bonesetting (13) may treat an unconscious member: member check, difficulty 20;
success sets the target to 1 HP and condition 0 (`bonesetting` event with
success). It draws one d100 unless the need is 100 or more, or 0 or less.

**LR-49, lab rule v1 (non-parity). Loot placement.** SPEC-03 section 9.6 gives
each loot item to the first member with a free item slot and its status from
the amount; members are taken in slot order whatever their condition; with no
free slot anywhere the item is lost (`item_lost`). Loot cash goes to the active
member; a cash amount of 0 changes nothing.

## 12. Shops

**LR-50, lab rule v1 (non-parity). Stock.** Shop list `n` (SPEC-02 L-SH3)
sells every item whose stock byte is 1 to 255. Stock is never decremented in
v1. The buy list shows these items in item id order, keyed a, b, c, ...

**LR-51, lab rule v1 (non-parity). Buying.** The buyer is a chosen member.
Ammunition stacks: if the buyer already holds that ammo id with a count below
127, the count rises by 1 and no slot is used. Otherwise the buyer needs a free
slot (UI string 3 if none). The price is paid with the buyer as first payer
(LR-20; UI string 2 on failure). New item status: ammunition 1, medical its
capacity byte, anything else 0.

**LR-52, lab rule v1 (non-parity). Selling.** The seller is a chosen member and
an item slot. A quest item shows UI string 31. Otherwise the slot empties, an
equipped item is unequipped (slot byte 0), AC is recomputed, and the seller
gains the sell price.

**LR-53, lab rule v1 (non-parity). Prices.** With `H = min(5, best Haggling
level among conscious members)`:

```text
buy price  = price x (100 - 5 x H) div 100
sell price = price x (50 + 5 x H) div 100
```

Worked example: Hessa Brand has Haggling 1, so a Hide vest (price 30) costs
30 x 95 div 100 = 28, and a Pipe club (price 15) sells for 15 x 55 div 100 = 8.

## 13. Save and load

**LR-54, lab rule v1 (non-parity). When.** Save and load are allowed in map
mode only. A save writes the GAME1 savegame block (SPEC-02 section 4, rules
L-SG1 to L-SG3) and LABSTATE.BIN next to GAME1. Map blocks and shop lists are
never rewritten (SPEC-03 L-TL2).

### 13.1 Savegame fields

**LR-55, lab rule v1 (non-parity). Savegame mapping.**

| Field (SPEC-02) | Written as |
| --- | --- |
| group 0 party order | slots 1 to n, then 0 |
| group 0 X, Y, location | party cell and location |
| group 0 previous X, Y, location | SPEC-03 L-TR4 previous fields; 0 when none |
| groups 1 to 3 | all 14 bytes 0 |
| 0x078, 0x079 viewport X, Y | party X and Y |
| 0x07D, 0x080 member counts | n |
| 0x07E current party index | 0 |
| 0x07F location byte | party location |
| 0x081 extra group count | 0 |
| 0x083 minute, 0x084 hour | clock |
| 0x085 combat scroll speed | 0 |
| 0x0F5 save serial | previous serial + 1 (new game: 0) |
| character records | slots 1 to n by section 3; slots above n all zero |

Record fields not named by these rules (refusal values, join string,
willingness, special promotion, UNKNOWN bytes) are written as 0.

### 13.2 Round trip

**LR-56, lab rule v1 (non-parity). Round trip.** Loading restores every value
the checkpoint snapshot of SPEC-06 section 6.4 holds, plus the clock seconds,
the previous-location fields, the generator state, jams and condition. A save
followed by a load followed by a save gives a savegame payload that differs
from the first only in the serial (0x0F5, plus 1) and a LABSTATE.BIN identical
to the first.

### 13.3 LABSTATE.BIN

**LR-57, lab rule v1 (non-parity). Lab state file.** Little-endian:

| Offset | Size | Field |
| --- | --- | --- |
| 0x00 | 8 | magic `WLLABSV1` |
| 0x08 | 4 | step counter |
| 0x0C | 2 | day number |
| 0x0E | 1 | clock seconds (0 to 59) |
| 0x0F | 1 | 0 |
| 0x10 | 4 | generator state |
| 0x14 | 2 | count N of cell changes |
| 0x16 | 6 x N | cell changes sorted by (location, y, x): location, x, y, class, action byte, image |
| 0x16 + 6N | 2 | u16 sum of all earlier bytes, mod 65536 |

A load that finds a wrong magic or sum fails with an error and changes
nothing.

## 14. Event order summary

For a step: `input`, `move`, the clock events of LR-17, then the effect of the
class. For a bump: `input`, `bump`, the record message, the tail's
`cell_change`, then the hook's events. For a round: `input`, `round_orders`,
`round_start`, phase 1 `click`/`jam`/`attack` events in resolution order,
`monster_dies` in (group, monster) order, member wound events in slot order,
then phase 2 events in actor order, then `group_closes`. Every random draw
happens inside the event that reports it, in the order the events appear. The
event schema is SPEC-06 section 6.

## 15. Amendments needed elsewhere (flagged for the spec owner)

1. SPEC-02 section 12.1 lists the lab file set. These rules add LABSKILL.BIN
   (LR-6), LABHOOKS.JSON (section 6), PARAGRAPHS.JSON (LR-25, as SPEC-03 L-MS2
   foresees) and the save-time file LABSTATE.BIN (LR-57). SPEC-02 needs a line
   for each; no SPEC-02 layout changes.
2. SPEC-03 L-AC5 names classes that need a record. Lab hooks attach to class 11
   cells with action 0 (no record), which SPEC-03 already allows; no change is
   needed there. SPEC-03 L-MV3 already hands combat, skills and checks to this
   file.

## 16. Index of lab rules

57 lab rules, LR-1 to LR-57, all "lab rule v1 (non-parity)":
generator LR-1 to LR-4; characters LR-5 to LR-12; checks LR-13 and LR-14;
movement and time LR-15 to LR-17; hooks LR-18 to LR-24; paragraphs LR-25;
encounters LR-26 to LR-30; combat LR-31 to LR-44; experience LR-45 and LR-46;
items LR-47 to LR-49; shops LR-50 to LR-53; save and load LR-54 to LR-57.
