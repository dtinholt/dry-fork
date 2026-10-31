# SPEC-05: the Dry Fork scenario

Status: draft for freeze with PREREG-W1, version 1, 21 Oct 2026.
Scope: the lab's own scenario, authored in the formats of SPEC-02 and SPEC-03
and played under the rules of SPEC-04. The machine-readable source is
`SPEC/scenario/*.json`; this file describes it for people and states every
non-plain cell. Where this file and the JSON disagree, the JSON wins and the
disagreement is a defect to report.

## 1. Content rule

Everything here is original lab work: the world, the place names, the maps, the
tiles, the portraits, the 24 paragraphs, the items, the monsters, the people,
the shops and the walkthrough. Nothing is taken from Wasteland's maps,
locations, paragraph text, item names, NPC names or numbers. All game rules are
SPEC-04 lab rules v1 (non-parity).

## 2. The world

Dry Fork is a stretch of desert cut by a river that has mostly stopped. One
branch of the river is dry gravel; the other still holds a channel of deep
water, crossed by one plank bridge and one shallow ford. The town of Saltwell
has a failing pump. The governor valve that would fix it lies in the old
company pumphouse east of the water. The party starts in Saltwell, crosses the
bridge, gets a gate card in the town of Ninemile, takes the valve from
Pumphouse Deep and fits it to the Saltwell pump. Fitting the valve wins.

| Location | Name | Size | Location code | Time per step | Border image |
| --- | --- | --- | --- | --- | --- |
| 0 | Dry Fork overworld | 64 x 64 | 0x80 | 0x0A00 (10 minutes) | 18 (mesa rock) |
| 1 | Saltwell | 32 x 32 | 0x81 | 0x0100 (1 minute) | 35 (fence) |
| 2 | Ninemile | 32 x 32 | 0x82 | 0x0100 (1 minute) | 26 (adobe wall) |
| 3 | Pumphouse Deep | 32 x 32 | 0x83 | 0x0200 (2 minutes) | 38 (concrete wall) |

All four maps are in GAME1 as map indexes 0 to 3, location `L` resolving to
map index `L` (location code `(2 << 6) | L`, SPEC-02 section 3.4). Map info for
every map: encounter frequency 0, tileset 0, random monster types 0, maximum
random encounters 0, heal rate 0, bytes +0x00, +0x01, +0x03, +0x04 and the 37
combat string bytes 0 (SPEC-03 L-MI1, L-MI3).

The new game starts at location 1, cell (15,20), day 1, 08:00, seed 20261021,
with paragraph 1 shown and the premade party of section 10.

## 3. Tiles

Tileset 0 holds 32 tiles. A cell's image byte is tile id + 10 (SPEC-03 section
7). Passability comes only from the action class (SPEC-03 L-MV2): the scenario
puts class 11 with action 0 on every cell that shows a tile marked "no" below,
unless section 5 lists another class for that cell. The glyph is the curses
character of SPEC-06 section 2.3.

| Id | Image | Name | Walkable | Description |
| --- | --- | --- | --- | --- |
| 0 | 10 | sand | yes | Pale wind-rippled sand, the default ground of the overworld. |
| 1 | 11 | hardpan | yes | Cracked grey clay flat with hairline fissures. |
| 2 | 12 | scrub | yes | Low grey-green brush in clumps on sand. |
| 3 | 13 | road | yes | Two rutted wheel tracks with a hump of weeds between them. |
| 4 | 14 | gravel bed | yes | Rounded river stones in a dry channel, lighter than sand. |
| 5 | 15 | salt crust | yes | White salt plate with a faint hexagonal crack pattern. |
| 6 | 16 | ford stones | yes | Flat stepping stones laid across dark water. |
| 7 | 17 | deep water | no | Slow dark-green water with a single highlight ripple. |
| 8 | 18 | mesa rock | no | Layered red-brown cliff face with a shadowed lower third. |
| 9 | 19 | boulder | no | One round tan boulder with a dark crack, on sand. |
| 10 | 20 | dead tree | no | Bare grey trunk with three forked branches. |
| 11 | 21 | cactus | no | Single green column cactus with two arms. |
| 12 | 22 | plank bridge | yes | Weathered boards running left to right, rope rails top and bottom. |
| 13 | 23 | town marker | yes | Overworld icon: three small flat-roofed huts in a cluster. |
| 14 | 24 | cave mouth | yes | Overworld icon: a black arch cut into a rock hump. |
| 15 | 25 | rubble | no | Heap of broken concrete and bent rebar. |
| 16 | 26 | adobe wall | no | Tan mud-brick wall with two darker brick courses. |
| 17 | 27 | plank floor | yes | Brown floorboards running vertically. |
| 18 | 28 | street | yes | Packed earth, darker than sand, with faint cart marks. |
| 19 | 29 | doorway | yes | Open door frame in an adobe wall, dark interior strip. |
| 20 | 30 | locked door | no | Heavy plank door with a black iron hasp and padlock. |
| 21 | 31 | counter | no | Waist-high wooden counter seen from above, with a ledger. |
| 22 | 32 | healer's cot | no | Narrow cot with a white sheet and a red cross on the blanket. |
| 23 | 33 | pump head | no | Iron hand-pump with a curved handle over a stone trough. |
| 24 | 34 | townsperson | no | Standing figure in a long coat and wide hat, seen from above. |
| 25 | 35 | fence | no | Split-rail fence running left to right. |
| 26 | 36 | well | no | Round stone well with a dark centre. |
| 27 | 37 | concrete floor | yes | Grey poured floor with an expansion joint across it. |
| 28 | 38 | concrete wall | no | Dark grey block wall with a lighter top edge. |
| 29 | 39 | steel gate | no | Barred steel gate, five vertical bars, a lock box at the centre. |
| 30 | 40 | console | no | Metal desk with a dim green screen and a row of switches. |
| 31 | 41 | stairs | yes | Concrete steps descending toward the top of the tile. |

Placeholder art (the compiler draws these until real art exists): tile `t` is
filled with palette color `t mod 16`, with a one-pixel border of color
`(t + 8) mod 16`. Tests never compare tile pixels beyond the round trip of
SPEC-02 section 6.

## 4. Portraits

Four portraits, 96 x 84 at 4 bits per pixel, raw portrait ids 1 to 4. Each has
one animation script whose updates net to zero over one pass (SPEC-02 L-PT1).
The character record has no portrait byte, so the `portrait` field of the
member records in `party.json` and in the map NPC sections is display
metadata that stays in the JSON (and in `npcs.json`); the compiler does not
write it. Monster records carry raw id 1 in their portrait byte so that the
last byte of every map's encrypted prefix is non-zero (section 5.6). The curses
front end draws no portraits.

- Raw id 1, Orla Penn: Head and shoulders, three-quarter view facing left. Narrow face, sun-creased eyes, short grey-streaked hair under a flat-brimmed hat pushed back. A rifle sling crosses the right shoulder. Background: a pale sky band over a dark horizon line. Palette: tans, a faded blue scarf, dark brown hat. Animation: the eyes blink every 40 frames; the scarf end lifts in two frames of wind.
- Raw id 2, Teodor Lusk: Head and shoulders, facing the viewer. Broad face, heavy black beard, round wire spectacles pushed up on the forehead, grease smear on one cheek. Apron strap over a collarless shirt. Background: a workbench wall with three hanging spanners as dark silhouettes. Palette: dark greys, black, one warm orange highlight on the spectacles. Animation: the spectacles drop onto the nose and back in three frames.
- Raw id 3, Wren Abara: Head and shoulders, profile facing right. Close-cropped dark hair, a thin scar along the jaw, one silver ring in the ear, chin slightly raised. Collar of a sand-coloured duster turned up. Background: plain ochre wall with a shadow cast from the left. Palette: deep brown skin tones, ochre, cream, one silver highlight. Animation: the head turns to the viewer over four frames and back.
- Raw id 4, Sallow Kett: Head and shoulders, facing the viewer, filling the frame. Large bald head, split lower lip, a broken nose, small eyes under a heavy brow, smiling. A coil of copper wire over one shoulder. Background: steel cage bars in dark grey behind him. Palette: pale skin, copper orange, steel greys. Animation: the smile widens in two frames; the wire coil glints in one frame.

Placeholder art: portrait `p` is filled with color `4 + p`, with a centred
48 x 42 rectangle of color 15; its one update XORs the 8 bytes at offset 2000
with 0xFF and its script is `(20, 0), (20, 0)`.

## 5. Maps

Notation: cells are (x, y), x from the left, y from the top, both from 0.
"Action" is the 1-based slot in the class's record list (SPEC-03 L-AC2,
L-AC3); records are listed with their fields. String indexes are into that
map's string table. Cells not listed are class 0 action 0 when their tile is
walkable and class 11 action 0 when it is not.

### 5.1 Dry Fork overworld (location 0)

A 64 x 64 desert. A mesa border rings the map. The wet branch of the river is a
column of deep water at x = 31 from y = 1 to y = 62, with gravel banks at
x = 29, 30, 32 and 33. The plank bridge is at (31,41) on the east-west road
(y = 41). The ford is at (31,55). The dry branch runs from (30,30) north-west
to (6,6) as a two-cell gravel band. Roads: y = 41 from x = 10 to 40; x = 40
from y = 28 to 47; y = 28 from x = 40 to 43; y = 47 from x = 41 to 43. Markers:
Saltwell (10,40), Ninemile (44,28), the Pumphouse cave mouth (44,47). The
scatter of scrub, boulders, dead trees, cacti, hardpan and salt is fixed by the
tile array in `map0-overworld.json`.

```text
     0000000000111111111122222222223333333333444444444455555555556666
     0123456789012345678901234567890123456789012345678901234567890123
  0  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  1  ^..............T...."".......,,~,,.............".."b.....Y...T.^
  2  ^."....""...................",,~,,....."..............Y..."....^
  3  ^.""...."........."..."......,,~,,............"....."..........^
  4  ^..."........................,,~,,....."..."...................^
  5  ^......................."."..,,~,,:...Y."."."......."....".."..^
  6  ^...Y",,.."....b.".".."...".",,~,,:.......^^^^....."...........^
  7  ^."....,,...T..."".sss"......,,~,,:.".....^^^^"..."."""."......^
  8  ^.....".,,.........ssss.."...,,~,,T""...."^^^^."".^^^^^^^Y.T...^
  9  ^......T.,,"..."...ssss....".,,~,,...""..T...."...^^^^^^^...T..^
 10  ^..:::::::,,.."..............,,~,,......".".......^^^^^^^....."^
 11  ^..:::::::.,,................,,~,,......."........^^^^^^^....."^
 12  ^.":::::::".,,...."s"s.....".,,~,,..."...ssss."...........b.Y..^
 13  ^..""..".....,,...s"ss:T::"..,,~,,.......ssss....."..T....."...^
 14  ^.....^^^^^...,,..ssss::::.".,,~,,.......sss".."........."."...^
 15  ^.....^^^^^..".,,..:::::::...,,~,,.............................^
 16  ^.....^^^^^.....,,.:::::":...,,~,,.."...Y.........".....T.b....^
 17  ^.....^^^^^......,,::::::Y...,,~,,.".".".......::::":"..T......^
 18  ^....b."......T...,,.........,,~,,........."...:::::::.."."....^
 19  ^.............."..",,....T...,,~,,..."......"..:::::::.."......^
 20  ^."."...."..........,,".....",,~,,....."."...T................"^
 21  ^......""..........Y.,,......,,~,,.............................^
 22  ^.:::"...."...........,,Y..::,,~,,..""....."""....""..."....b..^
 23  ^"::::".T....T::"......,,b.:",,~,,...".............""....."....^
 24  ^.::::...".""::"........,,.::,,~,,...........:::::Y""..."......^
 25  ^.:""b"......:::.........,,..,,~,,...."......:::":::.........."^
 26  ^"..............^^^^^^..b.,,.,,~,,.".T.Y.:::::":::::......"....^
 27  ^......Yb.."."b.^^^^^^.T..",,,,~,,"..."".":::::::"::........b..^
 28  ^...."......"...^^^^^^".....,,,~,,....."====*:":::::."...::::..^
 29  ^...."....."."..^^^^^^.....".,,~,,......=:::::".".."Y....:"::..^
 30  ^..........".......::Y.......,,~,,......=..............^^^^^...^
 31  ^......".........."::b.....".,,~,,......=""........."""^^^^^.".^
 32  ^........".........:ssss."...,,~,,......=........b.....^^^^^"..^
 33  ^."............."..:ssss.....,,~,,..."..=.............Y^^^^^.."^
 34  ^..."..""..........:ssss...".,,~,,......=..............^^^^^...^
 35  ^........."................T.,,~,,."..""=".......T.."..^^^^^...^
 36  ^.."............"....".......,,~,,....".=.."..."......."...."".^
 37  ^.........Y".................,,~,,.."...=.....".......Y........^
 38  ^"......Y.T::::::............,,~,,..."..=.."."......Y....."....^
 39  ^..T.......::::::.b..........,,~,,....."=........."..T.........^
 40  ^.......T.*......"......:":::,,~,,......=..".".............."""^
 41  ^.........=====================H=========...".T............""."^
 42  ^..".T.b.."......"......::"::,,~,,....."=........Y......"......^
 43  ^"......................:::::,,~,,....".=......TY..".".....b...^
 44  ^.........."".b.".b....."::::,,~,,......=..."..................^
 45  ^.....".......".........b...",,~,,..."b.=......."..............^
 46  ^...........Y...."...........,,~,,....Y.=."..................".^
 47  ^...."..........."...........,,~,,......====O....."..........".^
 48  ^.."............b...Y........,,~,,.............................^
 49  ^................."..........,,~,,Y.......".".....Y....".......^
 50  ^......"...........T^^^^^^...,,~,,.T.....".........T........"..^
 51  ^"....Tb............^^^^^^"..,,~,,.............................^
 52  ^............"T...".^^^^^^...,,~,,..^^^^^..........."..........^
 53  ^Y.........T........^^^^^^...,,~,,Y.^^^^^..."......."........""^
 54  ^".:::"::".."...T"..^^^^^^...,,~,,..^^^^^......................^
 55  ^..:::"::"............".""...,,~,,..^^^^^.........."...."......^
 56  ^..T"::::...^^^^^......"....",,~,,T"..""."...........T.....b.".^
 57  ^...........^^^^^........T".",,~,,................"..........."^
 58  ^...........^^^^^..."........,,~,,......"................."....^
 59  ^...........^^^^^....".......,,~,,...............".............^
 60  ^....T."...........".........,,~,,.."....T.".............".....^
 61  ^..T...............""".......,,~,,"....."......".Y.....b...."..^
 62  ^....Y..."".."...".........".,,~,,..".........."........"."....^
 63  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

Non-plain cells other than walls (594 wall cells are class 11, action 0):

| X | Y | Tile | Class | Action | Record | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 18 | 12 | 2 | 3 | 2 | vis 3, hit 1, message 7 "Dust hounds come loping out of the scrub.", groups mob 2 (dust hound) rnd 4, flags 0; tail (0, 0) | Encounter 2: dust hounds, rnd(4) |
| 22 | 22 | 4 | 3 | 4 | vis 3, hit 1, message 9 "Scavengers rise from the riverbed stones.", groups mob 4 (scavenger) 2; mob 1 (raider) 1, flags 0; tail (5, 2) | Encounter 4: riverbed scavengers, 2 scavengers and 1 raider; then loot rnd(40) coins |
| 24 | 25 | 0 | 1 | 3 | messages 3 "Read paragraph 16." | Dry fork riverbed, paragraph 16 |
| 44 | 28 | 13 | 10 | 2 | absolute, no confirm, message 0, target location 2 (1,16) | Ninemile marker to Ninemile (1,16) |
| 20 | 34 | 5 | 1 | 4 | messages 4 "Bleached cattle bones lie in a ring around a dry waterhole." | Bones message |
| 52 | 35 | 2 | 3 | 3 | vis 3, hit 1, message 8 "Glass beetles boil up out of the salt.", groups mob 3 (glass beetle) 2, flags 0; tail (0, 0) | Encounter 3: glass beetles, 2 |
| 10 | 40 | 13 | 10 | 1 | absolute, no confirm, message 0, target location 1 (15,30) | Saltwell marker to Saltwell (15,30) |
| 26 | 41 | 3 | 1 | 1 | messages 1 "Read paragraph 7." | Signpost, paragraph 7 |
| 30 | 41 | 3 | 3 | 1 | vis 3, hit 1, message 6 "Read paragraph 8.", groups mob 1 (raider) 3, flags 0; tail (5, 1) | Encounter 1: road raiders, 3 raiders; then loot 75 coins |
| 31 | 41 | 12 | 1 | 2 | messages 2 "Read paragraph 9."; tail (0, 0) | Plank bridge, paragraph 9, shown once (tail to class 0) |
| 45 | 45 | 0 | 1 | 5 | messages 5 "Wheel ruts from a heavy wagon run off into the scrub and stop." | Wheel ruts message |
| 44 | 47 | 14 | 10 | 3 | absolute, no confirm, message 0, target location 3 (3,2) | Cave mouth to Pumphouse Deep (3,2) |
| 31 | 55 | 7 | 4 | 2 | message 10 "Dark water, too deep to wade without care.", impassable, tile image 17; tail (4, 1) | Lock: ford, Fording 25 |

Records reached only through a tail or a lock:

- class 4 slot 1: message 0, passable, tile image 16 (reached only as a replacement)
- class 5 slot 1: replacement (0, 0); cash fixed 75 (reached only as a replacement)
- class 5 slot 2: replacement (0, 0); cash rnd 40 (reached only as a replacement)

Strings:

| Index | Text |
| --- | --- |
| 0 | (empty) |
| 1 | Read paragraph 7. |
| 2 | Read paragraph 9. |
| 3 | Read paragraph 16. |
| 4 | Bleached cattle bones lie in a ring around a dry waterhole. |
| 5 | Wheel ruts from a heavy wagon run off into the scrub and stop. |
| 6 | Read paragraph 8. |
| 7 | Dust hounds come loping out of the scrub. |
| 8 | Glass beetles boil up out of the salt. |
| 9 | Scavengers rise from the riverbed stones. |
| 10 | Dark water, too deep to wade without care. |
| 11 | Read paragraph 17. |
| 12 | The current pushes you back to the bank. |
| 13 | (empty) |
| 14 | (empty) |
| 15 | (empty) |

Monsters (map monster section; index is the 1-based monster index of encounter
records, SPEC-03 L-MB1):

| Index | Name | Sturdiness | Combat rating | Random damage (d6) | Max group | AC | Fixed damage | Weapon type | Type | Portrait |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | raider (plural +"s") | 12 | 6 | 1 | 4 | 1 | 0 | 3 | 3 | 1 |
| 2 | dust hound (plural +"s") | 8 | 8 | 1 | 6 | 0 | 0 | 1 | 1 | 1 |
| 3 | glass beetle (plural +"s") | 16 | 5 | 1 | 3 | 3 | 1 | 1 | 1 | 1 |
| 4 | scavenger (plural +"s") | 12 | 6 | 1 | 4 | 1 | 1 | 2 | 3 | 1 |

NPC section: none (SPEC-03 L-EN4).

### 5.2 Saltwell (location 1)

A fenced town. The dry goods store is the north-west building, the healer the
north-east building, the pump stands in the square at (15,11), the gate is the
gap in the south fence at (15,31) and (16,31).

```text
     00000000001111111111222222222233
     01234567890123456789012345678901
  0  ||||||||||||||||||||||||||||||||
  1  |..............................|
  2  |.#########......#############.|
  3  |.#_______#......#___________#.|
  4  |.#__nnn__#......#____h______#.|
  5  |.#_______#......#___________#.|
  6  |.#_______#..Y...#___________#.|
  7  |.####/####......######/######.|
  8  |.....;................;.......|
  9  |.....;;;;;;;;;;;;;;;;;;;......|
 10  |..T.........;;;;;.............|
 11  |............;;P;;......Y......|
 12  |............;;;;;.............|
 13  |..............;...............|
 14  |..............;.......b.......|
 15  |..w...........;...............|
 16  |..............;...............|
 17  |.......p......;...............|
 18  |.......;;;;;;;;...............|
 19  |..............;.......T.......|
 20  |..Y...........;...............|
 21  |..............;..........Y....|
 22  |..............;...............|
 23  |.....b........;...............|
 24  |..............;...............|
 25  |..............;.........b.....|
 26  |..............;...............|
 27  |..T...........;...............|
 28  |..............;...............|
 29  |..............;...............|
 30  |..............;;..............|
 31  |||||||||||||||;;|||||||||||||||
```

Non-plain cells other than walls (196 wall cells):

| X | Y | Tile | Class | Action | Record | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 22 | 4 | 22 | 11 | 0 | none | Healer's cot, Saltwell |
| 6 | 5 | 17 | 6 | 1 | shop list 0, message 5 "Saltwell Dry Goods." | Shop list 0, Saltwell Dry Goods |
| 6 | 7 | 19 | 1 | 2 | messages 2 "Read paragraph 3." | Dry goods doorway, paragraph 3 |
| 23 | 7 | 19 | 1 | 3 | messages 3 "Read paragraph 5." | Healer's doorway, paragraph 5 |
| 15 | 11 | 23 | 11 | 0 | none | Saltwell pump: win hook |
| 13 | 12 | 18 | 1 | 4 | messages 4 "The trough is green at the edges and nearly empty." | Trough message |
| 8 | 17 | 24 | 11 | 1 | message 6 "Read paragraph 6." | NPC 0 of Saltwell: Orla Penn |
| 15 | 29 | 18 | 1 | 1 | messages 1 "Read paragraph 2." | Saltwell sign, paragraph 2 |
| 15 | 31 | 18 | 10 | 1 | absolute, no confirm, message 0, target location 0 (10,41) | Saltwell gate to overworld (10,41) |
| 16 | 31 | 18 | 10 | 2 | absolute, no confirm, message 0, target location 0 (10,41) | Saltwell gate to overworld (10,41) |

Strings:

| Index | Text |
| --- | --- |
| 0 | (empty) |
| 1 | Read paragraph 2. |
| 2 | Read paragraph 3. |
| 3 | Read paragraph 5. |
| 4 | The trough is green at the edges and nearly empty. |
| 5 | Saltwell Dry Goods. |
| 6 | Read paragraph 6. |
| 7 | Orla shrugs. Some other time, then. |

Monsters:

| Index | Name | Sturdiness | Combat rating | Random damage (d6) | Max group | AC | Fixed damage | Weapon type | Type | Portrait |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | stray dog (plural +"s") | 4 | 2 | 1 | 2 | 0 | 0 | 1 | 1 | 1 |

NPC section: NPC 0 = Orla Penn (record in section 10).

### 5.3 Ninemile (location 2)

A walled town entered from the west gate (x = 0, y = 15 to 17). The gunsmith is
the north-west building, the outfitter the north-east building, the storehouse
stands east of the main street, the healer is south-east and the dining hall
south-west.

```text
     00000000001111111111222222222233
     01234567890123456789012345678901
  0  ################################
  1  #..............................#
  2  #.###########....#############.#
  3  #.#_________#....#___________#.#
  4  #.#___nnn___#....#__p____n___#.#
  5  #.#_________#....#___________#.#
  6  #.#####/#####....######/######.#
  7  #.......;..............;.......#
  8  #.......;;;;;;;;;;;;;;;;.......#
  9  #..............;...............#
 10  #..T...........;.......#######.#
 11  #..............;.......#_____#.#
 12  #..............;.......#_____#.#
 13  #..............;.......#_____#.#
 14  #..............;.......###+###.#
 15  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;...#
 16  ;..............;.........;.....#
 17  ;..............;..p......;.....#
 18  #..............;.........;.....#
 19  #.Y............;.......#####...#
 20  #..............;.......#___#...#
 21  #.###########..;.......#_h_#...#
 22  #.#_________#..;.......#___#...#
 23  #.#___n_____#..;.......##/##...#
 24  #.#_________#..;.........;.....#
 25  #.#####/#####..;;;;;;;;;;;.....#
 26  #.......;......;...............#
 27  #.......;;;;;;;;......b........#
 28  #..............................#
 29  #.....Y...............T........#
 30  #..............................#
 31  ################################
```

Non-plain cells other than walls (251 wall cells):

| X | Y | Tile | Class | Action | Record | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 20 | 4 | 24 | 11 | 2 | message 12 "Read paragraph 14." | NPC 1 of Ninemile: Wren Abara (leader CHA 17) |
| 7 | 5 | 17 | 6 | 1 | shop list 1, message 5 "Ninemile Gunsmith." | Shop list 1, Ninemile Gunsmith |
| 25 | 5 | 17 | 6 | 2 | shop list 2, message 6 "Ninemile Outfitter." | Shop list 2, Ninemile Outfitter |
| 7 | 6 | 19 | 1 | 2 | messages 2 "Read paragraph 11." | Gunsmith doorway, paragraph 11 |
| 10 | 9 | 0 | 1 | 4 | messages 4 "A dog asleep in the shade opens one eye and closes it again." | Sleeping dog message |
| 26 | 12 | 17 | 5 | 1 | replacement (0, 0); item 11 Gate card fixed 0 | Loot: Gate card |
| 26 | 14 | 20 | 4 | 2 | message 7 "A padlock hangs from the storehouse hasp.", impassable, tile image 30; tail (4, 1) | Lock: storehouse door, Tumblers 30 |
| 0 | 15 | 18 | 10 | 1 | absolute, no confirm, message 0, target location 0 (43,28) | Ninemile west gate to overworld (43,28) |
| 0 | 16 | 18 | 10 | 2 | absolute, no confirm, message 0, target location 0 (43,28) | Ninemile west gate to overworld (43,28) |
| 2 | 16 | 0 | 1 | 1 | messages 1 "Read paragraph 10." | Ninemile entry, paragraph 10 |
| 0 | 17 | 18 | 10 | 3 | absolute, no confirm, message 0, target location 0 (43,28) | Ninemile west gate to overworld (43,28) |
| 18 | 17 | 24 | 11 | 1 | message 10 "Read paragraph 13." | NPC 0 of Ninemile: Teodor Lusk |
| 25 | 21 | 22 | 11 | 0 | none | Healer's cot, Ninemile |
| 10 | 23 | 17 | 5 | 2 | replacement (0, 0); item 10 Rope coil fixed 0 | Loot: Rope coil |
| 7 | 25 | 19 | 1 | 3 | messages 3 "Read paragraph 15." | Dining hall doorway, paragraph 15 |

Records reached only through a tail or a lock:

- class 4 slot 1: message 0, passable, tile image 29 (reached only as a replacement)

Strings:

| Index | Text |
| --- | --- |
| 0 | (empty) |
| 1 | Read paragraph 10. |
| 2 | Read paragraph 11. |
| 3 | Read paragraph 15. |
| 4 | A dog asleep in the shade opens one eye and closes it again. |
| 5 | Ninemile Gunsmith. |
| 6 | Ninemile Outfitter. |
| 7 | A padlock hangs from the storehouse hasp. |
| 8 | Read paragraph 12. |
| 9 | The padlock holds. |
| 10 | Read paragraph 13. |
| 11 | Teodor squints at your leader and goes back to his clock. |
| 12 | Read paragraph 14. |
| 13 | Wren looks your leader up and down and laughs. |
| 14 | (empty) |
| 15 | (empty) |

Monsters:

| Index | Name | Sturdiness | Combat rating | Random damage (d6) | Max group | AC | Fixed damage | Weapon type | Type | Portrait |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | stray dog (plural +"s") | 4 | 2 | 1 | 2 | 0 | 0 | 1 | 1 | 1 |

NPC section: NPC 0 = Teodor Lusk, NPC 1 = Wren Abara (records in section 10).

### 5.4 Pumphouse Deep (location 3)

A concrete maze under a rock hump. Stairs at (3,1) lead up. The main corridor
runs south from the stairs and east along y = 6 to the vault gate at (16,6) and
the governor chamber behind it. A lower corridor along y = 11 leads east to the
console at (26,11); the spares cage below it opens when the console is worked.
A west gallery along y = 20 lies behind a rubble heap at (4,20).

```text
     00000000001111111111222222222233
     01234567890123456789012345678901
  0  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  1  XXX>XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  2  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  3  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  4  XXX`XXXXXXXXXXXXX``````XXXXXXXXX
  5  XXX`XXXXXXXXXXXXX``````XXXXXXXXX
  6  XXX`````````````G``P```XXXXXXXXX
  7  XXX`XXXXXXXXXXXXX``````XXXXXXXXX
  8  XXX`XXXXXXXXXXXXX``````XXXXXXXXX
  9  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
 10  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
 11  XXX```````````````````````KXXXXX
 12  XXX`XXXXXXXXXXGXXXXXXXXXXXXXXXXX
 13  XXX`XXXXXXXX`````XXXXXXXXXXXXXXX
 14  XXX`XXXXXXXX``p``XXXXXXXXXXXXXXX
 15  XXX`XXXXXXXX`````XXXXXXXXXXXXXXX
 16  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
 17  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
 18  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
 19  XXX`XXXXXXXXXXXXXXXXXXXXXXXXXXXX
 20  XXX`%```````````XXXXXXXXXXXXXXXX
 21  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 22  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 23  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 24  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 25  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 26  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 27  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 28  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 29  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 30  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 31  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Non-plain cells other than walls (911 wall cells):

| X | Y | Tile | Class | Action | Record | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 1 | 31 | 10 | 1 | absolute, no confirm, message 0, target location 0 (44,48) | Pumphouse stairs to overworld (44,48) |
| 3 | 3 | 27 | 1 | 1 | messages 1 "Read paragraph 18." | Foot of the stairs, paragraph 18 |
| 21 | 4 | 27 | 5 | 2 | replacement (0, 0); item 12 Governor valve fixed 0 | Loot: Governor valve |
| 9 | 6 | 27 | 3 | 1 | vis 3, hit 1, message 4 "Read paragraph 19.", groups mob 1 (pump crawler) 4, flags 0; tail (5, 1) | Encounter 5: pump crawlers, 4; then loot Field kit (status 3) |
| 16 | 6 | 29 | 4 | 5 | message 10 "A steel gate with a lock box at its centre.", impassable, tile image 39; tail (4, 4) | Lock: vault gate, key Gate card or Circuitry 60 |
| 17 | 6 | 27 | 1 | 2 | messages 2 "Read paragraph 22." | Governor chamber, paragraph 22 |
| 26 | 11 | 30 | 4 | 3 | message 7 "A console with a dim green screen hums faintly.", impassable, tile image 40; tail (11, 0) | Lock: console, Terminals 30; opens the cage gate (14,12) |
| 14 | 12 | 29 | 4 | 2 | message 6 "The way is shut.", impassable, tile image 39 | Door: spares cage gate, opened by the console |
| 12 | 13 | 27 | 5 | 3 | replacement (0, 0); item 9 Field kit fixed 3 | Loot: Field kit (status 3) |
| 14 | 14 | 24 | 11 | 1 | message 16 "Read paragraph 23." | NPC 0 of Pumphouse Deep: Sallow Kett |
| 4 | 20 | 15 | 4 | 7 | message 13 "A heap of rubble chokes the side passage.", impassable, tile image 25; tail (4, 6) | Lock: rubble, Scaling 35, tool Rope coil |
| 10 | 20 | 27 | 3 | 2 | vis 3, hit 1, message 5 "Two scrap drones lift off the pipes, whirring.", groups mob 2 (scrap drone) rnd 2, flags 0; tail (0, 0) | Encounter 6: scrap drones, rnd(2) |
| 15 | 20 | 27 | 1 | 3 | messages 3 "Old pipes run along this gallery, sweating rust." | Pipe gallery message |

Records reached only through a tail or a lock:

- class 4 slot 1: message 0, passable, tile image 37 (reached only as a replacement)
- class 4 slot 4: message 0, passable, tile image 37 (reached only as a replacement)
- class 4 slot 6: message 0, passable, tile image 37 (reached only as a replacement)
- class 5 slot 1: replacement (0, 0); item 9 Field kit fixed 3 (reached only as a replacement)

Strings:

| Index | Text |
| --- | --- |
| 0 | (empty) |
| 1 | Read paragraph 18. |
| 2 | Read paragraph 22. |
| 3 | Old pipes run along this gallery, sweating rust. |
| 4 | Read paragraph 19. |
| 5 | Two scrap drones lift off the pipes, whirring. |
| 6 | The way is shut. |
| 7 | A console with a dim green screen hums faintly. |
| 8 | Read paragraph 20. |
| 9 | The screen fills with symbols and then goes dark again. |
| 10 | A steel gate with a lock box at its centre. |
| 11 | Read paragraph 21. |
| 12 | The lock box clicks and stays shut. |
| 13 | A heap of rubble chokes the side passage. |
| 14 | You scramble over the rubble. |
| 15 | The rubble shifts under your hands and you slide back down. |
| 16 | Read paragraph 23. |
| 17 | Sallow shakes his head slowly. |
| 18 | (empty) |
| 19 | (empty) |

Monsters:

| Index | Name | Sturdiness | Combat rating | Random damage (d6) | Max group | AC | Fixed damage | Weapon type | Type | Portrait |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | pump crawler (plural +"s") | 14 | 7 | 1 | 6 | 1 | 0 | 1 | 2 | 1 |
| 2 | scrap drone (plural +"s") | 10 | 7 | 1 | 3 | 2 | 1 | 4 | 5 | 1 |

NPC section: NPC 0 = Sallow Kett (record in section 10).

### 5.5 Lab cell hooks

`hooks.json`, compiled to LABHOOKS.JSON (SPEC-04 section 6). Message fields are
string indexes of the hook's map; images are image bytes.

| Location | X | Y | Kind | Parameters | Note |
| --- | --- | --- | --- | --- | --- |
| 2 | 26 | 14 | lock | {"skill": 14, "difficulty": 30, "key_item": 0, "tool_item": 0, "success_message": 8, "fail_message": 9, "remote": null} | Lock: storehouse door, Tumblers 30 |
| 0 | 31 | 55 | lock | {"skill": 17, "difficulty": 25, "key_item": 0, "tool_item": 0, "success_message": 11, "fail_message": 12, "remote": null} | Lock: ford, Fording 25 |
| 3 | 26 | 11 | lock | {"skill": 29, "difficulty": 30, "key_item": 0, "tool_item": 0, "success_message": 8, "fail_message": 9, "remote": {"x": 14, "y": 12, "new_class": 4, "new_action": 1}} | Lock: console, Terminals 30; opens the cage gate (14,12) |
| 3 | 16 | 6 | lock | {"skill": 23, "difficulty": 60, "key_item": 11, "tool_item": 0, "success_message": 11, "fail_message": 12, "remote": null} | Lock: vault gate, key Gate card or Circuitry 60 |
| 3 | 4 | 20 | lock | {"skill": 16, "difficulty": 35, "key_item": 0, "tool_item": 10, "success_message": 14, "fail_message": 15, "remote": null} | Lock: rubble, Scaling 35, tool Rope coil |
| 1 | 8 | 17 | recruit | {"npc": 0, "min_leader_cha": 0, "refuse_message": 7, "cleared_image": 28} | NPC 0 of Saltwell: Orla Penn |
| 2 | 18 | 17 | recruit | {"npc": 0, "min_leader_cha": 10, "refuse_message": 11, "cleared_image": 28} | NPC 0 of Ninemile: Teodor Lusk |
| 2 | 20 | 4 | recruit | {"npc": 1, "min_leader_cha": 17, "refuse_message": 13, "cleared_image": 27} | NPC 1 of Ninemile: Wren Abara (leader CHA 17) |
| 3 | 14 | 14 | recruit | {"npc": 0, "min_leader_cha": 0, "refuse_message": 17, "cleared_image": 37} | NPC 0 of Pumphouse Deep: Sallow Kett |
| 1 | 22 | 4 | healer | {"price": 30} | Saltwell healer, 30 coins |
| 2 | 25 | 21 | healer | {"price": 40} | Ninemile healer, 40 coins |
| 1 | 15 | 11 | win | {"item": 12, "win_paragraph": 24, "not_yet_paragraph": 4} | Fit the Governor valve |

### 5.6 Encoding checks

Every map was encoded with `SPEC/reference/fixtures_gen.py` `build_map` (the
SPEC-03 lab encoder) and decoded with its `map_decode`: action classes, action
bytes and strings come back identical for all four maps; no map block contains
`msq` after its header; every string uses only characters of dictionary D
(SPEC-02 section 9.3). Block sizes: overworld 7874 bytes (encrypted prefix
6460), Saltwell 2406 (1957), Ninemile 2848 (2260), Pumphouse Deep 2682 (2059),
with the premade NPC records as written by the compiler. String lists are
padded with empty strings to a multiple of 4 (SPEC-02 L-ST1). Every monster
record carries portrait 1, because a monster record ends the encrypted prefix
and a final zero byte would make the prefix ambiguous (SPEC-01 section 2.7,
SPEC-03 L-EN2). Every listed cell is reachable from the start once the locks
are open.

## 6. Encounters

Six encounter types, each a class 3 record. Derived values follow SPEC-04
LR-26 and LR-27: hit points `sturdiness div 4 + rnd(sturdiness)`, experience
`sturdiness x (AC + 1)`, to-hit base `20 + 5 x combat rating`, speed = combat
rating, ranged when weapon type is 3 or more.

| Type | Location, cell | Groups | Start band | XP per monster | After victory |
| --- | --- | --- | --- | --- | --- |
| 1 Road raiders | 0, (30,41) | 3 raiders (fixed) | 3 | 24 | loot: 75 coins, then plain road |
| 2 Dust hounds | 0, (18,12) | rnd(4) dust hounds | 2 | 8 | plain |
| 3 Glass beetles | 0, (52,35) | 2 glass beetles | 2 | 64 | plain |
| 4 Riverbed scavengers | 0, (22,22) | 2 scavengers and 1 raider | 2 and 3 | 24 each | loot: rnd(40) coins |
| 5 Pump crawlers | 3, (9,6) | 4 pump crawlers (fixed) | 2 | 28 | loot: Field kit (status 3) |
| 6 Scrap drones | 3, (10,20) | rnd(2) scrap drones | 3 | 30 | plain |

The walkthrough fights types 1 and 5. Types 2, 3, 4 and 6 sit off its route.

## 7. Items

Item id N is record N - 1 of all three shop lists; records 12 to 93 are eight
zero bytes. Type byte = class code << 3 with low flags 0. Damage byte: dice
count in the high nibble and die sides in the low nibble for weapons and the
medical kit, AC bonus for armour.

| Id | Name | Price | Class | Type byte | Capacity | Skill | Damage byte | Ammo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pipe club | 15 | melee | 0x08 | 0 | 1 | 0x16 | 0 |
| 2 | Hook knife | 12 | melee | 0x08 | 0 | 2 | 0x14 | 0 |
| 3 | Ranch pistol | 60 | ranged | 0x10 | 6 | 4 | 0x18 | 4 |
| 4 | Pistol rounds | 8 | ammo | 0x18 | 6 | 0 | 0x00 | 0 |
| 5 | Lever rifle | 140 | ranged | 0x10 | 8 | 5 | 0x26 | 6 |
| 6 | Rifle rounds | 14 | ammo | 0x18 | 8 | 0 | 0x00 | 0 |
| 7 | Hide vest | 30 | armour | 0x20 | 0 | 0 | 0x01 | 0 |
| 8 | Plate jacket | 110 | armour | 0x20 | 0 | 0 | 0x03 | 0 |
| 9 | Field kit | 25 | medical | 0x28 | 3 | 12 | 0x24 | 0 |
| 10 | Rope coil | 10 | tool | 0x30 | 0 | 16 | 0x00 | 0 |
| 11 | Gate card | 0 | quest | 0x38 | 0 | 0 | 0x00 | 0 |
| 12 | Governor valve | 0 | quest | 0x38 | 0 | 0 | 0x00 | 0 |

Descriptions: 1 Pipe club: A length of iron pipe with tape wound round one end. 2 Hook knife: A short curved blade for cutting rope and hide. 3 Ranch pistol: A revolver that holds six rounds. 4 Pistol rounds: One box of six pistol rounds. One box fills the pistol once. 5 Lever rifle: A lever-action rifle that holds eight rounds. 6 Rifle rounds: One box of eight rifle rounds. One box fills the rifle once. 7 Hide vest: Stitched goat hide over a canvas lining. AC 1. 8 Plate jacket: Canvas jacket with flattened can lids sewn in rows. AC 3. 9 Field kit: Bandages, splints and a bottle of spirit. Three uses, heals 2d4. 10 Rope coil: Fifty feet of braided rope. Adds 20 to Scaling checks for the member who carries it. 11 Gate card: A punched steel card stamped with the pumping company's mark. 12 Governor valve: A brass valve the size of a fist, its spindle still greased.

## 8. Skills (LABSKILL.BIN)

The 36-entry table: entry 0 is a dummy; entries 1 to 35 are the skills of
SPEC-04 section 3.2. Byte 0 = `(min IQ << 3) | cost`, byte 1 = attribute offset.

| Id | Name | IQ | Attribute | Cost | Byte 0 | Byte 1 | Engine effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | (dummy) | 0 | none | 0 | 0x00 | 0x00 | none |
| 1 | Bludgeon | 3 | STR | 1 | 0x19 | 0x0E | To-hit level for items whose skill byte is 1 (clubs, bars). |
| 2 | Edged arms | 3 | AGL | 1 | 0x19 | 0x12 | To-hit level for items whose skill byte is 2 (knives, hatchets). |
| 3 | Grappling | 3 | STR | 1 | 0x19 | 0x0E | To-hit level when no weapon is equipped; unarmed attacks per action = 1 + floor(level / 2). |
| 4 | Handgun | 5 | AGL | 1 | 0x29 | 0x12 | To-hit level for items whose skill byte is 4 (pistols). |
| 5 | Longarm | 6 | AGL | 1 | 0x31 | 0x12 | To-hit level for items whose skill byte is 5 (rifles). |
| 6 | Spreadgun | 6 | AGL | 1 | 0x31 | 0x12 | To-hit level for items whose skill byte is 6 (shotguns). No such item in Dry Fork. |
| 7 | Autofire | 9 | AGL | 2 | 0x4A | 0x12 | To-hit level for items whose skill byte is 7 (burst weapons). No such item in Dry Fork. |
| 8 | Hurling | 4 | AGL | 1 | 0x21 | 0x12 | To-hit level for items whose skill byte is 8 (thrown). No such item in Dry Fork. |
| 9 | Tube launcher | 10 | AGL | 2 | 0x52 | 0x12 | To-hit level for items whose skill byte is 9. No such item in Dry Fork. |
| 10 | Archery | 6 | AGL | 1 | 0x31 | 0x12 | To-hit level for items whose skill byte is 10. No such item in Dry Fork. |
| 11 | Evasion | 8 | AGL | 2 | 0x42 | 0x12 | Adds its level to the member's AC. |
| 12 | First aid | 10 | IQ | 1 | 0x51 | 0x0F | When the member uses a medical item, the heal adds 2 x level. |
| 13 | Bonesetting | 14 | IQ | 2 | 0x72 | 0x0F | Use on an unconscious member: skill check, difficulty 20; success sets the target to 1 HP and conscious. |
| 14 | Tumblers | 9 | AGL | 1 | 0x49 | 0x12 | Named by barrier checks (locks). |
| 15 | Strongbox | 12 | IQ | 2 | 0x62 | 0x0F | Named by barrier checks (safes). |
| 16 | Scaling | 3 | STR | 1 | 0x19 | 0x0E | Named by barrier checks (cliffs, walls). |
| 17 | Fording | 3 | STR | 1 | 0x19 | 0x0E | Named by barrier checks (water). |
| 18 | Lookout | 8 | IQ | 1 | 0x41 | 0x0F | Surprise check at encounter start uses the best Lookout in the party. |
| 19 | Trailcraft | 8 | IQ | 1 | 0x41 | 0x0F | Random encounter chance on map 0 falls by 5 per level of the best member. |
| 20 | Haggling | 7 | CHA | 1 | 0x39 | 0x14 | Buy and sell prices use the best Haggling in the party. |
| 21 | Smooth talk | 9 | CHA | 1 | 0x49 | 0x14 | Lowers an NPC's leader-CHA requirement by 2 per level of the slot-1 member. |
| 22 | Gunsmithing | 10 | IQ | 1 | 0x51 | 0x0F | Unjam check uses it; each level lowers the member's jam chance by 1 point (minimum 1). |
| 23 | Circuitry | 12 | IQ | 2 | 0x62 | 0x0F | Named by barrier checks (wired locks). |
| 24 | Blasting | 11 | IQ | 2 | 0x5A | 0x0F | Named by barrier checks (charges). |
| 25 | Engines | 11 | IQ | 2 | 0x5A | 0x0F | Named by barrier checks (machinery). |
| 26 | Salvage | 7 | LCK | 1 | 0x39 | 0x10 | Victory money adds 5 x best level per monster killed. |
| 27 | Quiet foot | 8 | AGL | 1 | 0x41 | 0x12 | Random encounter chance on maps 1 to 3 falls by 5 per level of the best member. |
| 28 | Foraging | 6 | IQ | 1 | 0x31 | 0x0F | Rest heals each conscious member an extra HP equal to the best level. |
| 29 | Terminals | 13 | IQ | 2 | 0x6A | 0x0F | Named by barrier checks (consoles). |
| 30 | Signals | 12 | IQ | 2 | 0x62 | 0x0F | Named by barrier checks (radios). |
| 31 | Mapcraft | 8 | IQ | 1 | 0x41 | 0x0F | Named by barrier checks (route finding). |
| 32 | Beast lore | 7 | IQ | 1 | 0x39 | 0x0F | Named by barrier checks (animals). |
| 33 | Dice and cards | 6 | LCK | 1 | 0x31 | 0x10 | Named by barrier checks (games of chance). |
| 34 | Old script | 11 | IQ | 1 | 0x59 | 0x0F | Named by barrier checks (inscriptions). |
| 35 | Command | 12 | CHA | 2 | 0x62 | 0x14 | Flee chance adds 5 x level of the slot-1 member. |

## 9. Shops

Shop lists 0 to 2, each 94 records with the item records of section 7; only
the stock byte differs. Stock 0 means not sold here.

- Shop list 0, Saltwell Dry Goods: Pipe club (id 1, stock 255), Ranch pistol (id 3, stock 4), Pistol rounds (id 4, stock 255), Hide vest (id 7, stock 3), Field kit (id 9, stock 255), Rope coil (id 10, stock 255)
- Shop list 1, Ninemile Gunsmith: Ranch pistol (id 3, stock 2), Pistol rounds (id 4, stock 255), Lever rifle (id 5, stock 2), Rifle rounds (id 6, stock 255)
- Shop list 2, Ninemile Outfitter: Hook knife (id 2, stock 255), Hide vest (id 7, stock 255), Plate jacket (id 8, stock 2), Field kit (id 9, stock 255), Rope coil (id 10, stock 255)

## 10. People

### 10.1 Premade party (savegame slots 1 to 4)

Nationality names (LABSTR table 5): 0 Basin, 1 Upland, 2 Coast, 3 Delta,
4 Plateau. HP max follows SPEC-04 LR-8 (Hessa 24, Tobin 26, Maro 21, Dell 22).
Rank: Drifter. DEX 0. No unspent skill points.

| Slot | Name | Sex | Nat. | STR | IQ | LCK | SPD | AGL | CHA | Money | XP | Level | Skills (id:level) | Items (id:status) | Weapon slot | Armour slot |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | F | 0 | 14 | 13 | 11 | 12 | 14 | 15 | 120 | 90 | 1 | Handgun 2, Haggling 1, Smooth talk 1, Lookout 1 | Ranch pistol:6, Pistol rounds:2, Hide vest:0 | 1 | 3 |
| 2 | Tobin Ash | M | 1 | 16 | 10 | 12 | 11 | 12 | 9 | 60 | 90 | 1 | Longarm 2, Bludgeon 1, Fording 1, Grappling 1 | Lever rifle:8, Rifle rounds:1, Pipe club:0 | 1 | 0 |
| 3 | Maro Quill | M | 0 | 11 | 16 | 13 | 13 | 15 | 10 | 80 | 90 | 1 | Tumblers 2, Circuitry 1, Gunsmithing 1, Handgun 1, First aid 1 | Ranch pistol:6, Pistol rounds:1 | 1 | 0 |
| 4 | Dell Ostrow | F | 2 | 12 | 15 | 12 | 12 | 13 | 12 | 70 | 90 | 1 | First aid 2, Bonesetting 1, Handgun 1, Terminals 1, Lookout 1 | Ranch pistol:6, Pistol rounds:1, Field kit:3 | 1 | 0 |

### 10.2 NPC recruits (map NPC sections)

Records are written like the party records, with the NPC flag 1, curHP = maxHP
per LR-8 (Orla 27, Teodor 26, Wren 24, Sallow 27) and rank from their level.

| Saltwell NPC 0 | Orla Penn | F | 1 | 13 | 11 | 14 | 14 | 15 | 11 | 25 | 200 | 2 | Longarm 2, Lookout 2, Trailcraft 1 | Lever rifle:8, Rifle rounds:2 | 1 | 0 | portrait 1
| Ninemile NPC 0 | Teodor Lusk | M | 0 | 12 | 15 | 10 | 9 | 11 | 10 | 40 | 150 | 2 | Engines 2, Terminals 2, Bludgeon 1, Gunsmithing 1 | Pipe club:0, Hide vest:0 | 1 | 2 | portrait 2
| Ninemile NPC 1 | Wren Abara | F | 2 | 10 | 14 | 15 | 15 | 16 | 13 | 15 | 150 | 2 | Handgun 2, Quiet foot 2, Salvage 1 | Ranch pistol:6, Pistol rounds:2 | 1 | 0 | portrait 3
| Pumphouse Deep NPC 0 | Sallow Kett | M | 1 | 17 | 9 | 11 | 10 | 11 | 8 | 5 | 120 | 1 | Bludgeon 2, Grappling 2, Scaling 1 | Pipe club:0 | 1 | 0 | portrait 4

| Recruit | Where | Leader CHA needed | Paragraph |
| --- | --- | --- | --- |
| Orla Penn | Saltwell (8,17) | 0 | 6 |
| Teodor Lusk | Ninemile (18,17) | 10 | 13 |
| Wren Abara | Ninemile (20,4) | 17 (15 with Hessa's Smooth talk 1) | 14 |
| Sallow Kett | Pumphouse Deep (14,14) | 0 | 23 |

## 11. Strings

LABSTR.BIN (SPEC-02 section 12.3) holds six tables, all with dictionary D:

| Table | Content |
| --- | --- |
| 0 | intro and title: "", "Dry Fork", "A lab scenario for the clean room engine.", "Press any key." |
| 1 | general messages: string N = UI string N below, gaps empty |
| 2 | inventory: 0 empty, 1 to 35 skill names, 35 + N = name of item N |
| 3 | ranks by level: Drifter, Hand, Outrider, Warden, Steward, Marshal, Old hand |
| 4 | attribute names in record order: Strength, IQ, Luck, Speed, Agility, Dexterity, Charisma |
| 5 | nationality names: Basin, Upland, Coast, Delta, Plateau |

UI strings (table 1). `{name}` is byte 0x0B, `{num}` is byte 0x0F.

| Id | Text |
| --- | --- |
| 1 | There is no room in the party. |
| 2 | Not enough money. |
| 3 | {name} has no room for that. |
| 4 | The way is shut. |
| 5 | That cannot be equipped. |
| 6 | Nothing happens. |
| 7 | {name} is now level {num}. |
| 8 | {name} gains {num} experience. |
| 9 | {name} is unconscious. |
| 10 | {name} is dead. |
| 11 | {name}'s weapon jams. |
| 12 | {name} clears the jam. |
| 13 | {name} reloads. |
| 14 | Click. |
| 15 | The party is surprised! |
| 16 | The party wins the fight. |
| 17 | The party has fallen. |
| 18 | The party gets away. |
| 19 | The party cannot get away. |
| 20 | Game saved. |
| 21 | Game loaded. |
| 22 | Load the saved game? (Y/N) |
| 23 | Heal the party for {num}? (Y/N) |
| 24 | Take this one into the party? (Y/N) |
| 25 | Buy, Sell, or eXit? |
| 26 | Which member? (1 to 7) |
| 27 | Which item? |
| 28 | No one has room. |
| 29 | The party finds {num} coins. |
| 30 | The party is healed. |
| 31 | That cannot be sold. |
| 32 | No ammunition for that weapon. |
| 33 | {name} is not conscious. |
| 40 | A padlock hangs from the storehouse hasp. |
| 41 | The padlock holds. |
| 42 | Dark water, too deep to wade without care. |
| 43 | The current pushes you back to the bank. |
| 44 | A console with a dim green screen hums faintly. |
| 45 | The screen fills with symbols and then goes dark again. |
| 46 | A steel gate with a lock box at its centre. |
| 47 | The lock box clicks and stays shut. |
| 48 | A heap of rubble chokes the side passage. |
| 49 | The rubble shifts under your hands and you slide back down. |
| 50 | {name} takes a punched steel card. |
| 51 | {name} lifts the governor valve from its slot. |
| 52 | {name} takes a field kit from the shelf. |
| 53 | {name} takes a rope coil from a hook. |
| 60 | Orla shrugs. Some other time, then. |
| 61 | Teodor squints at your leader and goes back to his clock. |
| 62 | Wren looks your leader up and down and laughs. |
| 63 | Sallow shakes his head slowly. |

## 12. The paragraph book

Twenty-four entries, 40 to 120 words each. A map string "Read paragraph N."
shows entry N (SPEC-04 LR-25).

**1.** Saltwell has one pump and the pump is dying. For three weeks the handle has brought up less water each morning, and now it coughs air by noon. The town council, which is four people and a dog, has pooled what coin it has and hired you. Somewhere east of the wet branch of the Dry Fork stands the old company pumphouse. Its governor valve, if it still exists, would set the Saltwell pump right. Bring it back before the trough goes dry.

**2.** A board nailed to the fence post reads SALTWELL, POPULATION ENOUGH. Someone has scratched out ENOUGH and written FEWER. Below it, in fresher paint, a second board lists the town rules. No shooting inside the fence. No drinking from the trough before the animals. No credit at the store. The paint on the last rule is the thickest.

**3.** The dry goods store smells of lamp oil and dust. Shelves run to the ceiling, though most of them hold empty jars kept for the day there is something to put in them. The owner watches you from behind a counter worn pale by elbows. A slate by the door says rounds come six to a box and are sold one box at a time.

**4.** The pump handle moves with a dry rasp. A thin dribble wets the trough and stops. Underneath the head a gap shows where the governor valve should sit; someone has jammed a carved wooden plug in its place, and the plug is splitting. Nothing here will hold for long without the real part from the pumphouse across the wet branch.

**5.** A woman with rolled sleeves and a wet cloth over one shoulder looks up from a cot. Bottles stand in rows on a plank shelf, each labelled in a careful hand. She sets bones, stitches cuts and asks for payment up front, because, as she puts it, patients who wake up fixed have short memories.

**6.** A lean woman leans on a rifle by the well road, watching the gate as if she expects it to move. She says her name is Orla Penn and that she has walked the Dry Fork more times than the riverbed has flooded. She heard about the pump. She will ride with you to the pumphouse and back for a share of whatever the council pays, and she will keep watch at night without being asked.

**7.** A leaning signpost stands where the track from Saltwell nears the gravel of the old river. One arm points north-east and reads NINEMILE. A second arm, newer, points south-east and reads PUMPHOUSE, CLOSED. A third arm once pointed somewhere else, but only a nail remains. The wind has sanded the letters so thin you read them partly by touch.

**8.** Three figures rise from behind the bridge rail with scarves over their faces and guns already up. One of them calls out that the bridge costs whatever you carry, payable now. The plank bridge is the only dry crossing of the wet branch for miles, and they know it. Nobody waits for an answer.

**9.** The plank bridge sways under your boots. Someone has carved tally marks into the rail, dozens of them, and nailed a hand-drawn map to the last post with the bridge circled in charcoal. The water below moves slowly south, dark and quiet. On the far bank the road climbs toward land the Saltwell council has not seen in years.

**10.** Ninemile is a wide street and two rows of adobe buildings that have outlived whatever business built them. A gunsmith's sign hangs on the north side and an outfitter's on the far corner. People here keep their hats low and their voices lower. A storehouse at the east end has a new padlock on an old door, which in Ninemile counts as news.

**11.** Racks of long guns line the gunsmith's back wall, most of them missing a part. The smith files a spring at the bench without looking up. A card nailed to the counter reads REPAIRS IN THREE DAYS, ROUNDS TODAY. Behind him a door stands open on a yard where tin cans hang from a wire, every one of them holed.

**12.** The padlock gives with a click and the hasp swings free. Inside, the storehouse holds crates of rusted fittings, a broken cart axle and a desk with one drawer. In the drawer lies a punched steel card stamped with the old pumping company's mark, the kind that once opened company gates. Someone in Ninemile has been keeping it safe or keeping it hidden.

**13.** A broad man in a grease-black apron sits on an upturned bucket, taking apart a clock with a bent nail. He introduces himself as Teodor Lusk, mechanic, and says he worked at the pumphouse as a boy before the company left. He remembers the consoles and the gates and roughly where the spare parts were kept. He wants to see it again, and he wants paying.

**14.** Wren Abara sits on the outfitter's counter with her boots on a crate of bandages. She is quick, quiet and openly unimpressed. She has crossed the beetle flats twice and come back both times, which she says is the only qualification that counts. She will join a party whose leader can talk her into it, and she makes it plain that this is hard.

**15.** The long room was a dining hall once. Benches are stacked against the walls and the counter at the back holds a row of clean, empty cups. An old man sweeping the floor tells you, without being asked, that the pumphouse crawlers sleep in the cool of the main corridor and wake when they hear boots on concrete. He sweeps around your feet and says no more.

**16.** The dry fork of the river runs north-west here, a broad bed of rounded stones with not a drop between them. Old flood marks stain a boulder higher than your head. Your boots find a rusted length of pipe half buried in the gravel, stamped with the same company mark you saw on the signpost. The company ran water through here once.

**17.** You find the shallow line where the stones lie close to the surface and cross with the water at your knees. The current is stronger than it looks and cold enough to ache. On the far bank you stamp the water out of your boots. The stones you set in place behind you will make the crossing easier next time.

**18.** Concrete steps lead down into the dark under the rock hump. The air at the bottom is cool and smells of wet iron. A painted arrow on the wall points down the corridor toward a word too faded to read. Somewhere far ahead, a drip lands in standing water at a slow, steady count.

**19.** Something moves in the corridor ahead, low and many-legged, and then there are four of them: pale crawling things the size of dogs, with plated backs and pincers that click on the concrete. They have made a nest of rags and wire in the cool of the passage, and they come at you all at once.

**20.** The console screen warms from black to green. Most of the switches do nothing, but one row still answers, and with a heavy clunk somewhere below, a gate on the lower corridor slides open. Text crawls across the screen listing maintenance stores that no longer exist. The last line reads SPARES CAGE UNLOCKED, which is the only good news it has.

**21.** The steel gate rattles in its frame as the lock box reads the card. A green lamp you had not noticed blinks once, and the bars slide aside with a long scrape. Beyond lies the governor chamber, where the main pump once ran. The floor is dry, and footprints in the dust show nobody has been through in years.

**22.** The great pump stands silent in the middle of the chamber, taller than two men. A rack along the wall holds spare parts in labelled slots, most of them empty. One slot still holds a brass valve the size of a fist, wrapped in waxed cloth. The label beneath it reads GOVERNOR, SALTWELL LINE, in a hand that took care over it.

**23.** A big man with a split lip sits in the corner of the spares cage, surrounded by empty tins. He says his name is Sallow Kett and that he came down here looking for copper and got shut in when the gate jammed. That was eleven days ago, by his count of the tins. He will carry anything, hit anything and follow you anywhere with daylight in it.

**24.** The valve seats with a soft click and the pump handle comes up heavy. Then water, cold and clean, gushes into the trough until it spills over the lip and darkens the street. People come out of every door in Saltwell. The council, all four of them and the dog, stand at the front. Someone starts counting the coins they owe you, and nobody minds that the count takes a long time.

Where each entry is triggered: 1 new game; 2 Saltwell gate (15,29); 3 dry goods doorway (6,7); 4 Saltwell pump bumped without the valve; 5 healer's doorway (23,7); 6 Orla Penn; 7 signpost (26,41); 8 raiders' encounter message; 9 plank bridge (31,41), once (the PRINT tail turns the cell into class 0); 10 Ninemile entry (2,16); 11 gunsmith doorway (7,6); 12 storehouse unlock; 13 Teodor Lusk; 14 Wren Abara; 15 dining hall doorway (7,25); 16 dry fork riverbed (24,25); 17 ford unlock; 18 foot of the Pumphouse stairs (3,3); 19 crawlers' encounter message; 20 console unlock; 21 vault gate unlock; 22 governor chamber (17,6); 23 Sallow Kett; 24 the win.

## 13. Compiler outputs

The scenario compiler reads `scenario.json` and the files it lists and writes:
GAME1 (four maps, the savegame of the new game, shop lists 0 to 2),
LABTABLES.BIN, LABSTR.BIN, LABSKILL.BIN, LABHOOKS.JSON, PARAGRAPHS.JSON,
ALLHTDS1 and ALLPICS1, plus the remaining SPEC-02 section 12.1 files with
placeholder content. Milestone M4 checks that reading those files back through
the engine's own loaders gives the JSON content again: tiles, classes, action
bytes, records, monsters, NPC records, strings, items, stock, skills, party.

## 14. Walkthrough

`walkthrough.json` holds the exact input script (414 tokens) and the ten
checkpoints, plus one auxiliary checkpoint for the save and load round trip.
The script reaches the win in 358 steps (limit 400). Two kinds of macro keep it
valid for any seed: `repeat [A] until mode:map` fights a combat to its end with
auto orders, and `repeat [UP] until cell:2,26,14` bumps the storehouse door
until the lock opens. The lab reference replayed the script for seeds 1 to 5000:
every run won, every checkpoint matched its `expected` block, and no member was
ever knocked down. An independent implementation written from SPEC-03,
SPEC-04 and SPEC-06 and this scenario data alone, without access to the lab
reference, reproduced the full reference event log for seed 20261021 (1022
events) and passed every `expected` block for seeds 1 to 300.

### 14.1 Step list

Direction runs are written "UP x8". Menu keys are single characters: shop `B`
buy, `S` sell, `X` leave, an item letter, then a member digit; character screen
`C`, member digit, `E` equip, slot letter, `X`; `S` save, `O` load, `Y` yes.
Notes in brackets are what the step triggers with seed 20261021.

**To CP1** (step 0): 

**To CP2** (step 24): UP x8, LEFT, UP x4, LEFT x8, UP (paragraph 3), UP, UP (message 5; shop list 0 opens), B, c, 3 (slot 3 buys item 4 for 7), B, c, 4 (slot 4 buys item 4 for 7), S, 2, c (slot 2 sells item 1 for 8), B, d, 2 (slot 2 buys item 7 for 28), X, C, 2, E, c (slot 2 equips item 7, AC 3), X

**To CP3** (step 39): DOWN, DOWN (paragraph 3), DOWN, RIGHT, DOWN x10, RIGHT, UP (paragraph 6; prompt recruit), Y (recruit into slot 5)

**To CP4** (step 79): RIGHT x7, DOWN x10, DOWN (paragraph 2), DOWN, DOWN (enter location 0 at (10,41)), RIGHT x15, RIGHT (paragraph 7), RIGHT x3, RIGHT (encounter: 3 raider; paragraph 8), repeat [A] until mode:map (max 30; reference seed: 5 rounds)

**To CP5-pre-save** (step 145): RIGHT (paragraph 9), RIGHT, UP x13, RIGHT x11, RIGHT (enter location 2 at (1,16)), RIGHT (paragraph 10), UP x9, RIGHT x5, UP (paragraph 11), UP (message 5; shop list 1 opens), B, d, 2 (slot 2 buys item 6 for 13), X, DOWN (paragraph 11), DOWN, RIGHT x16, UP x2, RIGHT, RIGHT (message 6; shop list 2 opens), B, c, 1 (slot 1 buys item 8 for 104), X, C, 1, E, d (slot 1 equips item 8, AC 5), X

**To CP5** (step 145): S (saved), O (prompt load), Y (loaded)

**To CP6** (step 165): LEFT x2, DOWN x4, LEFT, DOWN x6, RIGHT x4, repeat [UP] until cell:2,26,14 (max 40; reference seed: 4 rounds), UP x2, UP (slot 1 gains item 11)

**To CP7** (step 194): DOWN x4, LEFT x8, DOWN (paragraph 13; prompt recruit), Y (recruit into slot 6), RIGHT x4, DOWN x8, RIGHT x3, UP x2, UP (prompt heal), Y (healed for 40)

**To CP8** (step 259): DOWN x2, LEFT x3, UP x8, LEFT x19, LEFT (paragraph 10), LEFT, LEFT (enter location 0 at (43,28)), DOWN, RIGHT, DOWN x17, DOWN (enter location 3 at (3,2)), DOWN (paragraph 18), DOWN x3, RIGHT x5, RIGHT (encounter: 4 pump crawler; paragraph 19), repeat [A] until mode:map (max 30; reference seed: 3 rounds)

**To CP9** (step 273): RIGHT x6, RIGHT (message 10; unlock (16,6); paragraph 21), RIGHT, RIGHT (paragraph 22), UP x2, RIGHT x3, RIGHT (slot 1 gains item 12)

**To CP10** (step 358): DOWN, LEFT x3, DOWN, LEFT (paragraph 22), LEFT x14, UP x2, UP (paragraph 18), UP, UP (enter location 0 at (44,48)), LEFT, UP x7, LEFT x13, UP, LEFT x19, LEFT (enter location 1 at (15,30)), UP (paragraph 2), UP x17, UP (paragraph 24; win)

### 14.2 Checkpoints and expected outcomes

Positions are (x, y). Money is coins. "Items" lists the non-ammunition item ids
held, sorted. Cell changes are written (location, x, y) -> (class, action,
image). Hit points are asserted at CP1, CP2, CP3 (all members at maxHP) and at
CP7 (all members at maxHP after the healer); elsewhere they depend on the
random stream and appear only in `reference_seeded`.

**CP1**: New game in Saltwell: four PCs at (15,20), 08:00 day 1, paragraph 1 shown.
Location 1 at (15,20), step 0, day 1 08:00, mode `map`.
Cell changes: none.

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 1 | 90 | 24 | 120 | 3 | Drifter | 1 | 3 | [3, 7] |
| 2 | Tobin Ash | 1 | 90 | 26 | 60 | 2 | Drifter | 1 | 0 | [1, 5] |
| 3 | Maro Quill | 1 | 90 | 21 | 80 | 3 | Drifter | 1 | 0 | [3] |
| 4 | Dell Ostrow | 1 | 90 | 22 | 70 | 2 | Drifter | 1 | 0 | [3, 9] |

**CP2**: Saltwell Dry Goods: two boxes of pistol rounds bought, pipe club sold, hide vest bought and worn by Tobin.
Location 1 at (6,5), step 24, day 1 08:24, mode `map`.
Cell changes: none.

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 1 | 90 | 24 | 120 | 3 | Drifter | 1 | 3 | [3, 7] |
| 2 | Tobin Ash | 1 | 90 | 26 | 40 | 3 | Drifter | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 1 | 90 | 21 | 73 | 3 | Drifter | 1 | 0 | [3] |
| 4 | Dell Ostrow | 1 | 90 | 22 | 63 | 2 | Drifter | 1 | 0 | [3, 9] |

**CP3**: Orla Penn recruited into slot 5.
Location 1 at (8,18), step 39, day 1 08:39, mode `map`.
Cell changes: (1,8,17) -> (0,0,28).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 1 | 90 | 24 | 120 | 3 | Drifter | 1 | 3 | [3, 7] |
| 2 | Tobin Ash | 1 | 90 | 26 | 40 | 3 | Drifter | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 1 | 90 | 21 | 73 | 3 | Drifter | 1 | 0 | [3] |
| 4 | Dell Ostrow | 1 | 90 | 22 | 63 | 2 | Drifter | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 200 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |

**CP4**: Bridge raiders beaten; PCs promoted to level 2; 75 coins looted.
Location 0 at (30,41), step 79, day 1 12:19, mode `map`.
Cell changes: (0,30,41) -> (0,0,13), (1,8,17) -> (0,0,28).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 104 | 28 | 195 | 3 | Hand | 1 | 3 | [3, 7] |
| 2 | Tobin Ash | 2 | 104 | 31 | 40 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 104 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 104 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 214 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |

**CP5-pre-save** (auxiliary): Auxiliary: state just before the save; CP5 must equal it field for field, generator state included.
Location 2 at (25,5), step 145, day 1 17:28, mode `map`.
Cell changes: (0,30,41) -> (0,0,13), (0,31,41) -> (0,0,22), (1,8,17) -> (0,0,28).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 104 | 28 | 91 | 5 | Hand | 1 | 4 | [3, 7, 8] |
| 2 | Tobin Ash | 2 | 104 | 31 | 27 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 104 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 104 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 214 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |

**CP5**: Ninemile purchases done, plate jacket worn by Hessa; saved and loaded: state equals the pre-save state.
Location 2 at (25,5), step 145, day 1 17:28, mode `map`.
Cell changes: (0,30,41) -> (0,0,13), (0,31,41) -> (0,0,22), (1,8,17) -> (0,0,28).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 104 | 28 | 91 | 5 | Hand | 1 | 4 | [3, 7, 8] |
| 2 | Tobin Ash | 2 | 104 | 31 | 27 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 104 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 104 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 214 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |

**CP6**: Storehouse unlocked with Tumblers; Gate card looted.
Location 2 at (26,12), step 165, day 1 17:48, mode `map`.
Cell changes: (0,30,41) -> (0,0,13), (0,31,41) -> (0,0,22), (1,8,17) -> (0,0,28), (2,26,12) -> (0,0,27), (2,26,14) -> (4,1,29).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 104 | 28 | 91 | 5 | Hand | 1 | 4 | [3, 7, 8, 11] |
| 2 | Tobin Ash | 2 | 104 | 31 | 27 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 114 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 104 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 214 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |

**CP7**: Teodor Lusk recruited into slot 6; party healed to full for 40 coins.
Location 2 at (25,22), step 194, day 1 18:17, mode `map`.
Cell changes: (0,30,41) -> (0,0,13), (0,31,41) -> (0,0,22), (1,8,17) -> (0,0,28), (2,18,17) -> (0,0,28), (2,26,12) -> (0,0,27), (2,26,14) -> (4,1,29).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 104 | 28 | 51 | 5 | Hand | 1 | 4 | [3, 7, 8, 11] |
| 2 | Tobin Ash | 2 | 104 | 31 | 27 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 114 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 104 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 214 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |
| 6 | Teodor Lusk | 2 | 150 | 26 | 40 | 3 | Hand | 1 | 2 | [1, 7] |

**CP8**: Pump crawlers beaten in Pumphouse Deep; Field kit looted.
Location 3 at (9,6), step 259, day 1 22:32, mode `map`.
Cell changes: (0,30,41) -> (0,0,13), (0,31,41) -> (0,0,22), (1,8,17) -> (0,0,28), (2,18,17) -> (0,0,28), (2,26,12) -> (0,0,27), (2,26,14) -> (4,1,29), (3,9,6) -> (0,0,37).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 122 | 28 | 51 | 5 | Hand | 1 | 4 | [3, 7, 8, 9, 11] |
| 2 | Tobin Ash | 2 | 122 | 31 | 27 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 132 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 122 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 232 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |
| 6 | Teodor Lusk | 2 | 168 | 26 | 40 | 3 | Hand | 1 | 2 | [1, 7] |

**CP9**: Vault gate opened with the Gate card; Governor valve looted.
Location 3 at (21,4), step 273, day 1 23:00, mode `map`.
Cell changes: (0,30,41) -> (0,0,13), (0,31,41) -> (0,0,22), (1,8,17) -> (0,0,28), (2,18,17) -> (0,0,28), (2,26,12) -> (0,0,27), (2,26,14) -> (4,1,29), (3,9,6) -> (0,0,37), (3,16,6) -> (4,4,37), (3,21,4) -> (0,0,37).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 122 | 28 | 51 | 5 | Hand | 1 | 4 | [3, 7, 8, 9, 11, 12] |
| 2 | Tobin Ash | 2 | 122 | 31 | 27 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 132 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 122 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 232 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |
| 6 | Teodor Lusk | 2 | 168 | 26 | 40 | 3 | Hand | 1 | 2 | [1, 7] |

**CP10**: Valve fitted at the Saltwell pump: game won.
Location 1 at (15,12), step 358, day 2 07:08, mode `won`.
Cell changes: (0,30,41) -> (0,0,13), (0,31,41) -> (0,0,22), (1,8,17) -> (0,0,28), (2,18,17) -> (0,0,28), (2,26,12) -> (0,0,27), (2,26,14) -> (4,1,29), (3,9,6) -> (0,0,37), (3,16,6) -> (4,4,37), (3,21,4) -> (0,0,37).

| Slot | Name | Level | XP | Max HP | Money | AC | Rank | Weapon slot | Armour slot | Items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hessa Brand | 2 | 122 | 28 | 51 | 5 | Hand | 1 | 4 | [3, 7, 8, 9, 11, 12] |
| 2 | Tobin Ash | 2 | 122 | 31 | 27 | 3 | Hand | 1 | 3 | [5, 7] |
| 3 | Maro Quill | 2 | 132 | 25 | 73 | 3 | Hand | 1 | 0 | [3] |
| 4 | Dell Ostrow | 2 | 122 | 26 | 63 | 2 | Hand | 1 | 0 | [3, 9] |
| 5 | Orla Penn | 2 | 232 | 27 | 25 | 3 | Hand | 1 | 0 | [5] |
| 6 | Teodor Lusk | 2 | 168 | 26 | 40 | 3 | Hand | 1 | 2 | [1, 7] |

### 14.3 What the walkthrough exercises

Shop buy, ammunition stacking, sell, equip and AC change (CP2); a recruit
(CP3); a transition, a paragraph trigger, an encounter with a surprise check,
ranged and melee resolution, reloads, a promotion of all four PCs and loot cash
through a record tail (CP4); a one-shot paragraph on the bridge, two shops, a second equip, save
and load (CP5); a
lock opened by skill with retries, experience for the check, a loot pickup
(CP6); a second recruit and a paid healer (CP7); a melee-heavy encounter and
item loot through a tail (CP8); a lock opened by a key item and two paragraph
triggers (CP9); a long walk back across two transitions and the win hook
(CP10). With seed 20261021 the reference run also shows a jam, a failed and a
successful unjam, and a surprise round in the crawler fight.
