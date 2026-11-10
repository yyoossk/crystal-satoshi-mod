#!/usr/bin/env python3
"""Phase 20: Red's Power Plant (ported from the Pikachu full-color hack) before the Kanto Hall of Fame.
Voltorb / Electrode disguised as items, Zapdos (Lv 50), items, Red's wild Pokémon.  Route 10's power plant door
leads there before the Hall of Fame, to Crystal's Power Plant afterwards.
usage: build_phase20.py IN.gbc OUT.gbc OUT.ips
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

FIRST_FLAG = 109
MAP_ID = 62                        # 26:52-61 = Cinnabar (phase 19)
FACILITY_TS = 34
SPR_BALL, SPR_BIRD = 0x54, 0x4E
MON = PM.MON


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x60, 0x63, 0x78, 0x79):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    n, g = 'PowerPlant', 0x53

    # ================= map + collision (Facility tileset, shared)
    TS = PM.Tilesets(rom, sp)
    fac = Tileset('Facility', 22, 'facility.bst', SC + '/out/pk_facility.pkl')
    coll = {'Facility': bytearray(rom[TS.coll_off(FACILITY_TS):TS.coll_off(FACILITY_TS) + 4 * fac.nblocks])}
    h = pkmap.header(g); mp = MapPort(n, fac, h['w'], h['h'], n + '.blk')
    PM.warp_collisions({n: mp}, lambda m: PM.objects_of(m)[:3], log, coll)
    co = TS.coll_off(FACILITY_TS); rom[co:co + len(coll['Facility'])] = coll['Facility']

    # ================= header slot 26:62
    u = US.get(); G = u.groups()
    lo, hi = GROUP26_END + 9 * (MAP_ID - G26_COUNT - 1), GROUP26_END + 9 * (MAP_ID - G26_COUNT)
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else MAP_ID - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                rom[hdr] = 0x79; w16(hdr + 3, sp.put(0x79, bytes(rom[ao:ao + size])))
    rom[lo:hi] = bytes(hi - lo)
    me_id = (G26, MAP_ID)

    # Route 10's door to the power plant
    r10 = mapid('Route10North'); cpp = mapid('PowerPlant')
    ra = attrs(rom, hdr_index('Route10North')); rev = parse_events(rom, ra['scbank'], ra['events'])
    door = [i for i, (o_, w) in enumerate(rev['warps']) if (w[3], w[4]) == cpp][0]

    # ================= scripts / events
    objs, warps, skip, bgl = PM.objects_of(n)
    a = Asm(sp.here(0x63)); texts = {}; obj_bytes = []; bgs = []
    battle = encode('{00}ビリビリッ！')
    for idx, o in enumerate(objs):
        tid = idx + 1; lab = 'o%d' % tid; oid = tid + 1
        if o['sprite'] == 'SPRITE_POKE_BALL' and o['extra'][0] in ('VOLTORB', 'ELECTRODE'):
            fl = FL.new(); sp_ = MON[o['extra'][0]]; lv = int(o['extra'][1])
            a.label(lab); a.opentext(); a.writetext('zap'); a.cry(sp_); a.waitbutton(); a.closetext()
            a.loadwildmon(sp_, lv); a.startbattle(); a.disappear(oid); a.reloadmapafterbattle(); a.end()
            obj_bytes.append([SPR_BALL, o['y'] + 4, o['x'] + 4, 6, 0, 0xFF, 0xFF, 0, 0, lab, fl])
        elif o['sprite'] == 'SPRITE_BIRD':
            fl = FL.new()
            a.label(lab); a.faceplayer(); a.opentext(); a.writetext('zd'); a.cry(MON['ZAPDOS']); a.waitbutton(); a.closetext()
            a.loadwildmon(MON['ZAPDOS'], int(o['extra'][1])); a.startbattle(); a.disappear(oid); a.reloadmapafterbattle(); a.end()
            obj_bytes.append([SPR_BIRD, o['y'] + 4, o['x'] + 4, P12.FACE['UP'], 0, 0xFF, 0xFF, 0, 0, lab, fl])
        else:
            fl = FL.new(); a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
            obj_bytes.append([SPR_BALL, o['y'] + 4, o['x'] + 4, 6, 0, 0xFF, 0xFF, 1, 0, lab, fl])
    texts['zap'] = battle
    texts['zd'] = encode('{00}ギャーオ！')
    for k, (x, y, fn, arg) in enumerate(PM.hidden_events(PM.map_const(n))):
        if fn == 'HiddenItems':
            L = 'hi%d' % k; a.label(L); a.dw(FL.new()); a.db(PM.item_id(arg)); bgs.append((y, x, 7, L))
    for k_, v in texts.items():
        a.label(k_); a.raw(P12.text(v))
    a.label('mapscripts'); a.db(0, 0)
    a.label('events'); a.db(0, 0)
    a.db(len(warps))
    for x, y, dest, wid in warps:
        a.db(y, x, door + 1, *r10)
    a.db(0)
    a.db(len(bgs))
    for (y, x, f_, l_) in bgs: a.db(y, x, f_); a.dw(l_)
    a.db(len(obj_bytes))
    for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
    base = a.base; blob = a.done(); assert sp.put(0x63, blob) == base
    blkp = sp.put(0x60, mp.blk)
    aa = sp.put(0x60, bytes([border_of(n), mp.h, mp.w, 0x60, blkp & 0xFF, blkp >> 8, 0x63, a.labels['mapscripts'] & 0xFF,
                             a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0]))
    hc = hdr_index('PowerPlant')
    hh = GROUP26_END + 9 * (MAP_ID - G26_COUNT - 1)
    rom[hh:hh + 9] = bytes([0x60, FACILITY_TS, 4, aa & 0xFF, aa >> 8, rom[hc + 5], rom[hc + 6], 0x01, 0x00])
    log.append('PowerPlant -> map %d:%d  scripts 63:%04X (%d bytes)' % (*me_id, base, len(blob)))

    # ================= Route 10 door: Red's power plant before the Hall of Fame
    o_, w = rev['warps'][door]
    fix = {door: bytes(w)}
    rom[o_ + 2] = 1; rom[o_ + 3], rom[o_ + 4] = me_id
    P15.install_hof_switch(rom, sp, 'Route10North', fix, log)

    # ================= wild Pokémon (Red) -> Kanto grass table
    p = P15.KANTO_GRASS
    while rom[p] != 0xFF: p += 47
    t = open(PR + '/data/wild/maps/PowerPlant.asm', encoding='utf-8').read()
    t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
    rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
    slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
    assert len(slots) == 10
    pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
    ent = bytes([*me_id, rate, rate, rate]) + bytes(sum(([lv, MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
    assert not any(rom[p + 1:p + 1 + len(ent)])
    rom[p:p + len(ent) + 1] = ent + b'\xff'
    log.append('Power Plant wild data (%d bytes)' % len(ent))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
