#!/usr/bin/env python3
"""Phase 110: the 2026-11-16 reports (Kanto: as in Red full color).
 * Kanto's Marts sell what Red's sell, in Red's order (Indigo Plateau stays Crystal's): Pewter's and Cerulean's lists
   were still Crystal's, Cinnabar's clerk used Saffron's list (Red's Cinnabar also has Ultra Balls).  Pewter = mart 19,
   Cerulean = 20 (lists replaced); Cinnabar gets mart 25 (Crystal's Celadon 3F TM list: Crystal's Celadon Dept. Store
   maps are not reachable in this MOD, Red's store is used) and its clerk's pokemart id 30 -> 25.
 * Walking with a poisoned Pokémon: Crystal turns the whole background one flat purple for 4 frames (looked like the
   map vanishing).  As in Red (ChangeBGPalColor0_4Frames: BG white -> dark gray for 4 frames; Red full color shows
   each palette's 3rd color): LoadPoisonBGPals' CGB loop (32:7C9D) now copies each BG palette's color 2 into its
   color 0 (routine in bank 32's free space).
 * No phone call from Bill when a caught Pokémon fills the box: PokeBallEffect's .SendToPC (03:6E08) no longer sets
   BATTLERESULT_BOX_FULL (the only thing that bit does is start Script_SpecialBillCall after the battle).
 * The player turned into the follower Pokémon (A held on turbo while walking in grass / battling): Crystal's
   follower movement queue (wFollowMovementQueue $D4C4, 5 bytes; length $D4C3) has no bound check; with the follower
   kept from moving while the player's steps were queued, the queue ran past its 5 bytes into the player's object
   struct ($D4C9: map object index, sprite tile, movement) and the player was drawn with the follower's tiles.
   The append (01:54D7) now drops a step when the queue is full (code at 01:7EE0, a free gap).
 * Red's warps that are entered by stepping onto them but were made carpet-down ($70: only pressing down while standing
   on them warps; the cell below is a wall, so it looked like they did nothing): the Celadon Mansion's back stairs,
   the stairs down to the Underground Path, the S.S. Anne's cabin doors / gangway, the Rocket Hideout's elevator
   doors.  Every Red-map warp at $70 that is not on the bottom edge and has a wall below becomes $73 (as the S.S.
   Anne's stairs, phase 106): stepping on it warps at once, as in Red; arriving on it does not.
 * Riding the bike the player looked like the rival: phase 71 took the Red full-color hack's sprite-table entry 2
   for the bike sprite, which is its rival's sprite.  Red's bike sprite (RedBikeSprite, akafc $05:$4000, 24 tiles in
   Crystal's walking-sprite layout) now goes where phase 71 put the bike gfx.
 * Trainer names: the Kanto trainers added from Red got names round-robin from one pool, so sailors, hikers and
   the like could be called ユミ and lasses タカシ.  Every name from that pool is given again by the class's sex
   (Red's female classes: LASS, JR_TRAINER_F, COOLTRAINER_F, BEAUTY, PICNICKER).
 * NPC sprites that did not match Red's (the same kind of person drawn two ways): the hikers on Routes 9, 10 and 25
   were the fishing guru (the other hikers are POKEFAN_M), Vermilion Gym's super nerd was a rocker, Fuchsia Gym's
   jugglers (Red: ROCKER) were super nerds / gentlemen, the Game Corner's gentleman was the fishing guru, Celadon Gym's
   cool trainers (Red: COOLTRAINER_F) were lasses, Route 20's beauties / jr. trainers (♀) were male swimmers while
   Route 19's are swimmer girls.
usage: build_phase110.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play'))
from lib import *
from portlib import *
import portmaps as PM
import build_phase15 as P15

MART_TABLE = 0x164C3                   # Crystal's Marts pointer table (bank 5; mart ids of JP Crystal)
RED_MARTS = {19: ('POKE_BALL', 'POTION', 'ESCAPE_ROPE', 'ANTIDOTE', 'BURN_HEAL', 'AWAKENING', 'PARLYZ_HEAL'),    # Pewter
             20: ('POKE_BALL', 'POTION', 'REPEL', 'ANTIDOTE', 'BURN_HEAL', 'AWAKENING', 'PARLYZ_HEAL'),          # Cerulean
             25: ('ULTRA_BALL', 'GREAT_BALL', 'HYPER_POTION', 'MAX_REPEL', 'ESCAPE_ROPE', 'FULL_HEAL', 'REVIVE')}  # Cinnabar
CINNABAR_MART, MART_SAFFRON, MART_CINNABAR = (26, 52), 30, 25


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    f, n = bank_free_tail(rom, 0x05); sp.set_area(0x05, f + 1, 0x05 * 0x4000 + 0x4000)
    log = []

    # ================= Marts
    from mapdb import DB
    db = DB(src_rom)
    for mid, goods in RED_MARTS.items():
        lst = [PM.item_id(n) for n in goods]
        w16(MART_TABLE + 2 * mid, sp.put(0x05, bytes([len(lst)] + lst + [0xFF])))
    m = db.maps[CINNABAR_MART]; hits = 0
    for o in db.objs(CINNABAR_MART):
        p = o[9] | o[10] << 8
        if p < 0x4000: continue
        s = fo(m['scbank'], p)
        i = bytes(rom[s:s + 12]).find(bytes([0x93, 0x00, MART_SAFFRON, 0x00]))
        if i >= 0: rom[s + i + 2] = MART_CINNABAR; hits += 1
    assert hits == 1, hits
    log.append('marts: Pewter, Cerulean, Cinnabar as in Red')

    # ================= no Bill call when the box fills
    o = 0xEE08
    assert rom[o:o + 9] == bytes.fromhex('fe 1e 20 05 21 ae d0 cb fe'), rom[o:o + 9].hex()
    rom[o + 7:o + 9] = b'\x00\x00'
    log.append('box full: no call from Bill')

    # ================= follower movement queue: bounded
    o = 0x54D7
    old = bytes.fromhex('f5 21 c3 d4 34 5e 16 00 21 c4 d4 19 f1 77 c9')
    assert rom[o:o + 15] == old, rom[o:o + 15].hex()
    NQ = 0x7EE0
    code = bytes.fromhex('f5 21 c3 d4 7e 3c fe 05 30 07 77 c6 c4 6f f1 77 c9 f1 c9')
    assert rom[NQ - 8:NQ + 0x20] == bytes(0x28) and rom[0x7ED7] == 0xC9
    rom[NQ:NQ + len(code)] = code
    rom[o:o + 15] = bytes([0xC3, NQ & 0xFF, NQ >> 8]) + bytes(12)
    log.append('follower queue: bounded (01:%04X)' % NQ)

    # ================= step-on warps (Red)
    from bot import grid_of, WALK
    STAIRS = []
    for k in sorted(db.maps):
        if k[0] != 26 or k[1] < 21: continue
        G = grid_of(rom, db.maps[k]['hdr'])
        for w in db.warps(k):
            x, y = w[0], w[1]
            if y < len(G) - 1 and x < len(G[0]) and G[y][x] == 0x70 and G[y + 1][x] not in WALK:
                STAIRS.append((k, (x, y)))
    TSO = PM.Tilesets(rom, Space(rom))
    def cell(k, x, y):
        mm = db.maps[k]; aa = attrs(rom, mm['hdr']); b2 = aa['blkbank'] * 0x4000 + aa['blk'] - 0x4000
        return rom[b2 + (y // 2) * aa['w'] + x // 2], (y % 2) * 2 + x % 2, rom[mm['hdr'] + 1]
    targets = set()
    for k, (x, y) in STAIRS:
        assert (x, y) in [(w[0], w[1]) for w in db.warps(k)]
        targets.add(cell(k, x, y))
    conflicts = []
    for blk, q, ts in sorted(targets):                 # every use of these block quadrants is a warp
        bad = []
        for k2, m2 in db.maps.items():
            if rom[m2['hdr'] + 1] != ts: continue
            a2 = attrs(rom, m2['hdr']); b3 = a2['blkbank'] * 0x4000 + a2['blk'] - 0x4000
            ws = {(w[0], w[1]) for w in db.warps(k2)}
            for i in range(a2['w'] * a2['h']):
                if rom[b3 + i] == blk:
                    xx, yy = (i % a2['w']) * 2 + q % 2, (i // a2['w']) * 2 + q // 2
                    if (xx, yy) not in ws: bad.append((k2, xx, yy))
        if bad: conflicts.append((ts, blk, q, bad[:4])); continue
        c = TSO.coll_off(ts) + 4 * blk + q
        assert rom[c] == 0x70, hex(rom[c])
        rom[c] = 0x73
        log.append('step-on warp: tileset %d block %02X quadrant %d -> $73' % (ts, blk, q))
    for c_ in conflicts: log.append('step-on warp NOT changed (block also used off warps): %s' % (c_,))

    # ================= bike sprite: Red's
    import build_phase71 as P71
    aka = open(P71.AKAFC, 'rb').read()
    t = fo(*P71.SPRITE_TABLE)
    bo = fo(rom[t + 9], rom[t + 6] | rom[t + 7] << 8)
    assert rom[t + 8] == 0xC0
    bike = aka[0x14000:0x14180]
    assert aka[0x14180:0x141A0] == aka[0x14180:0x141A0] and bike != rom[bo:bo + 0x180]
    rom[bo:bo + 0x180] = bike
    log.append('bike sprite: Red full color RedBikeSprite -> %X:%04X' % (rom[t + 9], rom[t + 6] | rom[t + 7] << 8))

    # ================= trainer names by the class's sex
    import build_phase13 as P13
    from jpchar import encode
    FEMALE_CLS = ('LASS', 'JR_TRAINER_F', 'COOLTRAINER_F', 'BEAUTY', 'PICNICKER')
    MALE_NAMES = PM.NAMEPOOL[:10] + ['ツヨシ', 'ヒデキ', 'マサル', 'ケンジ', 'トオル', 'シンジ']
    FEMALE_NAMES = PM.NAMEPOOL[10:] + ['ハルカ', 'ミホ', 'ユカ', 'アキコ', 'リサ', 'マイ', 'チカ', 'ノリコ', 'カオリ', 'メグミ']
    pool = {bytes(encode(n + '@')) for n in PM.NAMEPOOL}
    fem_ids = {PM.TCLS[c] for c in FEMALE_CLS}
    groups = P13.read_groups7e(rom); nm = nf = 0; ch = 0
    for i, grp in enumerate(groups):
        for e in grp:
            if bytes(e[0]) not in pool: continue
            if i + 1 in fem_ids: new = FEMALE_NAMES[nf % len(FEMALE_NAMES)]; nf += 1
            else: new = MALE_NAMES[nm % len(MALE_NAMES)]; nm += 1
            nb = bytes(encode(new + '@'))
            if nb != bytes(e[0]): ch += 1
            e[0] = nb
    log.append('trainer names by sex: %d changed (bank 7E free %d)' % (ch, P13.write_groups7e(rom, groups)))

    # ================= NPC sprites as in Red
    from lib import mapid
    SPRFIX = [((7, 13), 0x3B, 0x2D), ((7, 14), 0x3B, 0x2D), ((7, 16), 0x3B, 0x2D),            # Routes 9, 10, 25
              ((17, 8), 0x2B, 0x2C), ((17, 8), 0x40, 0x2C), ((21, 21), 0x28, 0x24)]           # Fuchsia, Celadon Gym
    SPRPOS = [((12, 11), (3, 8), 0x2C, 0x2B), ((21, 19), (17, 13), 0x3B, 0x40)]            # Vermilion Gym, Game Corner
    SPRPOS += [((6, 6), xy, 0x31, 0x32) for xy in ((68, 11), (45, 10), (55, 14), (25, 7), (24, 12), (15, 8))]   # Route 20's beauties / jr. trainers ♀: swimmer girl, as on Route 19
    nfix = 0
    for name, old, new in SPRFIX:
        for off, ob in db.maps[name]['ev']['objs']:
            if rom[off] == old: rom[off] = new; nfix += 1
    for name, (x, y), old, new in SPRPOS:
        hit = [off for off, ob in db.maps[name]['ev']['objs'] if (ob[2] - 4, ob[1] - 4) == (x, y)]
        assert len(hit) == 1 and rom[hit[0]] == old, (name, hit)
        rom[hit[0]] = new; nfix += 1
    log.append('NPC sprites as in Red: %d objects' % nfix)

    # ================= poison step flash (Red's)
    PB = 0x32; o = fo(PB, 0x7C9D)
    old = bytes.fromhex('21 80 d0 0e 20 3e bc 22 3e 7e 22 0d 20 f7')
    assert rom[o:o + len(old)] == old, rom[o:o + 14].hex()
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 1, PB * 0x4000 + 0x4000)
    code = bytes.fromhex('21 80 d0 0e 08'                       # ld hl, wBGPals2 / ld c, 8
                         '23 23 23 23 2a 46'                    # hl+4: a, b = color 2
                         '11 fb ff 19 22 70'                    # hl-5 -> color 0 = a, b
                         '11 07 00 19 0d 20 ed c9')             # next palette
    assert code[-3] == 0x20 and (code[-2] - 0x100) == 5 - (len(code) - 1)
    ad = sp.put(PB, code)
    rom[o:o + len(old)] = bytes([0xCD, ad & 0xFF, ad >> 8]) + bytes(len(old) - 3)
    log.append('poison step: Red\'s flash (routine %X:%04X)' % (PB, ad))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
