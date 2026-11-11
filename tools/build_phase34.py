#!/usr/bin/env python3
"""Phase 34: Routes 5, 6, 7 and 8 as in Red / the Pikachu full-color hack, with Red's Saffron gates:
 * Red's four routes (trainers, signs, wild Pokémon), joined to Cerulean (Red), Saffron, Vermilion, Celadon, Lavender
   (Crystal's for now: joined at the matching roads).
 * Red's gate buildings on Routes 5-8 (new maps): the thirsty guard turns the player back until he is given a drink
   (Fresh Water, Soda Pop or Lemonade, the first one in the bag; one drink for all four gates).  While Saffron City is
   still Crystal's, the gates' Saffron-side doors lead through Saffron's own gate doors.
 * Route 5: Crystal's Underground Path entrance and the house (Crystal's) behind Red's doors; Route 6: the Underground
   Path entrance.  (Routes 7 / 8: Red's west-east Underground Path is not there yet.)
usage: build_phase34.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import redmap as RM
from evedit import MapEvents
import build_phase17 as P17
import build_phase25 as P25
import build_phase28 as P28
import build_phase30 as P30
import routekit as RK

FIRST_FLAG = 318                   # 279-317: phase 33
FIRST_MAP = 100                    # 26:99 = phase 32
BANK, DBANK = 0x72, 0x70            # (their free tails)
GATE_TS = 47
SPR = dict(P30.SPR); SPR.update({'SPRITE_GUARD': 0x43, 'SPRITE_GAMBLER': 0x2D, 'SPRITE_SUPER_NERD': P25.SPR['SPRITE_SUPER_NERD']})
ROUTES = ['Route5', 'Route6', 'Route7', 'Route8']
RED_ID = {'Route5': 0x10, 'Route6': 0x11, 'Route7': 0x12, 'Route8': 0x13}
GATES = ['Route5Gate', 'Route6Gate', 'Route7Gate', 'Route8Gate']
GATE_RED = {'Route5Gate': 0x46, 'Route6Gate': 0x49, 'Route7Gate': 0x4C, 'Route8Gate': 0x4F}
# Red: where the guard stops the player, which way he is sent back
GATE_STOP = {'Route5Gate': ([(3, 3), (4, 3)], 0x0D), 'Route6Gate': ([(3, 2), (4, 2)], 0x0C),
             'Route7Gate': ([(3, 3), (3, 4)], 0x0E), 'Route8Gate': ([(2, 3), (2, 4)], 0x0F)}
# Crystal's Saffron gate maps (their Saffron doors now lead into Red's gates)
CR_GATE = {'Route5Gate': 'Route5SaffronGate', 'Route6Gate': 'Route6SaffronGate', 'Route7Gate': 'Route7SaffronGate',
           'Route8Gate': 'Route8SaffronGate'}
# Red gate warp indices (1-based) on the Saffron side
SAFFRON_SIDE = {'Route5Gate': (1, 2), 'Route6Gate': (3, 4), 'Route7Gate': (3, 4), 'Route8Gate': (1, 2)}
DRINKS = ('FRESH_WATER', 'SODA_POP', 'LEMONADE')
UNDERGROUND_FIRST_MAP = 139         # phase 43: 26:139-142 = Red's Underground Path entrances on Routes 5-8


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    for b in (BANK, DBANK):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, BANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    gave_drink = FL.new()
    gid = {g: (G26, FIRST_MAP + i) for i, g in enumerate(GATES)}
    saf = mapid('SaffronCity')

    # ================= tilesets
    mps = {}
    for rn in ROUTES:
        w, h = RK.red_dims(rn); mps[rn] = MapPort(rn, K.ow, w, h, rn + '.blk'); K.dims[rn] = (w, h)
    ov = {rn: RK.warp_overrides(K.ow, mps[rn], P25.red_objects(rn)[1]) for rn in ROUTES}
    K.overworld_variants(mps, ov)
    gts = Tileset('Gate', 12, 'gate.bst', SC + '/out/pk_gate.pkl')
    gmp = {}
    for g in GATES:
        w, h = RK.red_dims(g); gmp[g] = MapPort(g, gts, w, h, g + '.blk')
    gov = {g: {(x, y): P25.warp_override(gts, gmp[g], x, y) for x, y, d, wi in P25.red_objects(g)[1]} for g in GATES}
    K.ts_variants(GATE_TS, gts, gmp, gov)
    K.add_parties(ROUTES)
    K.alloc_headers(FIRST_MAP, len(GATES))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    built = {rn: K.red_events(a, texts, rn, RED_ID[rn], rn[5:] + '_', {}, SPR) for rn in ROUTES}
    # the guards
    t_thirsty = K.rt(0x46, 2); t_give = K.rt(0x46, 3); t_thanks = RM.crystal_text(7, 0x6C90)
    texts.update(g_th=t_thirsty, g_gv=t_give, g_ty=t_thanks)
    gbuilt = {}
    for g in GATES:
        objs, warps, bgl = P25.red_objects(g)
        pts, back = GATE_STOP[g]; lab = g + '_'
        # talk: thirsty / given a drink / thanks
        a.label(lab + 't'); a.faceplayer(); a.opentext(); a.checkevent(gave_drink); a.iftrue('g_thx')
        a.sjump(lab + 'chk')
        a.label(lab + 'c'); a.checkevent(gave_drink); a.iftrue('g_end'); a.opentext()
        a.label(lab + 'chk')
        for k, dname in enumerate(DRINKS):
            a.checkitem(PM.item_id(dname)); a.iftrue('%sd%d' % (lab, k))
        a.writetext('g_th'); a.waitbutton(); a.closetext(); a.applymovement(0, lab + 'mv'); a.end()
        for k, dname in enumerate(DRINKS):
            a.label('%sd%d' % (lab, k)); a.db(0x20, PM.item_id(dname), 1); a.sjump('g_give')            # takeitem
        a.label(lab + 'mv'); a.db(back, 0x47)
        ob = [[SPR['SPRITE_GUARD'], objs[0]['y'] + 4, objs[0]['x'] + 4, P25.face((0, 0, 0, 'STAY', objs[0]['face']))[0], 0,
               0xFF, 0xFF, 0, 0, lab + 't', 0xFFFF]]
        gbuilt[g] = (ob, [(0xFF, y, x, lab + 'c') for x, y in pts])
    a.label('g_give'); a.writetext('g_gv'); a.waitbutton(); a.closetext(); a.setevent(gave_drink); a.end()
    a.label('g_thx'); a.writetext('g_ty'); a.waitbutton(); a.closetext()
    a.label('g_end'); a.end()
    K.put_texts(a, texts)

    # warps of the routes (Red's order)
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    rw = {}
    for rn in ROUTES:
        rw[rn] = []
        for x, y, d, wi in P25.red_objects(rn)[1]:
            if d.endswith('_GATE'): gname = 'Route%sGate' % rn[5:]; rw[rn].append(W(x, y, wi, gid[gname]))
            elif d.startswith('UNDERGROUND_PATH_ROUTE_'):            # Red's entrances (phase 43's maps)
                rw[rn].append(W(x, y, wi, (G26, UNDERGROUND_FIRST_MAP + int(d[-1]) - 5)))
            elif d == 'DAYCARE': rw[rn].append(W(x, y, 1, mapid('Route5CleanseTagHouse')))
            else: raise KeyError(d)
    # (the missing ones are the last ones: left out)
    for rn in ROUTES:
        assert all(w_ is None for w_ in rw[rn][[i for i, x in enumerate(rw[rn]) if x is None][0]:]) if None in rw[rn] else True
        rw[rn] = [w_ for w_ in rw[rn] if w_]
    sw = K.warps_of('SaffronCity')
    def saffron_idx(cr): return [i + 1 for i, w_ in enumerate(sw) if (w_[3], w_[4]) == mapid(cr)]
    gw = {}
    for g in GATES:
        rn = 'Route' + g[5]
        gw[g] = []
        sidx = saffron_idx(CR_GATE[g])
        for i, (x, y, d, wi) in enumerate(P25.red_objects(g)[1]):
            if i + 1 in SAFFRON_SIDE[g]: gw[g].append(W(x, y, sidx[min(SAFFRON_SIDE[g].index(i + 1), len(sidx) - 1)], saf))
            else: gw[g].append(W(x, y, wi, mapid(rn)))
    for rn in ROUTES:
        ob, bgs = built[rn]
        cbs = []
        for t_, r in MapEvents(rom, rn).callbacks:
            L_ = rn + 'cb%d' % t_; a.label(L_); a.farsjump(r[1], r[2]); cbs.append((t_, L_))
        K.emit(a, rn, rw[rn], [], bgs, ob, cbs)
    for g in GATES:
        ob, coords = gbuilt[g]
        K.emit(a, g, gw[g], coords, [], ob, [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('routes / gates: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    for i, g in enumerate(GATES):
        K.make_map(FIRST_MAP + i, gmp[g], GATE_TS, border_of(g), CR_GATE[g], 6, a, g)

    # ================= attributes + connections
    rg = {rn: K.red_walk(mps[rn]) for rn in ROUTES}
    def off(rn, d, nb, red_off):
        if nb in ('CeruleanCity',): return red_off
        o = K.best_offset(d, rg[rn], K.walk_grid(nb), red_off)
        log.append('%s %s %s: offset %d (Red %d)' % (rn, d, nb, o, red_off)); return o
    conns = {}
    for rn in ROUTES:
        conns[rn] = [(d, nb, off(rn, d, nb, o)) for d, nb, c, o in
                     [(d, n_, None, o) for d, n_, o in RK.red_conns(rn)]]
    for rn in ROUTES:
        mp = mps[rn]
        K.new_attrs(rn, mp.w, mp.h, border_of(rn), a.labels[rn + 'ms'], a.labels[rn + 'ev'], conns[rn])
        rom[hdr_index(rn) + 1] = RK.OVERWORLD_TS
    opp = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
    for rn in ROUTES:
        for d, nb, o in conns[rn]:
            K.set_conn(nb, opp[d], rn, -o)
    for rn in ROUTES: K.place_blocks(rn, mps[rn].blk, True)
    for nb in ('SaffronCity', 'VermilionCity', 'CeladonCity', 'LavenderTown'):
        K.place_blocks(nb, K.crystal_blocks(nb), False)
    ca = attrs(rom, hdr_index('CeruleanCity'))
    K.place_blocks('CeruleanCity', bytes(rom[fo(ca['blkbank'], ca['blk']):][:ca['w'] * ca['h']]), True)

    # ================= warps back
    for rn, cr, idx in (('Route5', 'Route5CleanseTagHouse', 5),):
        assert K.fix_warps(cr, lambda i, w_: (idx, mapid(rn)) if (w_[3], w_[4]) == mapid(rn) else None)
    for g in GATES:
        doors = [i + 1 for i in range(4) if i + 1 in SAFFRON_SIDE[g]]
        k_ = [0]
        def fn(i, w_, g=g, doors=doors):
            if (w_[3], w_[4]) == mapid(CR_GATE[g]):
                r_ = (doors[min(k_[0], len(doors) - 1)], gid[g]); k_[0] += 1; return r_
        assert K.fix_warps('SaffronCity', fn) >= 1, g

    # ================= wild Pokémon
    for rn in ROUTES: K.red_wild(mapid(rn), rn)

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
