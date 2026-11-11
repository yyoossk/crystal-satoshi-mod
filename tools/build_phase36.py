#!/usr/bin/env python3
"""Phase 36: Routes 16, 17, 18, 19 and 21 as in Red / the Pikachu full-color hack:
 * Route 16 (Snorlax: the Poké Flute wakes it as on Route 12; the fly house: HM02), the Cycling Road (Route 17:
   always on the bicycle, downhill as in Crystal), Route 18, the sea routes 19 and 21 (Red's trainers, items, hidden
   items, signs, wild Pokémon).  Joined to Celadon / Fuchsia (Crystal's: Fuchsia's south side is walled, so Route 19's
   path leads through Crystal's Fuchsia gate), Route 20, Cinnabar Island and Pallet Town (Red's).
 * Red's gate buildings of Routes 16 and 18 (new maps): the guard stops the player without a bicycle; upstairs the
   binoculars and (Route 18) the Slowbro <-> Lickitung trade.
 * Red: on the Cycling Road side of the gates the player is always on the bicycle.
usage: build_phase36.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import redmap as RM
import redtexts as RT
from evedit import MapEvents
import build_phase17 as P17
import build_phase19 as P19
import build_phase25 as P25
import build_phase27 as P27
import build_phase28 as P28
import build_phase34 as P34
import build_phase35 as P35
import routekit as RK

FIRST_FLAG = 396                   # 334-395: phase 35
FIRST_MAP = 111                    # 26:104-110 = phase 35
TBANK, BANK, DBANK = 0x64, 0x5B, 0x67      # tilesets / events + attributes / blocks
GATE_TS, HOUSE_TS = 47, 44
SPR = dict(P35.SPR); SPR.update({'SPRITE_SWIMMER': 0x31, 'SPRITE_BIRD': 0x4E})
SPR_SWIMMER_GIRL = 0x32
ROUTES = ['Route16', 'Route17', 'Route18', 'Route19', 'Route21']
RED_ID = {'Route16': 0x1B, 'Route17': 0x1C, 'Route18': 0x1D, 'Route19': 0x1E, 'Route21': 0x20}
NEW = ['Route16Gate1F', 'Route16Gate2F', 'Route16FlyHouse', 'Route18Gate1F', 'Route18Gate2F']
NEW_RED = {'Route16Gate1F': 0xBA, 'Route16Gate2F': 0xBB, 'Route16FlyHouse': 0xBC, 'Route18Gate1F': 0xBE,
           'Route18Gate2F': 0xBF}
NEW_ROUTE = {n: 'Route' + n[5:7] for n in NEW}
CONST = {'ROUTE_16_GATE_1F': 'Route16Gate1F', 'ROUTE_16_GATE_2F': 'Route16Gate2F', 'ROUTE_16_FLY_HOUSE': 'Route16FlyHouse',
         'ROUTE_18_GATE_1F': 'Route18Gate1F', 'ROUTE_18_GATE_2F': 'Route18Gate2F'}
SNORLAX, SLOWBRO, LICKITUNG, TENTACOOL = 143, 80, 108, 72
BICYCLE, HM02 = 0x07, 0xF4
SFX_POKEFLUTE = 0x26
VAR_X, VAR_Y = 0x12, 0x13
ENGINE_ALWAYS_ON_BIKE = 0x19       # (from Crystal's Route 16 callback)
MAPCALLBACK_NEWMAP = 5
BG_UP = 1
KANTO_WATER = {'Route19': 0x2BD4D, 'Route21': 0x2BD5F}
# where the gate guards stop a player without a bicycle (Red), first one = next to the counter
GATE_STOP = {'Route16Gate1F': [(4, 7), (4, 8), (4, 9), (4, 10)], 'Route18Gate1F': [(4, 3), (4, 4), (4, 5), (4, 6)]}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (TBANK, BANK, DBANK, 0x3F):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    snorlax_gone = FL.new(); snorlax_had = FL.new(); got_hm02 = FL.new()
    nid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(NEW)}
    P35_FLUTE = P35.POKE_FLUTE

    # ================= Red's trade: Slowbro -> Lickitung (after phases 19, 27 and 35)
    ref = P19.NPC_TRADES_REF; assert rom[ref] == 0x21
    to = fo(0x3F, r16(ref + 1)); nt = 7 + len(P19.RED_TRADES) + 2
    table = bytearray(rom[to:to + 16 * nt])
    nick = bytes(RT.R[0x7206B + 3:0x7206B + 7])
    table += bytes([0, SLOWBRO, LICKITUNG]) + nick + bytes([0x96, 0x66, 0x00]) + (31415 + 1111 * nt).to_bytes(2, 'little') + \
        encode('ゴロウ')[:3] + b'\x00'
    trade_marc = nt
    w16(ref + 1, sp.put(0x3F, bytes(table)))

    # ================= tilesets
    mps = {}
    for rn in ROUTES:
        w, h = RK.red_dims(rn); mps[rn] = MapPort(rn, K.ow, w, h, rn + '.blk'); K.dims[rn] = (w, h)
    ov = {rn: RK.warp_overrides(K.ow, mps[rn], P25.red_objects(rn)[1]) for rn in ROUTES}
    # Route 19's two-way path north ends at Crystal's Fuchsia gate (Crystal's Fuchsia is walled there)
    m19 = mps['Route19']
    edge19 = [x for x in range(2 * m19.w) if K.ow.quad_tile(*m19.block_at(x, 0)) in K.ow.passable
              and K.ow.quad_tile(*m19.block_at(x, 1)) in K.ow.passable]
    assert edge19 == [13], edge19
    ov['Route19'][(13, 0)] = COLL_CARPET['up']
    K.overworld_variants(mps, ov)
    gts = Tileset('Gate', 12, 'gate.bst', SC + '/out/pk_gate.pkl')
    hts = Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl')
    nmp = {}
    for n in NEW:
        w, h = RK.red_dims(n); nmp[n] = MapPort(n, hts if 'House' in n else gts, w, h, n + '.blk')
    for ts, tid in ((gts, GATE_TS), (hts, HOUSE_TS)):
        mm = {n: nmp[n] for n in NEW if nmp[n].ts is ts}
        K.ts_variants(tid, ts, mm, {n: {(x, y): P25.warp_override(ts, nmp[n], x, y) for x, y, d, wi in P25.red_objects(n)[1]}
                                    for n in mm})
    K.bank = BANK
    K.add_parties(ROUTES)
    K.alloc_headers(FIRST_MAP, len(NEW))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end36'); a.end()
    dex = P27.W_DEX_CAUGHT + (SNORLAX - 1) // 8
    a.label('cbit'); a.raw(bytes([0xFA, dex & 0xFF, dex >> 8, 0xE6, 1 << ((SNORLAX - 1) % 8),
                                   0xEA, P27.W_SCRIPT_VAR & 0xFF, P27.W_SCRIPT_VAR >> 8, 0xC9]))
    def callasm_label(l_): a.db(0x0E, BANK); a.dw(l_)
    snor_idx = [i for i, o in enumerate(P25.red_objects('Route16')[0]) if o['sprite'] == 'SPRITE_SNORLAX'][0]
    def snorlax(a, texts, lab, o):
        texts.update(sx_sleep=K.rt(0x1B, 7), sx_wake=K.rt(0x1B, 10), sx_calm=K.rt(0x1B, 11),
                     sx_play=b'\x00' + encode('<PLAYER>は<LINE><POKEMON>のふえを　ふいてみた！@').rstrip(b'\x50') + b'\x57')
        a.label(lab); a.opentext(); a.checkitem(P35_FLUTE); a.iffalse(lab + 'n')
        a.writetext('sx_play'); a.playsound(SFX_POKEFLUTE); a.waitsfx(); a.promptbutton()
        a.writetext('sx_wake'); a.waitbutton(); a.closetext()
        callasm_label('cbit'); a.iffalse(lab + 'c0'); a.setevent(snorlax_had); a.sjump(lab + 'c1')
        a.label(lab + 'c0'); a.clearevent(snorlax_had)
        a.label(lab + 'c1'); a.loadwildmon(SNORLAX, 30); a.startbattle(); a.reloadmapafterbattle()
        a.disappear(snor_idx + 2); a.setevent(snorlax_gone)
        a.checkevent(snorlax_had); a.iftrue(lab + 'cm'); callasm_label('cbit'); a.iftrue('end36')
        a.label(lab + 'cm'); a.opentext(); a.writetext('sx_calm'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'n'); a.writetext('sx_sleep'); a.waitbutton(); a.closetext(); a.end()
        return SPR['SPRITE_SNORLAX'], 0x90, snorlax_gone, 0       # PAL_NPC_BLUE
    built = {}
    for rn in ROUTES:
        ob, bgs = K.red_events(a, texts, rn, RED_ID[rn], rn[5:] + '_', {snor_idx + 1: snorlax} if rn == 'Route16' else {}, SPR)
        objs = P25.red_objects(rn)[0]; assert len(ob) == len(objs)
        for o, b_ in zip(objs, ob):
            if o['sprite'] == 'SPRITE_SWIMMER' and o['extra'] and o['extra'][0] == 'OPP_BEAUTY': b_[0] = SPR_SWIMMER_GIRL
        built[rn] = (ob, bgs)

    def obj(o, lab, fl=0xFFFF):
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        return [SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, fl]
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    def jt(lab, b, p): a.label(lab); a.jumptext(T(lab + 't', b, p)); return lab
    def jtf(lab, b, p): a.label(lab); a.jumptextfaceplayer(T(lab + 't', b, p)); return lab
    nbuilt = {}
    # the gates' ground floors: the guard (with / without a bicycle) and the stop
    for n, g, yes, no, wait in (('Route16Gate1F', 0xBA, 0x6D5B, 0x6D2E, K.rt(0xBA, 3)),
                                ('Route18Gate1F', 0xBE, 0x6FD8, 0x6FB8, K.rt(0xBE, 2))):
        objs = P25.red_objects(n)[0]; L_ = n + '_'
        T(L_ + 'y', 0x12, yes); T(L_ + 'n', 0x12, no); texts[L_ + 'w'] = wait
        a.label(L_ + 'g'); a.faceplayer(); a.opentext(); a.checkitem(BICYCLE); a.iffalse(L_ + 'gn')
        a.writetext(L_ + 'y'); a.waitbutton(); a.closetext(); a.end()
        a.label(L_ + 'gn'); a.writetext(L_ + 'n'); a.waitbutton(); a.closetext(); a.end()
        coords = []
        for k, (x, y) in enumerate(GATE_STOP[n]):
            c_ = '%sc%d' % (L_, k); coords.append((0xFF, y, x, c_))
            a.label(c_); a.checkitem(BICYCLE); a.iftrue('end36')
            a.opentext(); a.writetext(L_ + 'w'); a.waitbutton(); a.closetext()
            if k: a.applymovement(0, c_ + 'm')
            a.sjump(L_ + 'stop')
            if k: a.label(c_ + 'm'); a.db(*([0x0D] * k), 0x47)                     # step up
        a.label(L_ + 'stop'); a.opentext(); a.writetext(L_ + 'n'); a.waitbutton(); a.closetext()
        a.applymovement(0, L_ + 'r'); a.end()
        a.label(L_ + 'r'); a.db(0x0F, 0x47)                                            # step right
        ob = [obj(objs[0], L_ + 'g')]
        if n == 'Route16Gate1F': ob.append(obj(objs[1], jtf(L_ + 'gb', *RM.text_ptr(0xBA, 2))))
        nbuilt[n] = (ob, [], coords)
    # Route 16 gate 2F
    objs = P25.red_objects('Route16Gate2F')[0]
    nbuilt['Route16Gate2F'] = ([obj(objs[0], jtf('g16b', 0x12, 0x6E42)), obj(objs[1], jtf('g16g', 0x12, 0x6E68))],
                               [(2, 1, BG_UP, jt('g16l', 0x12, 0x6E86)), (2, 6, BG_UP, jt('g16r', 0x12, 0x6EAD))], [])
    # Route 18 gate 2F
    objs = P25.red_objects('Route18Gate2F')[0]
    a.label('g18y'); a.faceplayer(); a.opentext(); a.db(0x95, trade_marc); a.waitbutton(); a.closetext(); a.end()
    nbuilt['Route18Gate2F'] = ([obj(objs[0], 'g18y')],
                               [(2, 1, BG_UP, jt('g18l', 0x12, 0x7061)), (2, 6, BG_UP, jt('g18r', 0x12, 0x7089))], [])
    # the fly house: HM02
    objs = P25.red_objects('Route16FlyHouse')[0]
    T('fh_g', 7, 0x7335); T('fh_x', 7, 0x738B); T('fh_f', 7, 0x73BF); T('fh_b', 7, 0x73E0)
    a.label('fh'); a.faceplayer(); a.opentext(); a.checkevent(got_hm02); a.iftrue('fh_e')
    a.writetext('fh_g'); a.verbosegiveitem(HM02, 1); a.iffalse('fh_n'); a.setevent(got_hm02)
    a.label('fh_e'); a.writetext('fh_x'); a.waitbutton(); a.closetext(); a.end()
    a.label('fh_n'); a.writetext('fh_f'); a.waitbutton(); a.closetext(); a.end()
    a.label('fhb'); a.faceplayer(); a.opentext(); a.writetext('fh_b'); a.cry(PM.MON['FEAROW']); a.waitbutton()
    a.closetext(); a.end()
    nbuilt['Route16FlyHouse'] = ([obj(objs[0], 'fh'), obj(objs[1], 'fhb')], [], [])
    K.put_texts(a, texts); texts = {}

    # ================= warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    rw = {}
    for rn in ROUTES:
        rw[rn] = [W(x, y, wi, nid[CONST[d]]) for x, y, d, wi in P25.red_objects(rn)[1]]
    fgate = mapid('Route19FuchsiaGate')
    r19_edge = len(rw['Route19']) + 1; rw['Route19'].append(W(13, 0, 3, fgate))
    nw = {}
    for n in NEW:
        rn = NEW_ROUTE[n]
        nw[n] = [W(x, y, wi, mapid(rn) if d == 'LAST_MAP' else nid[CONST[d]]) for x, y, d, wi in P25.red_objects(n)[1]]
    # callbacks: Route 16 / 18: always on the bicycle on the Cycling Road side (Red: from the gates' west doors);
    # Route 17: Crystal's (always on the bicycle, downhill); Route 19: Crystal's rocks are not there
    a.label('cb16'); a.db(0x1C, VAR_Y); a.db(0x0B, 8); a.dw('cbwalk'); a.db(0x1C, VAR_X); a.db(0x0A, 17); a.dw('cbwalk')
    a.label('cbbike'); a.setflag(ENGINE_ALWAYS_ON_BIKE); a.endcallback()
    a.label('cbwalk'); a.db(0x35); a.dw(ENGINE_ALWAYS_ON_BIKE); a.endcallback()                        # clearflag
    a.label('cb18'); a.db(0x1C, VAR_X); a.db(0x0A, 33); a.dw('cbwalk'); a.sjump('cbbike')
    cbs = {'Route16': [(MAPCALLBACK_NEWMAP, 'cb16')], 'Route18': [(MAPCALLBACK_NEWMAP, 'cb18')], 'Route19': [], 'Route21': []}
    me17 = MapEvents(rom, 'Route17'); assert [t_ for t_, r in me17.callbacks] == [MAPCALLBACK_NEWMAP]
    a.label('cb17'); a.farsjump(me17.callbacks[0][1][1], me17.callbacks[0][1][2]); cbs['Route17'] = [(MAPCALLBACK_NEWMAP, 'cb17')]
    for rn in ROUTES:
        ob, bgs = built[rn]
        K.emit(a, rn, rw[rn], [], bgs, ob, cbs[rn])
    for n in NEW:
        ob, bgs, coords = nbuilt[n]
        K.emit(a, n, nw[n], coords, bgs, ob, [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('routes / gates: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    hsrc = {n: 'Route15FuchsiaGate' for n in NEW}; hsrc['Route16FlyHouse'] = 'Route16FuchsiaSpeechHouse'
    for i, n in enumerate(NEW):
        house = 'House' in n
        K.make_map(FIRST_MAP + i, nmp[n], HOUSE_TS if house else GATE_TS, border_of(n), hsrc[n], 3 if house else 6, a, n)
        hh = GROUP26_END + 9 * (FIRST_MAP + i - G26_COUNT - 1)
        rom[hh + 5] = rom[hdr_index(NEW_ROUTE[n]) + 5]                                        # landmark: the route's

    # ================= attributes + connections
    rg = {rn: K.red_walk(mps[rn]) for rn in ROUTES}
    RED_TOWNS = ('CinnabarIsland', 'PalletTown', 'Route20')            # Red's already: Red's offsets
    # Crystal's Fuchsia: Route 19's path north must meet a wall (its edge warp); Route 18's road meets Fuchsia's
    # only west opening (rows 19-21) at -6
    FIXED = {('Route19', 'FuchsiaCity'): -5, ('Route18', 'FuchsiaCity'): -6}
    fg_ = K.walk_grid('FuchsiaCity')
    assert not fg_[-1][13 + 10] and not fg_[-2][13 + 10]
    assert all(fg_[y + 12][x] for y in (8, 9) for x in range(3))
    def off(rn, d, nb_, red_off):
        if nb_ in ROUTES or nb_ in RED_TOWNS: return red_off
        if (rn, nb_) in FIXED: return FIXED[(rn, nb_)]
        o_ = K.best_offset(d, rg[rn], K.walk_grid(nb_), red_off, depth=True)
        log.append('%s %s %s: offset %d (Red %d)' % (rn, d, nb_, o_, red_off)); return o_
    conns = {rn: [(d, nb_, off(rn, d, nb_, o_)) for d, nb_, o_ in RK.red_conns(rn)] for rn in ROUTES}
    for rn in ROUTES:
        mp = mps[rn]
        K.new_attrs(rn, mp.w, mp.h, border_of(rn), a.labels[rn + 'ms'], a.labels[rn + 'ev'], conns[rn])
        rom[hdr_index(rn) + 1] = RK.OVERWORLD_TS
    opp = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
    for rn in ROUTES:
        for d, nb_, o_ in conns[rn]:
            if nb_ not in ROUTES: K.set_conn(nb_, opp[d], rn, -o_)
    for rn in ROUTES: K.place_blocks(rn, mps[rn].blk, True)
    for nb_ in ('CeladonCity', 'FuchsiaCity'):
        K.place_blocks(nb_, K.crystal_blocks(nb_), False)
    for nb_ in RED_TOWNS:
        K.place_blocks(nb_, K.crystal_blocks(nb_), True)                # (Gen I blocks: Red's maps)

    # ================= warps back
    r19 = mapid('Route19')
    assert K.fix_warps('Route19FuchsiaGate', lambda i, w_: (r19_edge, r19) if (w_[3], w_[4]) == r19 else None) == 2

    # ================= wild Pokémon (grass: Red's; the sea: Red's Tentacool, as phase 22 did for Route 20)
    for rn in ROUTES:
        if os.path.exists(PR + '/data/wild/maps/%s.asm' % rn): K.red_wild(mapid(rn), rn)
    for rn, o in KANTO_WATER.items():
        assert rom[o:o + 2] == bytes(mapid(rn)), rn
        rom[o + 2:o + 9] = bytes([5, 5, TENTACOOL, 15, TENTACOOL, 30, TENTACOOL])

    P17.fix_outdoor_sprites(rom, log)
    P35.add_outdoor_sprite(rom, 'Route16', SPR['SPRITE_SNORLAX'], log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
