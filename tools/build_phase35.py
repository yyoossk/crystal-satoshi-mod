#!/usr/bin/env python3
"""Phase 35: Routes 11, 12, 13, 14 and 15 as in Red / the Pikachu full-color hack:
 * Red's five routes (trainers, items, hidden items, signs, wild Pokémon), joined to Vermilion, Lavender and Fuchsia
   (Crystal's for now: Fuchsia's east side is walled, so Route 15's west end leads through Crystal's Fuchsia gate).
 * Red's gate buildings (new maps): Route 11 (Oak's aide: the Itemfinder for 30 kinds of Pokémon caught; the
   Nidorino <-> Nidorina trade; binoculars), Route 12 (the girl with TM39 Swift; binoculars), Route 15 (Oak's aide:
   the Exp. Share for 50 kinds; binoculars).
 * Diglett's Cave's Route 11 entrance (new map) leading into Crystal's Diglett's Cave.
 * Route 12's Snorlax and the Poké Flute (Crystal's unused item slot, now a key item): Mr. Fuji, back in his house
   after the Pokémon Tower, gives it; with it Snorlax wakes up and battles (Lv30).
usage: build_phase35.py IN.gbc OUT.gbc OUT.ips
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
import build_phase12 as P12
import build_phase17 as P17
import build_phase19 as P19
import build_phase21 as P21
import build_phase25 as P25
import build_phase27 as P27
import build_phase28 as P28
import build_phase30 as P30
import build_phase34 as P34
import routekit as RK

FIRST_FLAG = 334                   # 318-333: phase 34
FIRST_MAP = 104                    # 26:100-103 = phase 34
TBANK, BANK, DBANK, BANK2 = 0x71, 0x73, 0x69, 0x68     # tilesets / events / blocks / names + Fuji
GATE_TS, CAVERN_TS = 47, 37
SPR = dict(P34.SPR); SPR.update({'SPRITE_SNORLAX': 0x9F, 'SPRITE_BIKER': 0x4A, 'SPRITE_MR_FUJI': 0x2F})
ROUTES = ['Route11', 'Route12', 'Route13', 'Route14', 'Route15']
RED_ID = {'Route11': 0x16, 'Route12': 0x17, 'Route13': 0x18, 'Route14': 0x19, 'Route15': 0x1A}
NEW = ['Route11Gate1F', 'Route11Gate2F', 'Route12Gate1F', 'Route12Gate2F', 'Route15Gate1F', 'Route15Gate2F',
       'DiglettsCaveRoute11']
NEW_RED = {'Route11Gate1F': 0x54, 'Route11Gate2F': 0x56, 'Route12Gate1F': 0x57, 'Route12Gate2F': 0xC3,
           'Route15Gate1F': 0xB8, 'Route15Gate2F': 0xB9, 'DiglettsCaveRoute11': 0x55}
NEW_ROUTE = {'Route11Gate1F': 'Route11', 'Route11Gate2F': 'Route11', 'Route12Gate1F': 'Route12',
             'Route12Gate2F': 'Route12', 'Route15Gate1F': 'Route15', 'Route15Gate2F': 'Route15',
             'DiglettsCaveRoute11': 'Route11'}
POKE_FLUTE = 0x38                  # Crystal's unused item (its effect is the Poké Flute's)
ITEMFINDER, EXP_SHARE = 0x37, 0x39
SNORLAX, NIDORINO, NIDORINA = 143, 33, 30
SFX_POKEFLUTE = 0x26
EV_RESCUED_FUJI = 0x5E1            # phase 11: Jessie and James beaten on the tower's top floor (their hide flag; 0x817 was Mt. Moon's Jessie and James)
BG_UP = 1                          # bg event read only when facing up (binoculars)


def add_outdoor_sprite(rom, name, spr, log):
    """a sprite fix_outdoor_sprites leaves out (Pokémon sprites) into the outdoor list of map name's group"""
    u = US.get(); G = u.groups(); tab = fo(*P17.OUTDOOR_SPRITES_PTR); gi = mapid(name)[0] - 1
    lp = fo(5, rom[tab + 2 * gi] | rom[tab + 2 * gi + 1] << 8); lst = list(rom[lp:lp + 23])
    if spr in lst: return
    used = set()
    for k in range((G[gi + 1] - G[gi]) // 9):
        hdr = G[gi] + 9 * k
        if rom[hdr + 2] not in (1, 2): continue
        a = attrs(rom, hdr); used |= {o[0] for _, o in parse_events(rom, a['scbank'], a['events'])['objs']}
    i = [i for i in range(22, 11, -1) if lst[i] not in used][0]
    log.append('outdoor sprites group %d: %02X -> %02X' % (gi + 1, lst[i], spr)); lst[i] = spr
    rom[lp:lp + 23] = bytes(lst)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (TBANK, BANK, DBANK, BANK2, 0x3F, 0x0B):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    snorlax_gone = FL.new(); snorlax_had = FL.new(); got_flute = FL.new(); fuji_hide = FL.new()
    got_itemfinder = FL.new(); got_expshare = FL.new(); got_tm39 = FL.new()
    nid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(NEW)}

    # ================= the Poké Flute: name, key item, description
    nb = rom[P12.ITEMNAMES_PTR]; o = fo(nb, r16(P12.ITEMNAMES_PTR + 1)); names = []
    for i in range(256):
        e_ = rom.index(0x50, o); names.append(bytes(rom[o:e_ + 1])); o = e_ + 1
    names[POKE_FLUTE - 1] = encode('ポケモンのふえ@')
    an = sp.put(BANK2, b''.join(names)); rom[P12.ITEMNAMES_PTR] = BANK2; w16(P12.ITEMNAMES_PTR + 1, an)
    at = P12.ITEMATTR + 7 * (POKE_FLUTE - 1)
    rom[at:at + 7] = bytes([0, 0, 0, 0, 0x80, 0x02, 0x46])           # can't toss, key item, field: use / battle: use
    w16(P12.ITEMDESC + 2 * (POKE_FLUTE - 1), sp.put(0x0B, encode('ねむっている　ポケモンが<NEXT>めを　さます　ふえ@')))

    # ================= Red's trade: Nidorino -> Nidorina (after phase 19's three and phase 27's)
    ref = P19.NPC_TRADES_REF; assert rom[ref] == 0x21
    to = fo(0x3F, r16(ref + 1)); nt = 7 + len(P19.RED_TRADES) + 1
    table = bytearray(rom[to:to + 16 * nt])
    nick = bytes(RT.R[0x72043 + 3:0x72043 + 7])
    table += bytes([0, NIDORINO, NIDORINA]) + nick + bytes([0x96, 0x66, 0x00]) + (31415 + 1111 * nt).to_bytes(2, 'little') + \
        encode('ゴロウ')[:3] + b'\x00'
    trade_terry = nt
    w16(ref + 1, sp.put(0x3F, bytes(table)))

    # ================= tilesets
    mps = {}
    for rn in ROUTES:
        w, h = RK.red_dims(rn); mps[rn] = MapPort(rn, K.ow, w, h, rn + '.blk'); K.dims[rn] = (w, h)
    ov = {rn: RK.warp_overrides(K.ow, mps[rn], P25.red_objects(rn)[1]) for rn in ROUTES}
    # Route 15's west end: the road's edge tiles lead into Crystal's Fuchsia gate (Crystal's Fuchsia is walled there)
    m15 = mps['Route15']
    def passable(mp, x, y): return K.ow.quad_tile(*mp.block_at(x, y)) in K.ow.passable
    edge15 = [y for y in range(2 * m15.h) if K.ow.quad_tile(*m15.block_at(0, y)) == 0x39]      # the road
    assert edge15 == [8, 9], edge15
    for y in edge15: ov['Route15'][(0, y)] = COLL_CARPET['left']
    log.append('Route 15 west edge rows %s -> Crystal\'s Fuchsia gate' % edge15)
    K.overworld_variants(mps, ov)
    gts = Tileset('Gate', 12, 'gate.bst', SC + '/out/pk_gate.pkl')
    cav = Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl')
    nmp = {}
    for n in NEW:
        w, h = RK.red_dims(n); nmp[n] = MapPort(n, cav if n.startswith('Diglett') else gts, w, h, n + '.blk')
    gates = {n: nmp[n] for n in NEW if 'Gate' in n}
    gov = {n: {(x, y): P25.warp_override(gts, nmp[n], x, y) for x, y, d, wi in P25.red_objects(n)[1]} for n in gates}
    K.ts_variants(GATE_TS, gts, gates, gov)
    dn = 'DiglettsCaveRoute11'
    K.ts_variants(CAVERN_TS, cav, {dn: nmp[dn]},
                  {dn: {(x, y): P25.warp_override(cav, nmp[dn], x, y, True) for x, y, d, wi in P25.red_objects(dn)[1]}},
                  P21.PAIRS)
    K.bank = BANK                                           # attributes / scripts / events
    K.add_parties(ROUTES)
    K.alloc_headers(FIRST_MAP, len(NEW))

    # ================= texts shared by the gates' aides (Red's Oak's aide)
    count = sp.put(BANK, bytes([0x21, P27.W_DEX_CAUGHT & 0xFF, P27.W_DEX_CAUGHT >> 8, 0x06, 0x20, 0x0E, 0x00,
                                0x2A, 0x16, 0x08, 0xCB, 0x3F, 0x30, 0x01, 0x0C, 0x15, 0x20, 0xF8, 0x05, 0x20, 0xF2,
                                0x79, 0xEA, P27.W_SCRIPT_VAR & 0xFF, P27.W_SCRIPT_VAR >> 8, 0xC9]))
    dex = P27.W_DEX_CAUGHT + (SNORLAX - 1) // 8
    caught_bit = sp.put(BANK, bytes([0xFA, dex & 0xFF, dex >> 8, 0xE6, 1 << ((SNORLAX - 1) % 8),
                                     0xEA, P27.W_SCRIPT_VAR & 0xFF, P27.W_SCRIPT_VAR >> 8, 0xC9]))
    i_ = RT.R.index(encode('ぼく　おぼえてます').rstrip(b'\x50')); hi_t = RT.R.rindex(0x00, i_ - 8, i_)
    def aide_texts(need, item):
        subs = {('dec', 0xFFDB): P27.lit(str(need)),
                ('dec', 0xFFDD): bytes([0x09, P27.W_SCRIPT_VAR & 0xFF, P27.W_SCRIPT_VAR >> 8, 0x13]),
                ('ram', 0xCC5B): P27.lit(item)}
        return {k: P27.gen1_text(o_, subs) for k, o_ in
                (('hi', hi_t), ('uhoh', 0x58E80), ('back', 0x58ED3), ('here', 0x58F05), ('got', 0x58F44), ('full', 0x58F5F))}

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end35'); a.end()
    # Route 12's Snorlax
    def snorlax(a, texts, lab, o):
        texts.update(sx_sleep=K.rt(0x17, 1), sx_wake=K.rt(0x17, 13), sx_calm=K.rt(0x17, 14),
                     sx_play=b'\x00' + encode('<PLAYER>は<LINE><POKEMON>のふえを　ふいてみた！@').rstrip(b'\x50') + b'\x57')
        a.label(lab); a.opentext(); a.checkitem(POKE_FLUTE); a.iffalse(lab + 'n')
        a.writetext('sx_play'); a.playsound(SFX_POKEFLUTE); a.waitsfx(); a.promptbutton()
        a.writetext('sx_wake'); a.waitbutton(); a.closetext()
        # caught or not: Snorlax's "caught" bit in the Pokédex before / after the battle
        a.callasm(BANK, caught_bit); a.iffalse(lab + 'c0'); a.setevent(snorlax_had); a.sjump(lab + 'c1')
        a.label(lab + 'c0'); a.clearevent(snorlax_had)
        a.label(lab + 'c1'); a.loadwildmon(SNORLAX, 30); a.startbattle(); a.reloadmapafterbattle()
        a.disappear(2); a.setevent(snorlax_gone)
        a.checkevent(snorlax_had); a.iftrue(lab + 'cm'); a.callasm(BANK, caught_bit); a.iftrue('end35')
        a.label(lab + 'cm'); a.opentext(); a.writetext('sx_calm'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'n'); a.writetext('sx_sleep'); a.waitbutton(); a.closetext(); a.end()
        return SPR['SPRITE_SNORLAX'], 0x90, snorlax_gone, 0       # PAL_NPC_BLUE
    built = {rn: K.red_events(a, texts, rn, RED_ID[rn], rn[5:] + '_', {1: snorlax} if rn == 'Route12' else {}, SPR)
             for rn in ROUTES}
    assert P25.red_objects('Route12')[0][0]['sprite'] == 'SPRITE_SNORLAX'

    # the gates' ground floors (guards) and Diglett's Cave entrance: plain people
    nbuilt = {}
    for n in ('Route11Gate1F', 'Route12Gate1F', 'Route15Gate1F', dn):
        nbuilt[n] = K.red_events(a, texts, n, NEW_RED[n], n + '_', {}, SPR)

    # upstairs: Oak's aides, the trade, the girl with TM39, binoculars
    def obj(o, lab, fl=0xFFFF):
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        return [SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, fl]
    def bgtext(g, b, p):
        return RM.crystal_text(b, p)
    def aide(lab, need, item, item_name, flag, after):
        t = aide_texts(need, item_name); texts.update({lab + k: v for k, v in t.items()}); texts[lab + 'af'] = after
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(flag); a.iftrue(lab + 'fl')
        a.writetext(lab + 'hi'); a.yesorno(); a.iffalse(lab + 'no')
        a.callasm(BANK, count); a.db(0x0B, need); a.dw(lab + 'few')                          # ifless
        a.writetext(lab + 'here'); a.db(0x1F, item, 1); a.iffalse(lab + 'nf')                # giveitem
        a.writetext(lab + 'got'); a.waitbutton(); a.setevent(flag)
        a.label(lab + 'fl'); a.writetext(lab + 'af'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'few'); a.writetext(lab + 'uhoh'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'no'); a.writetext(lab + 'back'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'nf'); a.writetext(lab + 'full'); a.waitbutton(); a.closetext(); a.end()
    def binoc(lab, b, p):
        texts[lab + 't'] = RM.crystal_text(b, p); a.label(lab); a.jumptext(lab + 't')
    # Route 11 gate 2F
    n = 'Route11Gate2F'; objs = P25.red_objects(n)[0]
    a.label('g11y'); a.faceplayer(); a.opentext(); a.db(0x95, trade_terry); a.waitbutton(); a.closetext(); a.end()
    aide('g11a', 30, ITEMFINDER, 'ダウジングマシン', got_itemfinder, RM.crystal_text(0x12, 0x67E3))
    binoc('g11l', 0x12, 0x6875); binoc('g11v', 0x12, 0x6892); binoc('g11r', 0x12, 0x68B5)
    a.label('g11L'); a.checkevent(snorlax_gone); a.iftrue('g11v'); a.sjump('g11l')
    nbuilt[n] = ([obj(objs[0], 'g11y'), obj(objs[1], 'g11a')], [(2, 1, BG_UP, 'g11L'), (2, 6, BG_UP, 'g11r')])
    # Route 12 gate 2F
    n = 'Route12Gate2F'; objs = P25.red_objects(n)[0]
    texts.update(g12g=RM.crystal_text(0x12, 0x69CB), g12x=RM.crystal_text(0x12, 0x6A31), g12f=RM.crystal_text(0x12, 0x6A7B))
    a.label('g12'); a.faceplayer(); a.opentext(); a.checkevent(got_tm39); a.iftrue('g12e')
    a.writetext('g12g'); a.verbosegiveitem(PM.item_id('TM_SWIFT'), 1); a.iffalse('g12n'); a.setevent(got_tm39)
    a.label('g12e'); a.writetext('g12x'); a.waitbutton(); a.closetext(); a.end()
    a.label('g12n'); a.writetext('g12f'); a.waitbutton(); a.closetext(); a.end()
    binoc('g12l', 0x12, 0x6A93); binoc('g12r', 0x12, 0x6AB9)
    nbuilt[n] = ([obj(objs[0], 'g12')], [(2, 1, BG_UP, 'g12l'), (2, 6, BG_UP, 'g12r')])
    # Route 15 gate 2F
    n = 'Route15Gate2F'; objs = P25.red_objects(n)[0]
    aide('g15a', 50, EXP_SHARE, 'がくしゅうそうち', got_expshare, RM.crystal_text(0x12, 0x6BC0))
    binoc('g15r', 0x12, 0x6C2C)
    nbuilt[n] = ([obj(objs[0], 'g15a')], [(2, 6, BG_UP, 'g15r')])
    K.put_texts(a, texts); texts = {}

    # ================= warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    fuchsia_gate = mapid('Route15FuchsiaGate')
    rw = {}
    for rn in ROUTES:
        rw[rn] = []
        for x, y, d, wi in P25.red_objects(rn)[1]:
            if d == 'ROUTE_12_SUPER_ROD_HOUSE': rw[rn].append(W(x, y, 1, mapid('Route12SuperRodHouse')))
            else:
                n_ = ''.join(p.capitalize() for p in d.split('_')).replace('Route', 'Route')
                n_ = {'ROUTE_11_GATE_1F': 'Route11Gate1F', 'ROUTE_12_GATE_1F': 'Route12Gate1F',
                      'ROUTE_15_GATE_1F': 'Route15Gate1F', 'DIGLETTS_CAVE_ROUTE_11': dn}[d]
                rw[rn].append(W(x, y, wi, nid[n_]))
    r15_edge = []
    for k, y in enumerate(edge15):
        r15_edge.append(len(rw['Route15']) + 1); rw['Route15'].append(W(0, y, 3 + min(k, 1), fuchsia_gate))
    nw = {}
    for n in NEW:
        rn = NEW_ROUTE[n]; nw[n] = []
        for x, y, d, wi in P25.red_objects(n)[1]:
            if d == 'LAST_MAP': nw[n].append(W(x, y, wi, mapid(rn)))
            elif d == 'DIGLETTS_CAVE': nw[n].append(W(x, y, 1, mapid('DiglettsCave')))
            else:
                n_ = {'ROUTE_11_GATE_2F': 'Route11Gate2F', 'ROUTE_11_GATE_1F': 'Route11Gate1F',
                      'ROUTE_12_GATE_2F': 'Route12Gate2F', 'ROUTE_12_GATE_1F': 'Route12Gate1F',
                      'ROUTE_15_GATE_2F': 'Route15Gate2F', 'ROUTE_15_GATE_1F': 'Route15Gate1F'}[d]
                nw[n].append(W(x, y, wi, nid[n_]))
    for rn in ROUTES:
        ob, bgs = built[rn]; cbs = []
        for t_, r in MapEvents(rom, rn).callbacks:
            L_ = rn + 'cb%d' % t_; a.label(L_); a.farsjump(r[1], r[2]); cbs.append((t_, L_))
        K.emit(a, rn, rw[rn], [], bgs, ob, cbs)
    for n in NEW:
        ob, bgs = nbuilt[n]
        K.emit(a, n, nw[n], [], bgs, ob, [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('routes / gates: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    hsrc = {n: 'Route15FuchsiaGate' for n in NEW}; hsrc[dn] = 'DiglettsCave'
    for i, n in enumerate(NEW):
        K.make_map(FIRST_MAP + i, nmp[n], CAVERN_TS if n == dn else GATE_TS, border_of(n), hsrc[n], 4 if n == dn else 6, a, n)
        hh = GROUP26_END + 9 * (FIRST_MAP + i - G26_COUNT - 1)
        rom[hh + 5] = rom[hdr_index(NEW_ROUTE[n]) + 5]                                        # landmark: the route's

    # ================= attributes + connections
    rg = {rn: K.red_walk(mps[rn]) for rn in ROUTES}
    def off(rn, d, nb_, red_off):
        if nb_ in ROUTES: return red_off
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
    for nb_ in ('VermilionCity', 'LavenderTown', 'FuchsiaCity'):
        K.place_blocks(nb_, K.crystal_blocks(nb_), False)

    # ================= warps back
    r12 = mapid('Route12'); r15 = mapid('Route15'); r11 = mapid('Route11')
    sr = [i + 1 for i, (x, y, d, wi) in enumerate(P25.red_objects('Route12')[1]) if d == 'ROUTE_12_SUPER_ROD_HOUSE'][0]
    assert K.fix_warps('Route12SuperRodHouse', lambda i, w_: (sr, r12) if (w_[3], w_[4]) == r12 else None) == 2
    k_ = [0]
    def fg(i, w_):
        if (w_[3], w_[4]) == r15: r_ = (r15_edge[min(k_[0], len(r15_edge) - 1)], r15); k_[0] += 1; return r_
    assert K.fix_warps('Route15FuchsiaGate', fg) == 2
    dc_w = [i + 1 for i, (x, y, d, wi) in enumerate(P25.red_objects(dn)[1]) if d == 'DIGLETTS_CAVE'][0]
    assert K.fix_warps('DiglettsCave', lambda i, w_: (dc_w, nid[dn]) if i == 0 else None) == 1

    # ================= Mr. Fuji at home after the Pokémon Tower: the Poké Flute
    me = MapEvents(rom, 'MrFujisHouse')
    a = Asm(sp.here(BANK2)); a.bank = BANK2
    fo_ = [o_ for o_ in P25.red_objects('MrFujisHouse')[0] if o_['sprite'] == 'SPRITE_MR_FUJI'][0]
    fj = []
    for b, p in RM.asm_hl(0x95, 5):
        try: fj.append(RM.crystal_text(b, p))
        except ValueError: pass                      # the "received" text (item name from RAM): Crystal's own
    assert len(fj) == 3, len(fj)
    t_help, t_full, t_helped = fj
    t_expl = RM.crystal_text(7, 0x6082); assert t_expl[1] == 0x51; t_expl = b'\x00' + t_expl[2:]
    texts.update(fj_help=t_help, fj_expl=t_expl, fj_full=t_full, fj_helped=t_helped)
    a.label('fj'); a.faceplayer(); a.opentext(); a.checkevent(got_flute); a.iftrue('fj_h')
    a.writetext('fj_help'); a.verbosegiveitem(POKE_FLUTE, 1); a.iffalse('fj_f'); a.setevent(got_flute)
    a.writetext('fj_expl'); a.waitbutton(); a.closetext(); a.end()
    a.label('fj_h'); a.writetext('fj_helped'); a.waitbutton(); a.closetext(); a.end()
    a.label('fj_f'); a.writetext('fj_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('fj_cb'); a.checkevent(EV_RESCUED_FUJI); a.iftrue('fj_cs')
    a.setevent(fuji_hide); a.endcallback()
    a.label('fj_cs'); a.clearevent(fuji_hide); a.endcallback()
    me.add_object(SPR['SPRITE_MR_FUJI'], fo_['x'], fo_['y'], P25.face((0, 0, 0, 'STAY', 'DOWN'))[0], 'fj', fuji_hide)
    cbs = [c for c in me.callbacks if c[0] == 2]
    if cbs:
        a.label('fj_cb0'); a.scall('fj_cb2'); ref_ = cbs[0][1]; a.farsjump(ref_[1], ref_[2])
        raise NotImplementedError('MrFujisHouse already has an objects callback')
    me.callbacks.append((2, 'fj_cb'))
    K.put_texts(a, texts)
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK2, blob) == base; me.install(a)
    log.append('Mr. Fuji\'s house: events %X:%04X (%d bytes)' % (BANK2, base, len(blob)))

    # ================= wild Pokémon
    for rn in ROUTES: K.red_wild(mapid(rn), rn)

    P17.fix_outdoor_sprites(rom, log)
    add_outdoor_sprite(rom, 'Route12', SPR['SPRITE_SNORLAX'], log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
