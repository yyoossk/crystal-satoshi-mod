#!/usr/bin/env python3
"""Phase 38: Fuchsia City as in Red / the Pikachu full-color hack:
 * Red's town (Gen I overworld tileset): Red's people, the Safari Zone's Pokémon on show (Chansey, the Voltorb that
   looks like a Poké Ball, Kangaskhan, Slowpoke, Lapras, the fossil Pokémon you did not choose at Mt. Moon) with
   their signs showing the Pokédex entry (as Red's DisplayPokedex: the Pokémon becomes "seen"), the town signs.
 * Routes 15, 18 and 19 joined to it directly at Red's offsets (no more detours through Crystal's gates).
 * Crystal's Pokémon Center, Mart (Red's goods), Gym, warden's home and Safari Zone office (Red's meeting room)
   behind Red's doors; the Safari Zone gate of phase 28.
 * Red's houses (new maps): Bill's grandfather's house, the fishing guru's brother (the Good Rod).
usage: build_phase38.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import redmap as RM
from evedit import MapEvents
import build_phase15 as P15
import build_phase17 as P17
import build_phase25 as P25
import build_phase26 as P26
import build_phase27 as P27
import build_phase28 as P28
import build_phase35 as P35
import build_phase37 as P37
import routekit as RK

FIRST_FLAG = 446                   # 443-445: phase 37
FIRST_MAP = 119                    # 26:116-118 = phase 37
TBANK, BANK, DBANK = 0x6F, 0x67, 0x68
HOUSE_TS, SHIP_TS = 44, 38
SPR = dict(P37.SPR); SPR.update({'SPRITE_FAIRY': 0x4D, 'SPRITE_SEEL': 0x9C, 'SPRITE_FOSSIL': 0x6B})
RED_F = 0x07
HOUSES = ['FuchsiaBillsGrandpasHouse', 'FuchsiaGoodRodHouse']
HOUSE_RED = {'FuchsiaBillsGrandpasHouse': 0x99, 'FuchsiaGoodRodHouse': 0xA4}
CR_DOOR = {'FUCHSIA_MART': 'FuchsiaMart', 'FUCHSIA_POKECENTER': 'FuchsiaPokecenter1F', 'WARDENS_HOUSE': 'SafariZoneWardensHome',
           'FUCHSIA_GYM': 'FuchsiaGym', 'FUCHSIA_MEETING_ROOM': 'SafariZoneMainOffice'}
NEW_DOOR = {'FUCHSIA_BILLS_GRANDPAS_HOUSE': 'FuchsiaBillsGrandpasHouse', 'FUCHSIA_GOOD_ROD_HOUSE': 'FuchsiaGoodRodHouse'}
MART_GOODS = ('ULTRA_BALL', 'GREAT_BALL', 'SUPER_POTION', 'REVIVE', 'FULL_HEAL', 'SUPER_REPEL')
CRYSTAL_MART = ('GREAT_BALL', 'ULTRA_BALL', 'SUPER_POTION', 'HYPER_POTION', 'FULL_HEAL', 'MAX_REPEL', 'FLOWER_MAIL')
GOOD_ROD = 0x3B
DOME_FOSSIL, HELIX_FOSSIL = P15.DOME_FOSSIL, P15.HELIX_FOSSIL
OMANYTE, KABUTO = 138, 140
DEX_SIGNS = {'TEXT_FUCHSIACITY_CHANSEY_SIGN': 113, 'TEXT_FUCHSIACITY_VOLTORB_SIGN': 100,
             'TEXT_FUCHSIACITY_KANGASKHAN_SIGN': 115, 'TEXT_FUCHSIACITY_SLOWPOKE_SIGN': 79, 'TEXT_FUCHSIACITY_LAPRAS_SIGN': 131}
W_SCRIPT_VAR = P27.W_SCRIPT_VAR
# JP home / bank 3E routines (as in the JP GameCornerPrizeMonCheckDex at 03:422A)
SET_SEEN_MON, FADE_TO_MENU, EXIT_ALL_MENUS, NEW_DEX_ENTRY, W_NAMED_OBJECT = 0x3357, 0x2AFB, 0x2B1F, (0x3E, 0x7A09), 0xD296


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    for b in (TBANK, BANK, DBANK):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    got_rod = FL.new()
    hid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(HOUSES)}
    fu = mapid('FuchsiaCity')
    assert rom[0xC22A:0xC245] == bytes([0xCD, 0xFB, 0x2A, 0xFA, 0xDD, 0xC2, 0xEA, 0x96, 0xD2, 0x3E, 0x3E, 0x21, 0x09, 0x7A, 0xCF,
                                        0xCD, 0x1F, 0x2B, 0xC9, 0xFA, 0xDD, 0xC2, 0x3D, 0xCD, 0x57, 0x33, 0xC9])

    # ================= the mart's goods: Red's
    ids = [P15.item_id(n) for n in CRYSTAL_MART]
    mo = rom.find(bytes([7] + ids)); assert mo > 0 and rom.find(bytes([7] + ids), mo + 1) < 0
    red = [P15.item_id(n) for n in MART_GOODS]
    rom[mo:mo + 9] = bytes([len(red)] + red + [0xFF]) + bytes(9 - len(red) - 2)

    # ================= tilesets
    w, h = RK.red_dims('FuchsiaCity'); town = MapPort('FuchsiaCity', K.ow, w, h, 'FuchsiaCity.blk')
    K.dims['FuchsiaCity'] = (w, h)
    redwarps = P25.red_objects('FuchsiaCity')[1]
    tov = RK.warp_overrides(K.ow, town, redwarps)
    K.overworld_variants({'FuchsiaCity': town}, {'FuchsiaCity': tov})
    tss = {'FuchsiaBillsGrandpasHouse': (HOUSE_TS, Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl')),
           'FuchsiaGoodRodHouse': (SHIP_TS, Tileset('Ship', 13, 'ship.bst', SC + '/out/pk_ship.pkl'))}
    hmp = {}
    for n in HOUSES:
        w_, h_ = RK.red_dims(n); ts = tss[n][1]; hmp[n] = MapPort(n, ts, w_, h_, n + '.blk')
        K.ts_variants(tss[n][0], ts, {n: hmp[n]}, {n: {(x, y): P25.warp_override(ts, hmp[n], x, y) for x, y, d, wi in
                                                       P25.red_objects(n)[1]}})
    K.bank = BANK
    K.alloc_headers(FIRST_MAP, len(HOUSES))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end38'); a.end()
    # the Pokédex entry of the Pokémon in wScriptVar (Red: DisplayPokedex)
    a.label('dex'); a.raw(bytes([0xFA, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0x3D, 0xCD, SET_SEEN_MON & 0xFF, SET_SEEN_MON >> 8,
                                 0xCD, FADE_TO_MENU & 0xFF, FADE_TO_MENU >> 8,
                                 0xFA, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0xEA, W_NAMED_OBJECT & 0xFF, W_NAMED_OBJECT >> 8,
                                 0x3E, NEW_DEX_ENTRY[0], 0x21, NEW_DEX_ENTRY[1] & 0xFF, NEW_DEX_ENTRY[1] >> 8, 0xCF,
                                 0xCD, EXIT_ALL_MENUS & 0xFF, EXIT_ALL_MENUS >> 8, 0xC9]))
    def caught(lab, mon):
        o_ = P27.W_DEX_CAUGHT + (mon - 1) // 8
        a.label(lab); a.raw(bytes([0xFA, o_ & 0xFF, o_ >> 8, 0xE6, 1 << ((mon - 1) % 8), 0xEA, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0xC9]))
    caught('c_kabuto', KABUTO); caught('c_omanyte', OMANYTE)
    def callasm_l(l_): a.db(0x0E, BANK); a.dw(l_)
    def show(mon): a.loadmem(W_SCRIPT_VAR, mon); callasm_l('dex')
    def ball(a, texts, lab, o):                 # the Voltorb that looks like a Poké Ball: a person, not an item
        a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = K.rt(RED_F, 6)
        return SPR['SPRITE_POKE_BALL'], 0, 0xFFFF, 0
    ob, bgs = K.red_events(a, texts, 'FuchsiaCity', RED_F, 'F_', {6: ball}, SPR)
    bgl = P25.red_objects('FuchsiaCity')[2]
    for k, (x, y, tc) in enumerate(bgl):
        L_ = 'F_dx%d' % k
        if tc in DEX_SIGNS:
            texts[L_ + 't'] = K.rt(RED_F, 11 + k)
            a.label(L_); a.opentext(); a.writetext(L_ + 't'); a.closetext(); show(DEX_SIGNS[tc]); a.end()
            bgs[k] = (y, x, 0, L_)
        elif tc == 'TEXT_FUCHSIACITY_FOSSIL_SIGN':
            und, om, kb = [RM.crystal_text(b, p) for b, p in RM.asm_hl(RED_F, 11 + k)]
            texts.update(fs_u=und, fs_o=om, fs_k=kb)
            # Red: the dome fossil chosen -> Omanyte here, the helix fossil -> Kabuto (fossil still in the bag, or its
            # Pokémon caught)
            a.label(L_); a.opentext(); a.checkitem(DOME_FOSSIL); a.iftrue('fs_d'); callasm_l('c_kabuto'); a.iftrue('fs_d')
            a.checkitem(HELIX_FOSSIL); a.iftrue('fs_h'); callasm_l('c_omanyte'); a.iftrue('fs_h')
            a.writetext('fs_u'); a.waitbutton(); a.closetext(); a.end()
            a.label('fs_d'); a.writetext('fs_o'); a.closetext(); show(OMANYTE); a.end()
            a.label('fs_h'); a.writetext('fs_k'); a.closetext(); show(KABUTO); a.end()
            bgs[k] = (y, x, 0, L_)
    # houses
    hb = {'FuchsiaBillsGrandpasHouse': K.red_events(a, texts, 'FuchsiaBillsGrandpasHouse', 0x99, 'BG_', {}, SPR)[0]}
    objs = P25.red_objects('FuchsiaGoodRodHouse')[0]
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    T('gr_hi', 0x15, 0x7119); T('gr_full', 0x15, 0x7203); T('gr_no', 0x15, 0x71E0); T('gr_how', 0x15, 0x71ED)
    R = RM.R; o_ = RM.fo(0x15, 0x714E); rams = [R[i + 1] | R[i + 2] << 8 for i in range(o_, o_ + 120) if R[i] == 0x01 and R[i - 1] == 0x50]
    texts['gr_give'] = P27.gen1_text(o_, {('ram', rams[0]): P27.lit('いいつりざお')})
    a.label('gr'); a.faceplayer(); a.opentext(); a.checkevent(got_rod); a.iftrue('gr_h')
    a.writetext('gr_hi'); a.yesorno(); a.iffalse('gr_n')
    a.db(0x1F, GOOD_ROD, 1); a.iffalse('gr_f')                                         # giveitem
    a.writetext('gr_give'); a.waitbutton(); a.closetext(); a.setevent(got_rod); a.end()
    a.label('gr_n'); a.writetext('gr_no'); a.waitbutton(); a.closetext(); a.end()
    a.label('gr_f'); a.writetext('gr_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('gr_h'); a.writetext('gr_how'); a.waitbutton(); a.closetext(); a.end()
    mv, rng = P25.face((0, 0, 0, objs[0]['move'], objs[0]['face']))
    hb['FuchsiaGoodRodHouse'] = [[SPR[objs[0]['sprite']], objs[0]['y'] + 4, objs[0]['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, 'gr', 0xFFFF]]
    K.put_texts(a, texts)

    # warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    safari_gate = [(w_[3], w_[4]) for w_ in K.warps_of('FuchsiaCity') if w_[3] == G26]
    assert len(safari_gate) == 1; safari_gate = safari_gate[0]
    tw = []; back = {}
    for i, (x, y, d, wi) in enumerate(redwarps):
        if d in NEW_DOOR: tw.append(W(x, y, wi, hid[NEW_DOOR[d]]))
        elif d == 'SAFARI_ZONE_GATE': tw.append(W(x, y, 1, safari_gate)); back.setdefault(safari_gate, []).append(i + 1)
        else:
            cr = CR_DOOR[d]
            pi = [k + 1 for k, w_ in enumerate(K.warps_of(cr)) if (w_[3], w_[4]) == fu]
            tw.append(W(x, y, pi[0], mapid(cr))); back.setdefault(cr, []).append(i + 1)
    cbs = []
    for t_, r in MapEvents(rom, 'FuchsiaCity').callbacks:
        L_ = 'Fcb%d' % t_; a.label(L_); a.farsjump(r[1], r[2]); cbs.append((t_, L_))
    K.emit(a, 'FuchsiaCity', tw, [], bgs, ob, cbs)
    for n in HOUSES:
        K.emit(a, n, [W(x, y, wi, fu) for x, y, d, wi in P25.red_objects(n)[1]], [], [], hb[n], [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Fuchsia: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    for i, n in enumerate(HOUSES):
        K.make_map(FIRST_MAP + i, hmp[n], tss[n][0], border_of(n), 'BillsOlderSistersHouse', 3, a, n)

    # ================= attributes, connections (Red's: Routes 15, 18, 19 are Red's), blocks
    conns = RK.red_conns('FuchsiaCity')
    K.new_attrs('FuchsiaCity', w, h, border_of('FuchsiaCity'), a.labels['FuchsiaCityms'], a.labels['FuchsiaCityev'], conns)
    rom[hdr_index('FuchsiaCity') + 1] = RK.OVERWORLD_TS
    opp = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
    for d, nb_, o_ in conns: K.set_conn(nb_, opp[d], 'FuchsiaCity', -o_)
    K.place_blocks('FuchsiaCity', town.blk, True)
    for d, nb_, o_ in conns: K.place_blocks(nb_, K.crystal_blocks(nb_), True)

    # ================= warps back
    for cr, idxs in back.items():
        k_ = [0]
        def fn(i, w_, idxs=idxs, k_=k_):
            if (w_[3], w_[4]) == fu: r_ = (idxs[min(k_[0], len(idxs) - 1)], fu); k_[0] += 1; return r_
        hdr = GROUP26_END + 9 * (cr[1] - G26_COUNT - 1) if isinstance(cr, tuple) else cr
        assert K.fix_warps(hdr, fn) >= 1, cr
    pc = [(x, y) for x, y, d, wi in redwarps if d == 'FUCHSIA_POKECENTER'][0]
    sp_i = [i for i in range(40) if (rom[P26.SPAWN_TABLE + 4 * i], rom[P26.SPAWN_TABLE + 4 * i + 1]) == fu]
    assert len(sp_i) == 1
    rom[P26.SPAWN_TABLE + 4 * sp_i[0] + 2:P26.SPAWN_TABLE + 4 * sp_i[0] + 4] = bytes([pc[0], pc[1] + 1])

    P17.fix_outdoor_sprites(rom, log)
    for s_ in (SPR['SPRITE_SEEL'], SPR['SPRITE_FOSSIL']): P35.add_outdoor_sprite(rom, 'FuchsiaCity', s_, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
