# SPEC-06: front end and headless driver

Status: draft for freeze with PREREG-W1, version 1, 21 Oct 2026.
Scope: the terminal (curses) screen model, the key bindings and menus, and the
headless mode in which a script of inputs drives the same engine and the engine
writes a JSON event log. The acceptance tests use the headless mode only,
except for one curses smoke test (section 7). Rules of play are SPEC-04.

## 1. One engine, two drivers

The engine core is a state machine that accepts one input token at a time and
appends events to a log. It owns the random generator (SPEC-04 LR-3), the
clock and all state. The curses front end and the headless driver are thin:
both translate their input into the same tokens, and neither changes state or
draws random numbers on its own. Given the same data, seed and token sequence,
the two drivers produce the same event log.

A token is one of `UP`, `DOWN`, `LEFT`, `RIGHT`, `ESC`, `ENTER`, or a single
printable ASCII character. Letters are case-sensitive.

## 2. Screen model (curses)

### 2.1 Layout

Minimum terminal 80 columns by 25 rows. Rows and columns count from 0.

| Area | Rows | Columns | Content |
| --- | --- | --- | --- |
| Status line | 0 | 0 to 79 | location name, `Day N`, `HH:MM`, `(x,y)`, `Steps N`, mode name, separated by two spaces |
| Map viewport | 1 to 11 | 0 to 38 | 39 x 11 cells, one character per cell |
| Party panel | 1 to 8 | 40 to 79 | header row, then one row per member |
| Help hint | 9 to 11 | 40 to 79 | the keys valid in the current mode |
| Message log | 12 to 22 | 0 to 79 | the last 11 log lines, newest at the bottom |
| Prompt line | 23 | 0 to 79 | the current prompt or menu line |
| Key line | 24 | 0 to 79 | `? help` and the mode's main keys |

### 2.2 Map viewport

The party is drawn as `@` at viewport cell (19, 5), screen row 6, column 19.
Viewport cell (i, j) shows map cell (x - 19 + i, y - 5 + j). A cell outside
the map shows the glyph of the map's border image (SPEC-03 L-MI5). A cell
inside shows the glyph of its current image (after cell changes, SPEC-04
LR-19). A class 3 cell that still holds its encounter record shows `!` over its
image (the text form of SPEC-03 L-IM2). Images 0 to 9 (sprites) show `0` to
`9`.

### 2.3 Glyphs

Image `t + 10` shows the glyph of tile `t`:

| Tile | Glyph | Tile | Glyph | Tile | Glyph | Tile | Glyph |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 sand | `.` | 8 mesa rock | `^` | 16 adobe wall | `#` | 24 townsperson | `p` |
| 1 hardpan | `:` | 9 boulder | `b` | 17 plank floor | `_` | 25 fence | `\|` |
| 2 scrub | `"` | 10 dead tree | `T` | 18 street | `;` | 26 well | `w` |
| 3 road | `=` | 11 cactus | `Y` | 19 doorway | `/` | 27 concrete floor | `` ` `` |
| 4 gravel bed | `,` | 12 plank bridge | `H` | 20 locked door | `+` | 28 concrete wall | `X` |
| 5 salt crust | `s` | 13 town marker | `*` | 21 counter | `n` | 29 steel gate | `G` |
| 6 ford stones | `o` | 14 cave mouth | `O` | 22 healer's cot | `h` | 30 console | `K` |
| 7 deep water | `~` | 15 rubble | `%` | 23 pump head | `P` | 31 stairs | `>` |

An image beyond tile 31 shows `?`. Colour is optional and has no effect on
tests; when used, water is blue, walls and rock are white, the party is bold.

### 2.4 Party panel

Header: `# Name          HP      AC Gun`. One row per slot:
slot digit, name padded to 13, `cur/max` padded to 7, condition (`U`
unconscious, `D` dead, blank otherwise), AC padded to 2, and the equipped
weapon's load as `n` (bits 0 to 6 of its status), `JAM` if jammed, or `-`
without a ranged weapon.

### 2.5 Message log

Each event that carries text (paragraph, message, check, attack, money, item,
promotion, combat end) adds one or more lines. A paragraph opens a pop-up over
rows 1 to 22 with the entry's text wrapped at 76 columns; any key closes it,
and that key is consumed and is not passed to the engine. The headless driver
has no pop-ups: paragraphs never wait (SPEC-04 LR-25). This is the only
difference between the drivers' input streams; the curses driver adds no
token for it.

### 2.6 Overlays

The shop, character screen, use menu and combat panel draw over the viewport
and the party panel (rows 1 to 11, columns 0 to 79). The combat panel lists
each living group as `a) 3 raiders band 3`, then the member whose order is
being chosen and that member's legal keys.

## 3. Map mode keys

| Key (curses) | Token | Effect |
| --- | --- | --- |
| arrow keys, keypad 8 2 4 6 | `UP` `DOWN` `LEFT` `RIGHT` | move or bump (SPEC-03 section 9.6) |
| `L` then a direction | `L` + direction | look: `look` event with the cell's image and class; no time, no draw |
| `T` then a direction | `T` + direction | talk or trade: if the cell is class 11, or class 4 with an impassable record, do exactly what a bump does (without the `bump` event); else UI string 6 |
| `U` | `U` | use menu (section 4.4) |
| `C` | `C` | character screen (section 4.3) |
| `R` | `R` | rest 60 minutes (SPEC-04 LR-17) |
| `S` | `S` | save (SPEC-04 section 13) |
| `O` | `O` | load, after a yes or no prompt |
| `?` | `?` | help overlay (curses only; the headless driver ignores it with an `ignored` event) |
| `Q` | none | quit, after a yes or no prompt (curses only) |

Shops open by stepping onto a shop cell (SPEC-03 lab class 6 is passable); the
trade menu is the shop menu of section 4.2.

## 4. Menus

Every menu accepts `ESC` to back out one level; at the top level of a menu
`ESC` (or `X` where listed) returns to map mode. An unlisted key gives an
`ignored` event and changes nothing. Member choice is a digit `1` to `7`
naming a slot. Item slot choice is a letter: slots 1 to 26 are `a` to `z`,
slots 27 to 30 are `A` to `D`.

### 4.1 Title and party creation

The curses front end opens on a title screen: `N` new game with the scenario's
premade party, `P` create a party, `L` load, `Q` quit. The headless driver
skips the title and starts a new game with the premade party unless the script
says `"start": "create"`, in which case the tokens begin on the creation
screen.

Creation, repeated for slots 1 to 4: type the name (printable characters, then
`ENTER`), gender `M` or `F`, nationality digit `0` to `4`; the six attributes
are rolled (SPEC-04 LR-7) and shown; `R` rerolls, `A` accepts; then skill
buying: skill letters `a` to `z` then `A` to `I` for skill ids 1 to 35 buy one
level each (SPEC-04 LR-10), `ENTER` finishes the character. After slot 4 the
game starts at the scenario start with paragraph 1.

### 4.2 Shop

Mode `shop`: `B` buy, `S` sell, `X` leave.

- Buy (mode `shop_buy`): the list of items sold, keyed `a`, `b`, ... in item id
  order (SPEC-04 LR-50), each with its buy price. An item letter, then a member
  digit (mode `shop_buy_who`), buys one unit and returns to `shop`. `X` returns
  to `shop`.
- Sell: a member digit (mode `shop_sell_who`), then an item slot letter (mode
  `shop_sell_item`) sells that item and returns to `shop`.

### 4.3 Character screen

`C` then a member digit (mode `char_member`; any other key cancels) opens mode
`char` for that member: attributes, HP, AC, level, experience, rank, money,
unspent skill points, skills and items. Keys:

| Key | Effect |
| --- | --- |
| `E` then an item slot letter | equip (SPEC-04 LR-47) |
| `K` then a skill letter (`a` to `z`, `A` to `I` for ids 1 to 35) | raise the skill one level (SPEC-04 LR-46) |
| `J` | unjam the equipped weapon (SPEC-04 LR-39) |
| `D` | dismiss the member (SPEC-04 LR-11), after a yes or no prompt |
| `X` | back to map mode |

### 4.4 Use menu

`U`, then a member digit (the user), then either an item slot letter (a medical
item) or `#` (Bonesetting), then a member digit (the target). Effects are
SPEC-04 LR-47 and LR-48. Outside combat the use happens at once and takes no
time; in combat it is the member's order for the round, resolved in phase 2.

### 4.5 Yes or no prompts

Recruit, heal, load, dismiss and quit prompts take `Y` for yes; any other key
is no and gives `cancel`.

### 4.6 Combat orders

Mode `combat`. The panel asks each conscious member in slot order for an
order:

| Key | Order |
| --- | --- |
| `F` then a group letter | attack that group (a ranged weapon fires in phase 1; melee or unarmed waits for phase 2) |
| `M` then a group letter | close in on that group |
| `R` | reload |
| `J` | unjam |
| `U` then an item slot letter or `#`, then a member digit | use an item or Bonesetting |
| `W` | wait |
| `A` | auto: this member and every later member get the auto order of SPEC-04 LR-33 |
| `X` | flee (accepted only as the first member's key; SPEC-04 LR-43) |
| `ESC` | discard the orders given so far this round and start again with the first member |

The round resolves as soon as the last conscious member has an order. Group
letters `a`, `b`, `c` name the living groups in group order.

### 4.7 Mode names

Mode names appear in the status line, in `checkpoint` snapshots and in
`repeat_until` conditions: `title`, `create`, `map`, `shop`, `shop_buy`,
`shop_buy_who`, `shop_sell_who`, `shop_sell_item`, `char_member`, `char`,
`char_equip`, `char_train`, `use_member`, `use_pick`, `use_target`,
`look_dir`, `interact_dir`, `confirm_recruit`, `confirm_heal`, `confirm_load`,
`confirm_dismiss`, `combat`, `won`, `gameover`.

## 5. Headless mode

### 5.1 Command line

```text
wl --headless --data DIR --script FILE [--seed N] --log OUT.jsonl
```

`DIR` holds the compiled data files (SPEC-05 section 13). `--seed` overrides
the script's seed. The run ends when the script ends, or at once on mode `won`
or `gameover` after the remaining tokens are logged as `ignored`.

Exit codes: 0 the script ran to its end; 2 a `repeat_until` exceeded its `max`;
3 a data error (SPEC-03 L-AC5, L-TR2, L-TR5, or a load failure); 4 a malformed
script.

### 5.2 Script file

The script is the JSON format of `SPEC/scenario/walkthrough.json`:

```text
{ "seed": 20261021,
  "start": "new" | "create",           optional, default "new"
  "script": [ token | macro, ... ] }
```

Macros:

- `{"repeat_until": COND, "keys": [token, ...], "max": N}`: test COND; while it
  is false, send the keys in order and test again; after N rounds with COND
  still false, stop with exit code 2. Conditions: `mode:NAME` (current mode),
  `cell:L,X,Y` (that cell has an entry in the cell-change table of SPEC-04
  LR-19).
- `{"checkpoint": NAME}`: append a `checkpoint` event with the snapshot of
  section 6.4. Consumes no input.

Each token sent, including those inside macros, is logged as an `input` event
before its effects.

### 5.3 Output

JSON Lines: one event object per line, UTF-8, keys in the order of section 6,
no trailing spaces. Every event has `seq` (0, 1, 2, ... in log order) and
`type`. A test compares events by `type` and fields; it never compares `seq`
across runs that differ in their scripts.

## 6. Event schema

UI strings 20, 21, 29 and 30 are display text for `save`, `load`, loot cash and
`heal_all`; the engine emits no `message` event for them.

Order inside one action: a purchase emits `money` (payment) then `buy`; a sale
emits `sell` then `money`; loot emits `item_gain` events, then `money`; an
experience award emits `xp` then any `promote` for that member before the next
member's `xp`.

Members, slots, groups and monsters are numbered from 1. Locations, x and y
are SPEC-03 values. `string` is a map string index of the current location;
`ui` is a LABSTR table 1 index.

### 6.1 Session, movement and map

| Type | Fields | When |
| --- | --- | --- |
| `new_game` | `seed` | first event of a new game |
| `input` | `key` | a token is consumed |
| `ignored` | `key` | the token has no meaning in the current mode |
| `move` | `location, x, y, steps` | the party changes cell |
| `blocked` | `x, y` | the move leaves the map |
| `bump` | `x, y, action_class, action` | the move hits class 11 or an impassable class 4 |
| `look` | `x, y, image, action_class` | look command |
| `map_change` | `location, x, y` | a transition places the party |
| `cell_change` | `location, x, y, action_class, action, image` | SPEC-04 LR-19; one event per write, even when the written triple equals the old one (stepping onto an opened DOOR rewrites its image and emits again) |
| `paragraph` | `n` | SPEC-04 LR-25 |
| `message` | `location, string` or `ui` | a string is shown |
| `natural_heal` | `members` (list of slots) | SPEC-04 LR-17 |
| `day` | `day` | SPEC-04 LR-17 |
| `rest` | none | rest finished |
| `warning` | `reason`, plus details | a reserved class or a tolerated data fault |
| `prompt` | `prompt`, plus `items` (list of item ids for sale, in id order) or `price` (heal) | a menu step opens, exactly at these points: `buy_item` on `B`; `member` after an item letter in the buy list, on `S` in a shop, and on `C`; `item_slot` after the sell member digit and on `E`; `shop` when `X` or `ESC` leaves the buy list; `recruit`, `heal`, `load`, `dismiss` for the yes or no questions. No prompt follows `shop_open`, a purchase or a sale |
| `cancel` | none | a prompt answered no or abandoned |

### 6.2 Party, items, shops, hooks

| Type | Fields |
| --- | --- |
| `check` | `member, skill, level, need, roll` (null when no draw), `success` |
| `unlock` | `x, y` |
| `key_used` | `member, item` |
| `recruit` | `location, npc, slot` |
| `dismiss` | `slot` |
| `heal_all` | `price` |
| `money` | `member, delta, total` |
| `xp` | `member, delta, total` |
| `promote` | `member, level, max_hp, rank` |
| `train` | `member, skill, level, points_left` |
| `item_gain` | `member, item, slot, status` |
| `item_lost` | `item` |
| `shop_open` | `shop` |
| `shop_close` | none |
| `buy` | `member, item, price, slot, status` |
| `sell` | `member, item, price, slot` |
| `char_open` | `member` |
| `char_close` | none |
| `equip` | `member, slot, item, ac` |
| `use_item` | `member, item, target, heal` |
| `bonesetting` | `member, target, success` |
| `save` | `serial` |
| `load` | `serial` |
| `win` | `steps, day, minutes` (time of day in minutes) |

### 6.3 Combat

| Type | Fields |
| --- | --- |
| `encounter_start` | `groups`: list of `{monster, count, band, hp}` (`monster` is the name before the first 0x0A byte; `hp` lists each monster's hit points) |
| `surprised` | none |
| `round_orders` | `round`, `orders`: object from slot (string) to `[order]` or `[order, group]`; order is `fire`, `melee`, `unarmed`, `reload`, `unjam`, `advance`, `use`, `wait` |
| `round_start` | `round` (0 for the surprise round) |
| `attack` | party: `side: "party", member, group, target, need, roll, hit`, plus `damage` on a hit; monsters: `side: "monsters", group, attacker, member, need, roll, hit`, plus `damage` |
| `click` | `member` |
| `jam` | `member, roll, chance` |
| `unjammed` | `member` |
| `reload` | `member, status` |
| `advance` | `member, group, band` |
| `wait` | `member` |
| `no_target` | `member` |
| `monster_dies` | `group, index` |
| `unconscious` | `member` |
| `death` | `member` |
| `group_closes` | `group, band` |
| `flee` | `need, roll, success` |
| `combat_end` | `result` (`victory`, `defeat`, `fled`, `friendly`), plus `rounds` on victory |
| `game_over` | none |

An order given by a key maps to these names: `F` with a ranged or burst weapon
is `fire`, `F` with a melee weapon is `melee`, `F` unarmed is `unarmed`, `M` is
`advance`, `U` is `use`.

### 6.4 Checkpoint snapshot

`checkpoint` has `name` and `state`:

```text
state = {
  "location", "x", "y", "steps", "day", "hour", "minute", "mode",
  "cell_changes": [[location, x, y, class, action, image], ...]   sorted by location, x, y
  "party": [ {
      "slot", "name", "npc" (0 or 1), "level", "xp", "max_hp", "hp",
      "cond" (0, 1, 2), "money", "ac", "rank", "skill_points",
      "items": [[item id, status], ...]   non-empty slots in slot order
      "weapon_slot", "armour_slot"        1-based, 0 = none
  }, ... ],
  "rng_state"                             the generator state after the last draw
}
```

The walkthrough's `expected` blocks are subsets of this object; a test checks
every field present in `expected` for equality and ignores the rest.
`items_excluding_ammo` in `expected` is the sorted list of item ids in `items`
whose item type is not ammunition.

## 7. Acceptance use

- Milestone M6, walkthrough: run `walkthrough.json` headless with seed
  20261021; the run must exit 0, end in mode `won`, and every checkpoint's
  `expected` block must match. `CP5` must equal `CP5-pre-save` in every field of
  the snapshot. The same script must also pass with seeds 1 to 20 (the
  `expected` blocks do not depend on the seed).
- Milestone M6, reference log: `walkthrough-reference-log.json` is the lab
  reference's full event log for seed 20261021. An independent implementation
  built from the spec text reproduced all 1022 events on 21 Oct 2026; SPEC-07
  decides whether a test compares the logs event for event.
- Curses smoke test: `wl --data DIR --render-frame` starts a new game, renders
  the first frame (after the paragraph pop-up is closed) into an 80 x 25 text
  buffer, prints it and exits 0. Row 0 starts with `Saltwell`; row 6 column 19
  is `@`; row 6 column 18 is the glyph of the cell west of the party (`.`,
  sand, for the Dry Fork start at (15,20)); row 6 column 20 is `.` as well.
