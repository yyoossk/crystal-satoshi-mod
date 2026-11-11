#!/usr/bin/env python3
"""Phase 42: Saffron City as in Red / the Pikachu full-color hack:
 * Red's town (Gen I overworld tileset): Team Rocket all over the town until Giovanni leaves Silph Co. (phase 14), the
   guard in front of Silph Co.'s door (moves aside once Mr. Fuji is rescued), the people who come back afterwards
   (with the Pidgeot), the signs.  Routes 5-8 joined directly at Red's offsets; Red's gates (phase 34) lead back to
   their routes again.
 * Crystal's Pokémon Center, Mart (Red's goods), Gym, Mr. Psychic's house behind Red's doors; Red's Silph Co.
 * The Fighting Dojo (Crystal's room): Red's five Black Belts and the Karate Master, then Hitmonlee or Hitmonchan.
 * The Copycat's house (Crystal's rooms): Red's people; the Copycat gives TM31 for a Poké Doll.
 * Red's Pidgey house (new map).
usage: build_phase42.py IN.gbc OUT.gbc OUT.ips
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
import build_phase34 as P34
import build_phase37 as P37
import build_phase38 as P38
import build_phase41 as P41
import routekit as RK

FIRST_FLAG = 462                   # 456-461: phase 41
FIRST_MAP = 138                    # 26:126-137 = phase 41
TBANK, BANK, DBANK, BANK2 = 0x70, 0x6F, 0x6B, 0x65
HOUSE_TS = 44
SPR = dict(P41.SPR); SPR.update({'SPRITE_CHANNELER': 0x30})
RED_S = 0x0A
CR_DOOR = {'COPYCATS_HOUSE_1F': 'CopycatsHouse1F', 'FIGHTING_DOJO': 'FightingDojo', 'SAFFRON_GYM': 'SaffronGym',
           'SAFFRON_MART': 'SaffronMart', 'SILPH_CO_1F': 'SilphCo1F', 'SAFFRON_POKECENTER': 'SaffronPokecenter1F',
           'MR_PSYCHICS_HOUSE': 'MrPsychicsHouse'}
MART_GOODS = ('GREAT_BALL', 'HYPER_POTION', 'MAX_REPEL', 'ESCAPE_ROPE', 'FULL_HEAL', 'REVIVE')
CRYSTAL_MART = ('GREAT_BALL', 'ULTRA_BALL', 'HYPER_POTION', 'MAX_POTION', 'FULL_HEAL', 'X_ATTACK', 'X_DEFEND')
GIO_LEFT = 0x606                   # phase 14: Giovanni's object flag on Silph Co. 11F (set when he leaves)
EV_RESCUED_FUJI = 0x817
POKE_DOLL, TM_MIMIC = 0x25, 0xDF
HITMONLEE, HITMONCHAN, PIDGEY, PIDGEOT, CLEFAIRY, DODUO = 106, 107, 16, 18, 35, 84
W_SCRIPT_VAR = P27.W_SCRIPT_VAR


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    for b in (TBANK, BANK, DBANK, BANK2):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    rk_hide, cz_hide, r8_hide, r9_hide = FL.new(), FL.new(), FL.new(), FL.new()
    beat_master, got_hitmon, lee_gone, chan_gone, got_tm31 = FL.new(), FL.new(), FL.new(), FL.new(), FL.new()
    saf = mapid('SaffronCity')
    pidgey = (G26, FIRST_MAP)

    # ================= the mart's goods: Red's
    ids = [P15.item_id(n) for n in CRYSTAL_MART]
    mo = rom.find(bytes([8] + ids)); assert mo > 0 and rom.find(bytes([8] + ids), mo + 1) < 0
    red = [P15.item_id(n) for n in MART_GOODS]
    rom[mo:mo + 11] = bytes([len(red)] + red + [0xFF]) + bytes(11 - len(red) - 2)

    # ================= tilesets
    w, h = RK.red_dims('SaffronCity'); town = MapPort('SaffronCity', K.ow, w, h, 'SaffronCity.blk')
    K.dims['SaffronCity'] = (w, h)
    redwarps = P25.red_objects('SaffronCity')[1]
    K.overworld_variants({'SaffronCity': town}, {'SaffronCity': RK.warp_overrides(K.ow, town, redwarps)})
    hts = Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl')
    w_, h_ = RK.red_dims('SaffronPidgeyHouse'); hmp = MapPort('SaffronPidgeyHouse', hts, w_, h_, 'SaffronPidgeyHouse.blk')
    K.ts_variants(HOUSE_TS, hts, {'SaffronPidgeyHouse': hmp},
                  {'SaffronPidgeyHouse': {(x, y): P25.warp_override(hts, hmp, x, y) for x, y, d, wi in P25.red_objects('SaffronPidgeyHouse')[1]}})
    K.bank = BANK
    K.add_parties(['FightingDojo'])
    K.alloc_headers(FIRST_MAP, 1)

    # ================= Saffron City
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end42'); a.end()
    objs = P25.red_objects('SaffronCity')[0]
    pg = [i for i, o in enumerate(objs) if o['sprite'] == 'SPRITE_BIRD'][0]
    def pidgeot(a, texts, lab, o):
        b_, p_ = RM.text_ptr(RED_S, pg + 1); o_ = RM.fo(b_, p_); e_ = o_
        while RM.R[e_] != 0x50: e_ += 1
        assert RM.R[e_ + 1] == 0x15                          # (Red: text, then the cry)
        texts['S_pgt'] = bytes(RM.R[o_:e_]) + b'\x57'
        a.label(lab); a.opentext(); a.writetext('S_pgt'); a.cry(PIDGEOT); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    ob, bgs = K.red_events(a, texts, 'SaffronCity', RED_S, 'S_', {pg + 1: pidgeot}, SPR)
    assert [o['sprite'] for o in objs][:7] == ['SPRITE_ROCKET'] * 7 and objs[13]['sprite'] == objs[14]['sprite'] == 'SPRITE_ROCKET'
    for i in range(7): ob[i][10] = rk_hide
    for i in range(7, 13): ob[i][10] = cz_hide
    ob[13][10] = r8_hide; ob[14][10] = r9_hide
    # Red's toggles: the Rockets until Giovanni leaves Silph Co.; the door guard until Mr. Fuji is rescued, then the
    # other one beside the door
    a.label('Scbo'); a.checkevent(GIO_LEFT); a.iftrue('Scb_g')
    a.clearevent(rk_hide); a.setevent(cz_hide)
    a.checkevent(EV_RESCUED_FUJI); a.iftrue('Scb_f')
    a.clearevent(r8_hide); a.setevent(r9_hide); a.endcallback()
    a.label('Scb_f'); a.setevent(r8_hide); a.clearevent(r9_hide); a.endcallback()
    a.label('Scb_g'); a.setevent(rk_hide); a.clearevent(cz_hide); a.setevent(r8_hide); a.setevent(r9_hide); a.endcallback()
    # warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    tw = []; back = {}
    for i, (x, y, d, wi) in enumerate(redwarps):
        if d == 'SAFFRON_PIDGEY_HOUSE': tw.append(W(x, y, wi, pidgey)); continue
        cr = CR_DOOR[d]
        pi = [k + 1 for k, w__ in enumerate(K.warps_of(cr)) if (w__[3], w__[4]) == saf]
        tw.append(W(x, y, pi[0], mapid(cr))); back[cr] = i + 1
    cbs = [(2, 'Scbo')]
    for t_, r in MapEvents(rom, 'SaffronCity').callbacks:
        if t_ == 5: a.label('Scb5'); a.farsjump(r[1], r[2]); cbs.append((5, 'Scb5'))       # (fly point)
    K.emit(a, 'SaffronCity', tw, [], bgs, ob, cbs)
    # the Pidgey house
    po = P25.red_objects('SaffronPidgeyHouse')[0]
    texts['ph_g'] = K.rt(0xB3, 1); first, more = P37.text_then_asm(0xB3, 2); texts['ph_p'] = first
    texts['ph_y'] = K.rt(0xB3, 3); texts['ph_l'] = K.rt(0xB3, 4)
    a.label('phg'); a.jumptextfaceplayer('ph_g')
    a.label('php'); a.opentext(); a.writetext('ph_p'); a.cry(PIDGEY); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    a.label('phy'); a.jumptextfaceplayer('ph_y')
    a.label('phl'); a.jumptext('ph_l')
    def obj(o, lab, fl=0xFFFF, spr=None):
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        return [spr or SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, fl]
    K.emit(a, 'SaffronPidgeyHouse', [W(x, y, wi, saf) for x, y, d, wi in P25.red_objects('SaffronPidgeyHouse')[1]], [], [],
           [obj(po[0], 'phg'), obj(po[1], 'php'), obj(po[2], 'phy'), obj(po[3], 'phl')], [])
    K.put_texts(a, texts); texts = {}
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Saffron: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    LABELS['SaffronCityms'] = a.labels['SaffronCityms']; LABELS['SaffronCityev'] = a.labels['SaffronCityev']
    K.make_map(FIRST_MAP, hmp, HOUSE_TS, border_of('SaffronPidgeyHouse'), 'MrPsychicsHouse', 3, a, 'SaffronPidgeyHouse')

    # ================= the Fighting Dojo (Crystal's room, Red's people)
    me = MapEvents(rom, 'FightingDojo')
    a = Asm(sp.here(BANK2)); a.bank = BANK2; texts = {}
    a.label('dojo_end'); a.end()
    a.label('dex'); a.raw(bytes([0xFA, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0x3D, 0xCD, P38.SET_SEEN_MON & 0xFF, P38.SET_SEEN_MON >> 8,
                                 0xCD, P38.FADE_TO_MENU & 0xFF, P38.FADE_TO_MENU >> 8,
                                 0xFA, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0xEA, P38.W_NAMED_OBJECT & 0xFF, P38.W_NAMED_OBJECT >> 8,
                                 0x3E, P38.NEW_DEX_ENTRY[0], 0x21, P38.NEW_DEX_ENTRY[1] & 0xFF, P38.NEW_DEX_ENTRY[1] >> 8, 0xCF,
                                 0xCD, P38.EXIT_ALL_MENUS & 0xFF, P38.EXIT_ALL_MENUS >> 8, 0xC9]))
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    T('km_a', 0x17, 0x60A2); T('km_w', 0x17, 0x60F1); T('km_g', 0x17, 0x6104); T('km_s', 0x17, 0x616B)
    T('hb_greedy', 0x17, 0x63DD); T('hb_lee', 0x17, 0x6362); T('hb_chan', 0x17, 0x63C2)
    dobjs = P25.red_objects('FightingDojo')[0]
    def master(a, texts, lab, o):
        cid, pid = K.party_of[('FightingDojo', 0)]
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_hitmon); a.iftrue(lab + 'd')
        a.checkevent(beat_master); a.iftrue(lab + 'b')
        a.writetext('km_a'); a.waitbutton(); a.closetext()
        a.winlosstext('km_w', 0); a.loadtrainer(cid, pid); a.startbattle(); a.reloadmapafterbattle(); a.setevent(beat_master)
        a.opentext()
        a.label(lab + 'b'); a.writetext('km_g'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'd'); a.writetext('km_s'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    def ball(mon, t_, flag, oid):
        def f(a, texts, lab, o):
            a.label(lab); a.checkevent(got_hitmon); a.iftrue(lab + 'g')
            a.loadmem(W_SCRIPT_VAR, mon); a.db(0x0E, BANK2); a.dw('dex')                        # Red: DisplayPokedex
            a.opentext(); a.writetext(t_); a.yesorno(); a.iffalse(lab + 'n')
            a.givepoke(mon, 30); a.iffalse(lab + 'n'); a.closetext()
            a.disappear(oid); a.setevent(flag); a.setevent(got_hitmon); a.end()
            a.label(lab + 'n'); a.closetext(); a.end()
            a.label(lab + 'g'); a.jumptext('hb_greedy')
            return SPR['SPRITE_POKE_BALL'], 0, flag, 0
        return f
    assert dobjs[5]['sprite'] == dobjs[6]['sprite'] == 'SPRITE_POKE_BALL'
    K.ignore_hidden = {'PrintFightingDojoText', 'PrintFightingDojoText2', 'PrintFightingDojoText3'}                 # Crystal's room keeps its own signs
    dob, dbgs = K.red_events(a, texts, 'FightingDojo', 0xB1, 'D_', {1: master, 6: ball(HITMONLEE, 'hb_lee', lee_gone, 7),
                                                                    7: ball(HITMONCHAN, 'hb_chan', chan_gone, 8)}, SPR)
    me.objs = [[bytearray(o[:9] + [0, 0] + [o[10] & 0xFF, o[10] >> 8]), o[9]] for o in dob]
    K.put_texts(a, texts); texts = {}
    me.write(a, sp)
    # ================= the Copycat's house (Crystal's rooms): Red's people where Crystal's stand
    c1 = MapEvents(rom, 'CopycatsHouse1F'); c2 = MapEvents(rom, 'CopycatsHouse2F')
    base = a.base; blob = a.done(); assert sp.put(BANK2, blob) == base; me.install(a)
    log.append('Fighting Dojo: events %X:%04X (%d bytes)' % (BANK2, base, len(blob)))

    a = Asm(sp.here(BANK2)); a.bank = BANK2; texts = {}
    texts['c1_w'] = K.rt(0xAF, 1); texts['c1_m'] = K.rt(0xAF, 2); first, more = P37.text_then_asm(0xAF, 3); texts['c1_c'] = first
    a.label('c1w'); a.jumptextfaceplayer('c1_w')
    a.label('c1m'); a.jumptextfaceplayer('c1_m')
    a.label('c1c'); a.opentext(); a.writetext('c1_c'); a.cry(CLEFAIRY); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    co = P25.red_objects('CopycatsHouse1F')[0]
    def at(o_crys, spr, lab, mv, rng=0):
        return [bytearray([spr, o_crys[0][1], o_crys[0][2], mv, rng, 0xFF, 0xFF, 0, 0, 0, 0, 0xFF, 0xFF]), lab]
    cr1 = c1.objs                                                              # (2,3) woman, (5,4) man, (6,6) Clefairy
    c1.objs = [at(cr1[0], SPR['SPRITE_MIDDLE_AGED_WOMAN'], 'c1w', P25.face((0, 0, 0, 'STAY', 'DOWN'))[0]),
               at(cr1[1], SPR['SPRITE_MIDDLE_AGED_MAN'], 'c1m', P25.face((0, 0, 0, 'STAY', 'NONE'))[0]),
               [cr1[2][0], 'c1c']]
    c1.objs[2][0][11:13] = b'\xff\xff'
    K.put_texts(a, texts); texts.clear()
    c1.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK2, blob) == base; c1.install(a)
    a = Asm(sp.here(BANK2)); a.bank = BANK2
    T('cc_hi', 0x17, 0x5CF6); T('cc_doll', 0x17, 0x5D78); T('cc_full', 0x17, 0x5E4E); T('cc_after', 0x17, 0x5DFD)
    texts['cc_dd'] = K.rt(0xB0, 2); texts['cc_toy'] = K.rt(0xB0, 3)
    a.label('cc'); a.faceplayer(); a.opentext(); a.checkevent(got_tm31); a.iftrue('cc_a')
    a.checkitem(POKE_DOLL); a.iftrue('cc_d')
    a.writetext('cc_hi'); a.waitbutton(); a.closetext(); a.end()
    a.label('cc_d'); a.writetext('cc_doll'); a.promptbutton(); a.verbosegiveitem(TM_MIMIC, 1); a.iffalse('cc_f')
    a.db(0x20, POKE_DOLL, 1); a.setevent(got_tm31); a.closetext(); a.end()                       # takeitem
    a.label('cc_f'); a.writetext('cc_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('cc_a'); a.writetext('cc_after'); a.waitbutton(); a.closetext(); a.end()
    a.label('ccd'); a.opentext(); a.writetext('cc_dd'); a.cry(DODUO); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    a.label('cct'); a.jumptext('cc_toy')
    cr2 = c2.objs                       # (4,3) Copycat x2, (6,4) Doduo, three dolls
    girl = at(cr2[0], SPR['SPRITE_BRUNETTE_GIRL'], 'cc', P25.face((0, 0, 0, 'STAY', 'DOWN'))[0])
    c2.objs = [girl, [cr2[2][0], 'ccd'], [cr2[3][0], 'cct'], [cr2[4][0], 'cct'], [cr2[5][0], 'cct']]
    for o_ in c2.objs[1:]: o_[0][11:13] = b'\xff\xff'
    c2.callbacks = []
    K.put_texts(a, texts)
    c2.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK2, blob) == base; c2.install(a)
    log.append('Copycat\'s house: events %X:%04X' % (BANK2, base))

    # ================= attributes, connections (Routes 5-8 are Red's), blocks
    conns = RK.red_conns('SaffronCity')
    K.new_attrs('SaffronCity', w, h, border_of('SaffronCity'), Kl(K, 'SaffronCityms'), Kl(K, 'SaffronCityev'), conns)
    rom[hdr_index('SaffronCity') + 1] = RK.OVERWORLD_TS
    opp = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
    for d, nb_, o_ in conns: K.set_conn(nb_, opp[d], 'SaffronCity', -o_)
    K.place_blocks('SaffronCity', town.blk, True)
    for d, nb_, o_ in conns: K.place_blocks(nb_, K.crystal_blocks(nb_), True)

    # ================= warps back; Red's gates: their Saffron-side doors lead back to the routes again
    for cr, idx in back.items():
        assert K.fix_warps(cr, lambda i, w_, idx=idx: (idx, saf) if (w_[3], w_[4]) == saf else None) >= 1, cr
    for k, g in enumerate(P34.GATES):
        gid = (G26, P34.FIRST_MAP + k); rn = mapid('Route' + g[5])
        reds = P25.red_objects(g)[1]
        n_ = K.fix_warps(GROUP26_END + 9 * (gid[1] - G26_COUNT - 1),
                         lambda i, w_, reds=reds, rn=rn: (reds[i][3], rn) if (w_[3], w_[4]) == saf else None)
        assert n_ == len(P34.SAFFRON_SIDE[g]), (g, n_)
    pc = [(x, y) for x, y, d, wi in redwarps if d == 'SAFFRON_POKECENTER'][0]
    sp_i = [i for i in range(40) if (rom[P26.SPAWN_TABLE + 4 * i], rom[P26.SPAWN_TABLE + 4 * i + 1]) == saf]
    assert len(sp_i) == 1
    rom[P26.SPAWN_TABLE + 4 * sp_i[0] + 2:P26.SPAWN_TABLE + 4 * sp_i[0] + 4] = bytes([pc[0], pc[1] + 1])

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


LABELS = {}
def Kl(K, name): return LABELS[name]


if __name__ == '__main__':
    main()
