#!/usr/bin/env python3
"""Phase 21: Red's Seafoam Islands (1F-B4F, ported from the Pikachu full-color hack) before the Kanto Hall of Fame.
Strength boulders, Articuno (Lv 50), Red's wild Pokémon.  Route 20's cave leads there before the Hall of Fame and to
Crystal's Seafoam Gym afterwards.  The currents of B3F/B4F (and the boulders dropped through the holes) are not
reproduced: the water can be surfed freely.
Also: Chris's back pic moves out of bank 0A to make room in the Kanto grass wild table.
usage: build_phase21.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import pkmap
import portmaps as PM
import build_phase10 as P10
import build_phase12 as P12
import build_phase15 as P15

FIRST_FLAG = 125
FIRST_MAP = 63                     # 26:62 = Power Plant (phase 20)
CAVERN_TS = 37
MAPS = [('SeafoamIslands1F', 0xC0), ('SeafoamIslandsB1F', 0x9F), ('SeafoamIslandsB2F', 0xA0),
        ('SeafoamIslandsB3F', 0xA1), ('SeafoamIslandsB4F', 0xA2)]
CONST = {'SEAFOAM_ISLANDS_1F': 'SeafoamIslands1F', 'SEAFOAM_ISLANDS_B1F': 'SeafoamIslandsB1F',
         'SEAFOAM_ISLANDS_B2F': 'SeafoamIslandsB2F', 'SEAFOAM_ISLANDS_B3F': 'SeafoamIslandsB3F',
         'SEAFOAM_ISLANDS_B4F': 'SeafoamIslandsB4F'}
SPR_BOULDER, SPR_BIRD, MV_BOULDER, STD_BOULDER = 0x5A, 0x4E, 0x19, 0x0E
CHRIS_BACKPIC = (0x2BA3D, 0x2BBCD)
CHRIS_REFS = [(0x3FC39, 0x3FC3B), (0x8883D, 0x8883A)]      # (bank byte, address)
WATER = 0x14
MON = PM.MON


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x60, 0x63, 0x75, 0x78, 0x79):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)

    # ================= Chris's back pic -> bank 60
    lo_, hi_ = CHRIS_BACKPIC
    for bb, aa in CHRIS_REFS:
        assert rom[bb] == 0x0A and r16(aa) == 0x4000 + lo_ % 0x4000, hex(bb)
    na = sp.put(0x60, bytes(rom[lo_:hi_]))
    for bb, aa in CHRIS_REFS:
        rom[bb] = 0x60; w16(aa, na)
    rom[lo_:hi_] = bytes(hi_ - lo_)
    log.append('Chris back pic moved to 60:%04X' % na)

    # ================= cavern water (Seafoam), collision
    TS = PM.Tilesets(rom, sp)
    cav = Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl')
    co = TS.coll_off(CAVERN_TS)
    coll = {'Cavern': bytearray(rom[co:co + 4 * cav.nblocks])}
    for b in range(cav.nblocks):
        for q in range(4):
            if cav.quad_tile(b, q) == WATER: coll['Cavern'][4 * b + q] = COLL_WATER
    maps = {}
    for n, g in MAPS:
        h = pkmap.header(g); maps[n] = MapPort(n, cav, h['w'], h['h'], n + '.blk')
    for n, mp in maps.items():                         # same rule as Mt. Moon (phase 15): ladders are staircases
        objs, warps, skip, bgl = PM.objects_of(n)
        for (x, y, dest, wid) in warps:
            b_, q = mp.block_at(x, y); tile = cav.quad_tile(b_, q)
            if tile == WATER: continue                 # B3F<->B4F current warps: left inert (water collision)
            if tile in cav.warp_tiles: v = COLL_STAIRCASE
            elif y == mp.h * 2 - 1 or y == 0 or x == 0 or x == mp.w * 2 - 1:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            else: raise AssertionError((n, x, y, hex(tile)))
            old = coll['Cavern'][4 * b_ + q]
            assert old in (COLL_FLOOR, COLL_WALL, v), (n, x, y, hex(old), hex(v))
            coll['Cavern'][4 * b_ + q] = v
    rom[co:co + len(coll['Cavern'])] = coll['Cavern']

    # ================= headers 26:63-67
    u = US.get(); G = u.groups()
    lo, hi = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1), GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1 + len(MAPS))
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                rom[hdr] = 0x79; w16(hdr + 3, sp.put(0x79, bytes(rom[ao:ao + size])))
    rom[lo:hi] = bytes(hi - lo)
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g) in enumerate(MAPS)}

    r20 = mapid('Route20'); gym = mapid('SeafoamGym')
    ra = attrs(rom, hdr_index('Route20')); rev = parse_events(rom, ra['scbank'], ra['events'])
    door = [i for i, (o_, w) in enumerate(rev['warps']) if (w[3], w[4]) == gym][0]
    hc = hdr_index('SeafoamGym')

    for n, g in MAPS:
        mp = maps[n]
        objs, warps, skip, bgl = PM.objects_of(n)
        a = Asm(sp.here(0x63)); obj_bytes = []
        for idx, o in enumerate(objs):
            lab = 'o%d' % (idx + 1)
            if o['sprite'] == 'SPRITE_BOULDER':
                if o['face'] != 'BOULDER_MOVEMENT_BYTE_2': continue    # boulders that fell from above: not used
                a.label(lab); a.jumpstd(STD_BOULDER)
                obj_bytes.append([SPR_BOULDER, o['y'] + 4, o['x'] + 4, MV_BOULDER, 0, 0xFF, 0xFF, 0, 0, lab, 0xFFFF])
            elif o['sprite'] == 'SPRITE_BIRD':
                fl = FL.new(); oid = len(obj_bytes) + 2
                a.label(lab); a.faceplayer(); a.opentext(); a.writetext('art'); a.cry(MON['ARTICUNO']); a.waitbutton(); a.closetext()
                a.loadwildmon(MON['ARTICUNO'], int(o['extra'][1])); a.startbattle(); a.disappear(oid); a.reloadmapafterbattle(); a.end()
                a.label('art'); a.raw(P12.text(encode('{00}ギャーオ！')))
                obj_bytes.append([SPR_BIRD, o['y'] + 4, o['x'] + 4, P12.FACE['DOWN'], 0, 0xFF, 0xFF, 0, 0, lab, fl])
        a.label('mapscripts'); a.db(0, 0)
        a.label('events'); a.db(0, 0)
        a.db(len(warps))
        for x, y, dest, wid in warps:
            if dest == 'LAST_MAP': a.db(y, x, door + 1, *r20)
            else: a.db(y, x, wid, *mapids[CONST[dest]])
        a.db(0, 0)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(0x63, blob) == base
        blkp = sp.put(0x60, mp.blk)
        aa = sp.put(0x60, bytes([border_of(n), mp.h, mp.w, 0x60, blkp & 0xFF, blkp >> 8, 0x63, a.labels['mapscripts'] & 0xFF,
                                 a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0]))
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        rom[hh:hh + 9] = bytes([0x60, CAVERN_TS, 4, aa & 0xFF, aa >> 8, rom[hc + 5], rom[hc + 6], 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts 63:%04X (%d bytes)' % (n, *mapids[n], base, len(blob)))

    # ================= Route 20's cave: Red's Seafoam Islands before the Hall of Fame
    o_, w = rev['warps'][door]
    fix = {door: bytes(w)}
    rom[o_ + 2] = 1; rom[o_ + 3], rom[o_ + 4] = mapids['SeafoamIslands1F']
    P15.install_hof_switch(rom, sp, 'Route20', fix, log)

    # ================= wild Pokémon (Red) -> Kanto grass table
    p = P15.KANTO_GRASS
    while rom[p] != 0xFF: p += 47
    ent = b''
    for n, g in MAPS:
        t = open(PR + '/data/wild/maps/%s.asm' % n, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        assert len(slots) == 10, n
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        ent += bytes([*mapids[n], rate, rate, rate]) + bytes(sum(([lv, MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
    assert not any(rom[p + 1:p + 1 + len(ent)])
    rom[p:p + len(ent) + 1] = ent + b'\xff'
    log.append('Seafoam Islands wild data (%d bytes)' % len(ent))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
