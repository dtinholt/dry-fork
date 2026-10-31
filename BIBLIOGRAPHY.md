# Wasteland (1988) clean-room engine: bibliography (web sweep, 21 Oct 2026)

Ranked by usefulness for an engine rebuild. Fetch limits: the Fandom "Definitive Deconstruction"
wiki answered 402 to automated reads; NMA, GOG forum and openmw docs 403/503. Read manually later.

## Tier 1: format specifications (DOS version)
1. wastelib, Klaus Reimer, MIT. https://github.com/kayahr/wastelib (TypeScript, pushed 2026-10-17);
   docs https://kayahr.github.io/wastelib/ and doc/formats/: game.md, rotating-xor.md, huffman.md,
   vertical-xor.md, map.md (marked incomplete), savegame.md, shopitemlist.md, paragraphs.md
   (2013 re-release images, not the original book), strings.md, tilesets.md, allpics.md,
   sprites.md, cursors.md, font.md, title.md, ending.md, exe.md (WL.EXE table offsets).
   Codec facts: rotating XOR key = xor1^xor2, per byte decoded = enc^key, checksum -= decoded,
   key += 0x1F (mod 256); prefix mode stops when the running checksum equals xor1|(xor2<<8).
   Huffman: MSB-first bitstream, serialized tree (1 = leaf + 8-bit symbol; 0 = node, left,
   one ignored separator bit, right), decode to an externally supplied size. Vertical XOR after
   Huffman for tiles (8-byte stride) and portraits (48-byte stride). Tiles 16x16 at 4 bpp
   (128 bytes). Portraits 96x84 at 4 bpp plus an animation block of (delay, index) pairs
   ended by 0xFF, timing (delay+1)*54.925 ms. GAME1: 20 maps, 1 savegame, 3 shop lists;
   GAME2: 22 maps, 1 savegame, 1 shop list; blocks start "msq0"/"msq1"; offsets come from
   tables in WL.EXE (map offsets 0x18C9A, tile-map offsets 0x18D42, sizes 0x18F3C, location
   mapping 0x18EE9, shop offsets 0x18E40, skill metadata 0x18A40 with 36 entries).
   Savegame: 0x800 decoded bytes, four 14-byte party-group records, seven 0x100-byte
   characters (name 14, six attributes, money 3, gender, nationality, AC, HP, equipment,
   experience 3, level, 25-byte rank string, 30 skill slots, 30 item slots). Shop list: 766
   bytes, 94 records of 8. String control bytes 0x0D, 0x06, 0x0B name, 0x0F number, 0x0A
   plural, 0x0C gender, 0x0E pronoun, 0x10/0x11 choice lists.
2. Wasteland Suite (same author), Java converters, http://kayahr.github.io/wlandsuite/ (v1.3.2,
   2026-03-30); wlsuite (C, archived 2012); wludata (C, archived 2012).
3. badvassal/wllib (Go, MIT, 2020) and wlmanip: a second independent MSQ implementation to
   cross-check.
4. "Wasteland: The Definitive Deconstruction" (Fandom): pages MSQ_Block, Encryption_Decryption,
   Huffman_Coding, Pics, Tiles, END.CPA, GameX, Character_Data, Files, NLocation, Misc; organised
   per file and per WL.EXE segment. Unread by machine; the first manual read to do.
5. ModdingWiki file inventory: https://moddingwiki.shikadi.net/wiki/Wasteland (transtbl format
   unknown; wla.bin x86 graphics code; wl.exe EXEPACK).

## Tier 2: reimplementations
6. WERK (C++/OpenGL, NMA thread 194424), status unknown, no repo found.
7. Wasteland Ranger HQ file room lists Revival of the Wasteland (Java), Newcomer (C64),
   Wasteland Zero, Multiplayer Wasteland: none verified, none on GitHub.
8. inXile's DOSBox fork for the Original Classic: github.com/dosbox-tools/dosbox-wasteland.

## Tier 3: rules
9. Nearly Ultimate Wasteland Guide (Fandom), Wasteland Archive combat pages: unread.
10. CRPG Addict, Game 65 (2011): ranged combat simultaneous, melee by speed, Brawling levels
    add attacks; no to-hit formula documented anywhere readable.
11. Apple II mirror (asimov): four 140 KB game disks, wastdocs.txt (69.75 KB), wastpgrf.txt
    (64.92 KB), 1996 FAQs, walkthrough. Not opened. Disk 1 is copy-protected (applefritter
    thread 2024–2025: nibble copy or WOZ via Applesauce; ADTPro failed on side 1).

## Tier 4: legal and platform
12. inXile (Microsoft since 2018) holds the rights; "Wasteland 1 – The Original Classic" on
    Steam/GOG ($5.99); Wasteland Remastered (2020, Unity) is a different codebase.
13. Clean-room precedents: ScummVM, OpenMW ("You must legally own Morrowind"), OpenXcom:
    engine open, no assets, user supplies data files.
14. Internet Archive DOS copy exists; rights unclear; never a fixture in a public repo.

## Judgement
Container and codec level: well specified for DOS (wastelib, cross-checked by wllib). Map
action semantics, NPC/monster/string sections, scripts, combat and skill formulas: not in any
readable public source; they live in WL.EXE and in the Deconstruction wiki's segment notes.
Apple II: effectively undocumented at byte level.

## Three unknowns
1. Map action semantics and the in-EXE game logic. 2. Apple II data and code. 3. Combat, skill
and item mechanics (no authoritative formula source; parity needs disassembly and differential
testing against an emulator; no corpus exists).
