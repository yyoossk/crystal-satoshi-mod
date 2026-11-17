#!/usr/bin/env python3
"""Phase 112: Kanto gyms as in Red.
 * Fuchsia Gym: Koga stood where Crystal's Janine stands (1,10); Red's Koga is at (4,10), facing down (phase 55 put
   his object at Janine's place).
 * Pewter, Cerulean, Vermilion, Celadon and Fuchsia Gyms: Red's rooms (Red's blocks with the Red gym tileset of
   phase 44's Fighting Dojo, Red's sizes and borders) in place of Crystal's; the people, the doors, the statues stand
   where Red has them (Crystal's post-game people keep their places).  Vermilion's door block (phase 75 / 108) is
   Red's ($24 closed, $05 open).
 * The gym tileset's colors as in Red full color (dumps of its gyms and Dojo): the statues' tiles $22 $23 $32 $33
   use palette 0 (gray), not 5 (gold); palette 7 is Red full color's.
 * Cut in the gym tileset as in Red (Celadon Gym's small trees, tile $50): their quadrants are cut trees, and the
   Cut table gets Red's swaps for it ($3C/$3F -> $35, $3D -> $36).
usage: build_phase112.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play'))
from lib import *
from portlib import *
import portmaps as PM
import pairwalls
import routekit as RK
import build_phase25 as P25
import build_phase12 as P12
from evedit import MapEvents

FUCHSIA_GYM = (17, 8)
SPR_KOGA = 0x21
FACILITY_TS = 34                 # Red's FACILITY (Saffron Gym's tileset in Red)
DOJO_TS = 52                     # phase 44: Red's gym tileset (Red's DOJO and GYM share blocks, graphics, collision)
DATA_BANK = 0xA0
# Crystal's objects (event order) -> Red's place and facing; None: keep (Crystal's post-game people)
OBJS = {
    'PewterGym': [(4, 1, 'DOWN'), (3, 6, 'RIGHT'), (7, 10, 'DOWN')],
    'CeruleanGym': [None, (4, 2, 'DOWN'), (2, 3, 'RIGHT'), (8, 7, 'LEFT'), None, (7, 10, 'DOWN')],
    'VermilionGym': [(5, 1, 'DOWN'), (9, 6, 'LEFT'), (3, 8, 'LEFT'), (0, 10, 'RIGHT'), (4, 14, 'DOWN')],
    'CeladonGym': [(4, 3, 'DOWN'), (2, 11, 'RIGHT'), (7, 10, 'LEFT'), (9, 5, 'DOWN'), (1, 5, 'DOWN'), (6, 3, 'DOWN'),
                   (3, 3, 'DOWN'), (5, 3, 'DOWN')],
    'FuchsiaGym': [None, (8, 13, 'DOWN'), (7, 8, 'RIGHT'), (1, 12, 'DOWN'), (3, 5, 'UP'), (7, 15, 'DOWN'), (8, 2, 'DOWN'),
                   (2, 7, 'LEFT'), (4, 10, 'DOWN')],
    'SaffronGym': [(9, 8, 'DOWN'), (10, 1, 'DOWN'), (17, 1, 'DOWN'), (3, 7, 'DOWN'), (17, 7, 'DOWN'), (10, 15, 'DOWN'),
                   (3, 13, 'DOWN'), (17, 13, 'DOWN'), (3, 1, 'DOWN')],
    # Crystal's Blue (after the Kanto Hall of Fame) stands where Giovanni stood
    'ViridianGym': [(2, 1, 'DOWN'), (16, 15, 'DOWN'), (12, 7, 'DOWN'), (11, 11, 'UP'), (10, 7, 'DOWN'), (3, 7, 'LEFT'),
                    (13, 5, 'RIGHT'), (10, 1, 'DOWN'), (2, 16, 'RIGHT'), (6, 5, 'DOWN'), (2, 1, 'DOWN')],
}
STATUES = {'PewterGym': [(3, 10), (6, 10)], 'CeruleanGym': [(3, 11), (6, 11)], 'VermilionGym': [(3, 14), (6, 14)],
           'CeladonGym': [(3, 15), (6, 15)], 'FuchsiaGym': [(3, 15), (6, 15)], 'SaffronGym': [(9, 15)],
           'ViridianGym': [(15, 15), (18, 15)]}
FIRST_FLAG = 533
CUT_LD_HL = 0xC7E1                 # 03:47E1  ld hl, CutTreeBlockPointers (phase 27 moved the table)
COLL_CUT_TREE = 0x12
OVERWORLD_TS = 40
L_PLACE = (0xC862, 0xC8A4)          # phase 27's lists (03:4862-48A3)
T_PLACE = (0xFFE2, 0xFFF6)          # phase 27's table (03:7FE2-7FF4) and the byte after it                   # 532: phase 88
FACE = {'DOWN': 6, 'UP': 7, 'LEFT': 8, 'RIGHT': 9}
VERMILION_DOOR = {0x40: 0x24, 0x01: 0x05}        # phase 108's door / floor block -> Red's


def viridian(rom, sp, mp, log):
    """Red's Viridian Gym (10x9, spinner arrows) on Crystal's map: the events rewritten in DATA_BANK"""
    me = MapEvents(rom, 'ViridianGym')
    red_w = P25.red_objects('ViridianGym')[1]
    assert len(me.warps) == len(red_w)
    me.warps = [bytes([y, x]) + w[2:] for w, (x, y, d, wi) in zip(me.warps, red_w)]
    assert len(me.objs) == len(OBJS['ViridianGym'])
    for ob, (x, y, fc) in zip(me.objs, OBJS['ViridianGym']):
        ob[0][1] = y + 4; ob[0][2] = x + 4; ob[0][3] = FACE[fc]
    sts = [i for i, b_ in enumerate(me.bgs) if b_[2] == 0]; assert len(sts) == 2
    for i, (x, y) in zip(sts, STATUES['ViridianGym']):
        y0, x0, t_, r_ = me.bgs[i]; me.bgs[i] = (y, x, t_, r_)
    a = Asm(sp.here(DATA_BANK)); a.bank = DATA_BANK
    # Red's spinner arrows (as phase 12 ported the Rocket Hideout's): coord events moving the player
    for i, (x, y, mvl) in enumerate(P12.spinner_table('ViridianGym')):
        L = 'sp%d' % i
        a.label(L); a.applymovement(0, L + 'm'); a.end()
        a.label(L + 'm')
        for d, c in mvl: a.db(*([0x18 + d] * c))
        a.db(0x47)
        me.coords.append((0xFF, y, x, L))
    # Red's Revive (item ball)
    FL = PM.Flags(FIRST_FLAG)
    me.add_object(PM.SPR['SPRITE_POKE_BALL'], 16, 9, 6, ('data', bytes([PM.item_id('REVIVE'), 1])), flag=FL.new(),
                  pal_type=0x01)
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(DATA_BANK, blob) == base
    me.install(a)
    log.append('ViridianGym: Red\'s room %dx%d, %d spinner arrows, Revive, events %X:%04X (%d bytes)'
               % (mp.w, mp.h, len(P12.spinner_table('ViridianGym')), DATA_BANK, base, len(blob)))


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    from mapdb import DB
    db = DB(src_rom)
    log = []
    hit = [off for off, ob in db.maps[FUCHSIA_GYM]['ev']['objs'] if ob[0] == SPR_KOGA]
    assert len(hit) == 1, hit
    o = hit[0]
    assert (rom[o + 2] - 4, rom[o + 1] - 4) == (1, 10), (rom[o + 2], rom[o + 1])
    rom[o + 2] = 4 + 4; rom[o + 3] = 0x06            # x = 4, STANDING_DOWN
    log.append('Fuchsia Gym: Koga -> (4,10) facing down')

    # ================= Red's gym rooms
    sp = Space(rom)
    f, n = bank_free_tail(rom, DATA_BANK); sp.set_area(DATA_BANK, f + 1 if f > DATA_BANK * 0x4000 else f, DATA_BANK * 0x4000 + 0x4000)
    TS = PM.Tilesets(rom, sp)
    dts = Tileset('Dojo', 5, 'gym.bst', SC + '/out/pk_dojo.pkl')
    def ovr(ts, mp, n): return {(x, y): P25.warp_override(ts, mp, x, y) for x, y, d, wi in P25.red_objects(n)[1]}
    dw, dh = RK.red_dims('FightingDojo'); dojo = MapPort('FightingDojo', dts, dw, dh, 'FightingDojo.blk')
    meta0, coll0, _ = pairwalls.variants(dts, bytes(dts.blocks), bytes(dts.coll), {'FightingDojo': dojo}, [],
                                         {'FightingDojo': ovr(dts, dojo, 'FightingDojo')})
    nb0 = len(coll0) // 4
    e = TS.entry(DOJO_TS)
    mo, co = fo(e[3], e[4] | e[5] << 8), fo(e[6], e[7] | e[8] << 8)
    assert bytes(rom[mo:mo + 16 * nb0]) == meta0, 'tileset 52 is not phase 44\'s'
    meta, coll = bytes(rom[mo:mo + 16 * nb0]), bytes(rom[co:co + 4 * nb0])      # (later phases' collision changes kept)
    gyms = {}
    for g in OBJS:
        if g == 'SaffronGym': continue
        w_, h_ = RK.red_dims(g); gyms[g] = MapPort(g, dts, w_, h_, g + '.blk')
    meta2, coll2, blks = pairwalls.variants(dts, meta, coll, gyms, [], {g: ovr(dts, gyms[g], g) for g in gyms})
    coll2 = bytearray(coll2); ncut = 0
    for b_ in range(len(coll2) // 4):
        for q, (r_, c_) in enumerate(((1, 0), (1, 2), (3, 0), (3, 2))):
            if meta2[16 * b_ + 4 * r_ + c_] == 0x50 and coll2[4 * b_ + q] == 0x07: coll2[4 * b_ + q] = COLL_CUT_TREE; ncut += 1
    coll2 = bytes(coll2)
    log.append('tileset %d: %d cut-tree quadrants' % (DOJO_TS, ncut))
    # Saffron Gym: Red's FACILITY tileset (ours: 34, with variants of earlier phases: its block count = the highest
    # block any of its maps uses + 1)
    fts = Tileset('Facility', 22, 'facility.bst', SC + '/out/pk_facility.pkl')
    nf = 0
    for k_, m_ in db.maps.items():
        if rom[m_['hdr'] + 1] != FACILITY_TS: continue
        a2 = attrs(rom, m_['hdr']); b3 = a2['blkbank'] * 0x4000 + a2['blk'] - 0x4000
        nf = max(nf, max(rom[b3:b3 + a2['w'] * a2['h']]) + 1)
    ef = TS.entry(FACILITY_TS); mf, cf = fo(ef[3], ef[4] | ef[5] << 8), fo(ef[6], ef[7] | ef[8] << 8)
    w_, h_ = RK.red_dims('SaffronGym'); sg = MapPort('SaffronGym', fts, w_, h_, 'SaffronGym.blk')
    assert max(sg.blk) < fts.nblocks
    fmeta, fcoll, fb = pairwalls.variants(fts, bytes(rom[mf:mf + 16 * nf]), bytes(rom[cf:cf + 4 * nf]), {'SaffronGym': sg}, [],
                                          {'SaffronGym': ovr(fts, sg, 'SaffronGym')})
    gyms['SaffronGym'] = sg; blks['SaffronGym'] = fb['SaffronGym']
    a_fm = sp.put(DATA_BANK, fmeta); a_fc = sp.put(DATA_BANK, fcoll)
    t = TS.tab + 15 * FACILITY_TS
    rom[t + 3:t + 9] = bytes([DATA_BANK, a_fm & 0xFF, a_fm >> 8, DATA_BANK, a_fc & 0xFF, a_fc >> 8])
    log.append('tileset %d: %d -> %d blocks (Saffron Gym) at %X:%04X' % (FACILITY_TS, nf, len(fcoll) // 4, DATA_BANK, a_fm))
    a_m = sp.put(DATA_BANK, meta2); a_c = sp.put(DATA_BANK, coll2)
    t = TS.tab + 15 * DOJO_TS
    rom[t + 3:t + 9] = bytes([DATA_BANK, a_m & 0xFF, a_m >> 8, DATA_BANK, a_c & 0xFF, a_c >> 8])
    log.append('tileset %d: %d -> %d blocks (gym variants) at %X:%04X' % (DOJO_TS, nb0, len(coll2) // 4, DATA_BANK, a_m))
    for g, mp in gyms.items():
        k = mapid(g); h = hdr_index(g); a_ = attrs(rom, h); ao = a_['attr_off']
        bp = sp.put(DATA_BANK, blks[g])
        rom[h + 1] = FACILITY_TS if g == 'SaffronGym' else DOJO_TS
        rom[ao] = border_of(g); rom[ao + 1] = mp.h; rom[ao + 2] = mp.w
        rom[ao + 3] = DATA_BANK; rom[ao + 4] = bp & 0xFF; rom[ao + 5] = bp >> 8
        if g == 'ViridianGym': viridian(rom, sp, mp, log); continue
        ev = db.maps[k]['ev']
        red_w = P25.red_objects(g)[1]
        assert len(ev['warps']) == len(red_w), (g, len(ev['warps']), len(red_w))
        for j, ((off, wb), (x, y, d, wi)) in enumerate(zip(ev['warps'], red_w)):
            rom[off] = y; rom[off + 1] = x
            if d == 'SAFFRON_GYM': rom[off + 2] = wi; rom[off + 3:off + 5] = bytes(k)      # Red's pads
        objs = ev['objs']; assert len(objs) == len(OBJS[g]), (g, len(objs))
        for (off, ob), to in zip(objs, OBJS[g]):
            if to is None: continue
            x, y, fc = to
            rom[off + 1] = y + 4; rom[off + 2] = x + 4; rom[off + 3] = FACE[fc]
        sts = [(off, b_) for off, b_ in ev['bgs'] if b_[2] == 0 and not (g == 'VermilionGym' and b_[0] in (7, 9, 11))]
        assert len(sts) == len(STATUES[g]), (g, sts)
        for (off, b_), (x, y) in zip(sts, STATUES[g]):
            rom[off] = y; rom[off + 1] = x
        log.append('%s: Red\'s room %dx%d (blocks %X:%04X), %d warps, people, statues as in Red' % (g, mp.w, mp.h, DATA_BANK, bp, len(red_w)))
    # Cut: the gym tileset uses the Gen I overworld tileset's list (Red's CutTreeBlockSwaps, which begins with the gym's
    # $3C/$3F -> $35, $3D -> $36).  Bank 3 is full: the table and lists are rearranged in their two places
    # (03:4862-48A3, phase 27's lists; 03:7FE2-7FF5, its table)
    tp = rom[CUT_LD_HL + 1] | rom[CUT_LD_HL + 2] << 8; to_ = fo(0x03, tp); assert to_ == T_PLACE[0], hex(to_)
    tab = []
    while rom[to_] != 0xFF: tab.append((rom[to_], rom[to_ + 1] | rom[to_ + 2] << 8)); to_ += 3
    lists = {}
    for t_, p_ in tab:
        o_ = fo(0x03, p_); e_ = rom.index(0xFF, o_); lists[t_] = bytes(rom[o_:e_ + 1])
    ow = OVERWORLD_TS; assert lists[ow][:9] == bytes([0x3C, 0x35, 0, 0x3F, 0x35, 0, 0x3D, 0x36, 0])
    kanto = lists[3]; assert lists[ow].endswith(kanto)
    def a3(o): return 0x4000 + o % 0x4000
    region = L_PLACE[0]; ptr = {}
    body = bytearray()
    tab_at = region; body += bytes(3 * (len(tab) + 1) + 1)            # the table first (filled below)
    for t_ in [t for t, p in tab if t not in (1, 3, ow)]:
        ptr[t_] = a3(region + len(body)); body += lists[t_]
    ptr[ow] = a3(region + len(body)); ptr[3] = ptr[ow] + len(lists[ow]) - len(kanto); body += lists[ow]
    ptr[DOJO_TS] = ptr[ow]
    assert len(body) <= L_PLACE[1] - L_PLACE[0], len(body)
    second = bytes(lists[1]); assert len(second) <= T_PLACE[1] - T_PLACE[0]
    ptr[1] = a3(T_PLACE[0])
    newtab = b''.join(bytes([t_, ptr[t_] & 0xFF, ptr[t_] >> 8]) for t_ in [t for t, p in tab] + [DOJO_TS]) + b'\xff'
    body[0:len(newtab)] = newtab
    rom[L_PLACE[0]:L_PLACE[1]] = bytes(body) + bytes(L_PLACE[1] - L_PLACE[0] - len(body))
    rom[T_PLACE[0]:T_PLACE[1]] = second + bytes(T_PLACE[1] - T_PLACE[0] - len(second))
    rom[CUT_LD_HL + 1] = a3(tab_at) & 0xFF; rom[CUT_LD_HL + 2] = a3(tab_at) >> 8
    log.append('Cut: tileset %d uses the Gen I overworld list (table 03:%04X)' % (DOJO_TS, a3(tab_at)))

    # colors as in Red full color
    pm = fo(0x13, e[13] | e[14] << 8)
    for t_ in (0x22, 0x23, 0x32, 0x33):
        i = pm + t_ // 2; sh = 4 * (t_ & 1)
        rom[i] = rom[i] & ~(7 << sh) & 0xFF
    RED_PAL7 = bytes.fromhex('ff7f7f2a5e190000')
    ph = [o_ for o_ in range(0x6A * 0x4000, 0x6B * 0x4000 - 3) if rom[o_] == DOJO_TS and 0x40 <= rom[o_ + 2] < 0x80
          and rom[fo(0x6A, rom[o_ + 1] | rom[o_ + 2] << 8):][:8] == bytes.fromhex('9e6b734ead35e71c')]
    assert len(ph) == 1, ph
    pp = fo(0x6A, rom[ph[0] + 1] | rom[ph[0] + 2] << 8); rom[pp + 56:pp + 64] = RED_PAL7
    log.append('tileset %d: statues palette 0, palette 7 as Red full color' % DOJO_TS)

    # Vermilion: phase 75's changeblock 4,4 (door / floor; its scripts are in bank 63) with Red's blocks
    lo_ = 0x63 * 0x4000
    d = [lo_ + i for i in range(0x4000 - 4) if rom[lo_ + i:lo_ + i + 4] == bytes([0x79, 4, 4, 0x40])]
    assert len(d) == 1, d
    fl = [lo_ + i for i in range(0x4000 - 5) if rom[lo_ + i:lo_ + i + 5] == bytes([0x79, 4, 4, 0x01, 0x7B])
          and abs(lo_ + i - d[0]) < 0x200]
    assert len(fl) == 1, fl
    rom[d[0] + 3] = VERMILION_DOOR[0x40]; rom[fl[0] + 3] = VERMILION_DOOR[0x01]
    log.append('VermilionGym: changeblock 4,4: door $40 -> $24, floor $01 -> $05')

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
