#!/usr/bin/env python3
"""Phase 41: Celadon's Department Store and Mansion as in Red / the Pikachu full-color hack (new maps; Crystal's are
no longer reached):
 * Department Store 1F-5F, the roof and the elevator (1F-5F): the receptionist, Red's shops (2F: medicine / TMs,
   4F: Poké Doll and the evolution stones, 5F: X items / vitamins), the 3F clerk who gives TM18, the video game corner
   (Super Famicoms, posters), the roof's vending machines (Fresh Water / Soda Pop / Lemonade, as Crystal's) and the
   thirsty little girl who gives TM13 / TM48 / TM49 for them.
 * Mansion 1F-3F, the roof and the roof house: the landlady and her Pokémon (they cry), the PC, Game Freak's room (the
   game designer shows the diploma once 150 kinds are caught), the Eevee in the Poké Ball (Lv25).
usage: build_phase41.py IN.gbc OUT.gbc OUT.ips
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
import build_phase27 as P27
import build_phase28 as P28
import build_phase37 as P37
import build_phase40 as P40
import routekit as RK

FIRST_FLAG = 456                   # 452-455: phase 40
FIRST_MAP = 126                    # 26:123-125 = phase 40
TBANK, BANK, DBANK = 0x6D, 0x68, 0x70
LOBBY_TS, HOUSE_TS = 35, 44
SPR = dict(P40.SPR); SPR['SPRITE_FAIRY'] = 0x4D
MART = ['CeladonMart1F', 'CeladonMart2F', 'CeladonMart3F', 'CeladonMart4F', 'CeladonMart5F', 'CeladonMartRoof',
        'CeladonMartElevator']
MANSION = ['CeladonMansion1F', 'CeladonMansion2F', 'CeladonMansion3F', 'CeladonMansionRoof', 'CeladonMansionRoofHouse']
NEW = MART + MANSION
RED_ID = {'CeladonMart1F': 0x7A, 'CeladonMart2F': 0x7B, 'CeladonMart3F': 0x7C, 'CeladonMart4F': 0x7D,
          'CeladonMart5F': 0x88, 'CeladonMartRoof': 0x7E, 'CeladonMartElevator': 0x7F, 'CeladonMansion1F': 0x80,
          'CeladonMansion2F': 0x81, 'CeladonMansion3F': 0x82, 'CeladonMansionRoof': 0x83, 'CeladonMansionRoofHouse': 0x84}
CONST = {'CELADON_MART_%s' % k: 'CeladonMart%s' % k for k in ('1F', '2F', '3F', '4F', '5F')}
CONST.update({'CELADON_MART_ROOF': 'CeladonMartRoof', 'CELADON_MART_ELEVATOR': 'CeladonMartElevator',
              'CELADON_MANSION_1F': 'CeladonMansion1F', 'CELADON_MANSION_2F': 'CeladonMansion2F',
              'CELADON_MANSION_3F': 'CeladonMansion3F', 'CELADON_MANSION_ROOF': 'CeladonMansionRoof',
              'CELADON_MANSION_ROOF_HOUSE': 'CeladonMansionRoofHouse'})
# Red's shops -> Crystal's Celadon mart ids (their lists are replaced)
MART_LAVENDER, MARTS = 21, {
    23: ('GREAT_BALL', 'SUPER_POTION', 'REVIVE', 'SUPER_REPEL', 'ANTIDOTE', 'BURN_HEAL', 'ICE_HEAL', 'AWAKENING', 'PARLYZ_HEAL'),
    24: ('TM_DOUBLE_TEAM', 'TM_REFLECT', 'TM_RAZOR_WIND', 'TM_HORN_DRILL', 'TM_EGG_BOMB', 'TM_MEGA_PUNCH', 'TM_MEGA_KICK',
         'TM_TAKE_DOWN', 'TM_SUBMISSION'),
    26: ('POKE_DOLL', 'FIRE_STONE', 'THUNDERSTONE', 'WATER_STONE', 'LEAF_STONE'),
    27: ('X_ACCURACY', 'GUARD_SPEC', 'DIRE_HIT', 'X_ATTACK', 'X_DEFEND', 'X_SPEED', 'X_SPECIAL'),
    28: ('PROTEIN', 'IRON', 'CARBOS', 'CALCIUM')}           # (JP Red: no HP Up at 5F)
MART_OF = {('CeladonMart2F', 0): 23, ('CeladonMart2F', 1): 24, ('CeladonMart4F', 0): 26, ('CeladonMart5F', 2): 27,
           ('CeladonMart5F', 3): 28}
FRESH_WATER, SODA_POP, LEMONADE = 0x2E, 0x2F, 0x30
EEVEE, MEOWTH, CLEFAIRY, NIDORAN_F = 133, 52, 35, 29
SFX_ELEVATOR, FLOOR_1F = 0x6E, 4
SPECIAL_DIPLOMA = 0x6B
W_SCRIPT_VAR = P27.W_SCRIPT_VAR


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (TBANK, BANK, DBANK, 0x05):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    got_tm18, got_tm13, got_tm48, got_tm49, eevee_gone = FL.new(), FL.new(), FL.new(), FL.new(), FL.new()
    nid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(NEW)}
    cel = mapid('CeladonCity')
    mansion_ts = rom[GROUP26_END + 9 * (124 - G26_COUNT - 1) + 1]          # phase 40's chief's house: Red's Mansion tileset

    # ================= Red's shops (new lists in bank 5; Crystal's Celadon mart table entries re-pointed)
    ids = [P15.item_id(n) for n in ('GREAT_BALL', 'POTION', 'SUPER_POTION', 'MAX_REPEL', 'ANTIDOTE', 'PARLYZ_HEAL',
                                    'AWAKENING', 'BURN_HEAL')]
    mo = orig.find(bytes([8] + ids)); assert mo // 0x4000 == 5
    p_ = 0x4000 + mo % 0x4000; refs = [i for i in range(0x14000, 0x18000 - 1) if orig[i] == p_ & 0xFF and orig[i + 1] == p_ >> 8]
    assert len(refs) == 1; table = refs[0] - 2 * MART_LAVENDER
    for mid, goods in MARTS.items():
        lst = [PM.item_id(n) for n in goods]
        w16(table + 2 * mid, sp.put(0x05, bytes([len(lst)] + lst + [0xFF])))

    # ================= tilesets
    tss = {'Lobby': (LOBBY_TS, Tileset('Lobby', 18, 'lobby.bst', SC + '/out/pk_lobby.pkl')),
           'Mansion': (mansion_ts, Tileset('Mansion', 19, 'mansion.bst', SC + '/out/pk_mansion.pkl')),
           'House': (HOUSE_TS, Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl'))}
    tk = {n: 'Lobby' for n in MART}; tk.update({n: 'Mansion' for n in MANSION}); tk['CeladonMansionRoofHouse'] = 'House'
    nmp = {}
    for n in NEW:
        w_, h_ = RK.red_dims(n); nmp[n] = MapPort(n, tss[tk[n]][1], w_, h_, n + '.blk')
    for k, (tid, ts) in tss.items():
        mm = {n: nmp[n] for n in NEW if tk[n] == k}
        K.ts_variants(tid, ts, mm, {n: {(x, y): P25.warp_override(ts, nmp[n], x, y) for x, y, d, wi in P25.red_objects(n)[1]}
                                    for n in mm})
    K.bank = BANK
    K.alloc_headers(FIRST_MAP, len(NEW))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end41'); a.end()
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    def mart(mid):
        def f(a, texts, lab, o):
            a.label(lab); a.faceplayer(); a.opentext(); a.db(0x93, 0x00); a.dw(mid); a.closetext(); a.end()   # pokemart
            return None, 0, 0xFFFF, 0
        return f
    def cry(g, tid, mon):
        def f(a, texts, lab, o):
            first, more = P37.text_then_asm(g, tid); texts[lab + 't'] = first
            a.label(lab); a.opentext(); a.writetext(lab + 't'); a.cry(mon); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
            return None, 0, 0xFFFF, 0
        return f
    def tm18(a, texts, lab, o):
        T(lab + 'a', 0x12, 0x4369); T(lab + 'f', 0x12, 0x43F0); T(lab + 'x', 0x12, 0x43BC)
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_tm18); a.iftrue(lab + 'e')
        a.writetext(lab + 'a'); a.promptbutton(); a.verbosegiveitem(PM.item_id('TM_COUNTER'), 1); a.iffalse(lab + 'n')
        a.setevent(got_tm18)
        a.label(lab + 'e'); a.writetext(lab + 'x'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'n'); a.writetext(lab + 'f'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    # the thirsty girl on the roof (Red: one TM per kind of drink)
    R = RM.R
    def g1(p): return P27.gen1_text(RM.fo(0x12, p), {('ram', ram): P27.lit(name) for ram, name in ((0xCF45, 'わざマシン'),)})
    def girl(a, texts, lab, o):
        T('rg_ask', 0x12, 0x4A9E); T('rg_cry', 0x12, 0x4A82); T('rg_full', 0x12, 0x49CF); T('rg_no', 0x12, 0x49DD)
        drinks = ((FRESH_WATER, got_tm13, 0x484A, 'TM_ICE_BEAM'), (SODA_POP, got_tm48, 0x48CE, 'TM_ROCK_SLIDE'),
                  (LEMONADE, got_tm49, 0x4950, 'TM_TRI_ATTACK'))
        recv = ((0x4881, 'わざマシン13'), (0x4904, 'わざマシン48'), (0x4986, 'わざマシン49'))
        for k, (it, fl, yay, tm) in enumerate(drinks):
            o_ = RM.fo(0x12, yay); e_ = o_
            while R[e_] != 0x50: e_ += 1
            texts['rg_y%d' % k] = bytes(R[o_:e_]) + b'\x57'
            # the explanation after "received" (Red: after the jingle): from the sound command on
            o_ = RM.fo(0x12, recv[k][0]); e_ = o_
            while not (R[e_] == 0x0B and R[e_ - 1] == 0x50): e_ += 1
            t_ = P27.gen1_text(e_ + 1, {('ram', 0xCF45): P27.lit(recv[k][1])})
            if t_[:3] == b'\x00\x51\x50': t_ = t_[3:]
            texts['rg_x%d' % k] = t_
        a.label(lab); a.faceplayer(); a.opentext()
        for it, fl, yay, tm in drinks: a.checkitem(it); a.iftrue(lab + 'h')
        a.writetext('rg_cry'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'h'); a.writetext('rg_ask'); a.yesorno(); a.iffalse('rg_e')
        a.db(0x4F); a.dw('rg_mh'); a.db(0x58); a.db(0x50)                       # loadmenu ; verticalmenu ; closewindow
        for k in range(3): a.ifequal(k + 1, 'rg_d%d' % k)
        a.label('rg_e'); a.closetext(); a.end()
        for k, (it, fl, yay, tm) in enumerate(drinks):
            a.label('rg_d%d' % k); a.checkitem(it); a.iffalse('rg_e'); a.checkevent(fl); a.iftrue('rg_nt')
            a.writetext('rg_y%d' % k); a.waitbutton(); a.db(0x20, it, 1)                                  # takeitem
            a.verbosegiveitem(PM.item_id(tm), 1); a.iffalse('rg_f'); a.setevent(fl)
            a.writetext('rg_x%d' % k); a.waitbutton(); a.closetext(); a.end()
        a.label('rg_nt'); a.writetext('rg_no'); a.waitbutton(); a.closetext(); a.end()
        a.label('rg_f'); a.writetext('rg_full'); a.waitbutton(); a.closetext(); a.end()
        a.label('rg_mh'); a.db(0x40, 2, 0, 11, 13); a.dw('rg_md'); a.db(1)
        a.label('rg_md'); a.db(0x80, 4); a.raw(b''.join(encode(s) for s in ('おいしいみず@', 'サイコソーダ@', 'ミックスオレ@', 'やめる@')))
        return None, 0, 0xFFFF, 0
    # the game designer: the diploma once 150 kinds (No. 1-151) are caught
    dex = P27.W_DEX_CAUGHT
    def designer(a, texts, lab, o):
        T(lab + 'a', 0x12, 0x4DD5)
        o_ = RM.fo(0x12, 0x4E1F); e_ = o_
        while R[e_] != 0x50: e_ += 1
        texts[lab + 'c'] = bytes(R[o_:e_]) + b'\x57'
        a.label(lab); a.faceplayer(); a.opentext(); callasm('count151'); a.db(0x0B, 150); a.dw(lab + 'n')     # ifless
        a.writetext(lab + 'c'); a.waitbutton(); a.closetext(); a.special(SPECIAL_DIPLOMA); a.end()
        a.label(lab + 'n'); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    def callasm(l_): a.db(0x0E, BANK); a.dw(l_)
    # count of caught kinds No. 1-151 -> wScriptVar (18 bytes, then the low 7 bits of the 19th)
    a.label('count151'); a.raw(bytes([0x21, dex & 0xFF, dex >> 8, 0x06, 18, 0x0E, 0x00,
                                      0x2A, 0x16, 0x08, 0xCB, 0x3F, 0x30, 0x01, 0x0C, 0x15, 0x20, 0xF8, 0x05, 0x20, 0xF2,
                                      0x7E, 0xE6, 0x7F, 0x16, 0x07, 0xCB, 0x3F, 0x30, 0x01, 0x0C, 0x15, 0x20, 0xF8,
                                      0x79, 0xEA, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0xC9]))
    def eevee(a, texts, lab, o):
        a.label(lab); a.opentext(); a.givepoke(EEVEE, 25); a.iffalse(lab + 'f'); a.closetext()
        a.disappear(o['_id']); a.setevent(eevee_gone); a.end()
        a.label(lab + 'f'); a.closetext(); a.end()
        return SPR['SPRITE_POKE_BALL'], 0, eevee_gone, 0
    vend = MapEvents(rom, 'CeladonDeptStore6F').bgs
    vend = [r for y, x, t, r in vend if x == 8][0]                      # Crystal's vending machine script
    a.label('vend'); a.farsjump(vend[1], vend[2])
    special = {'CeladonMart2F': {1: mart(23), 2: mart(24)}, 'CeladonMart3F': {1: tm18}, 'CeladonMart4F': {1: mart(26)},
               'CeladonMart5F': {3: mart(27), 4: mart(28)}, 'CeladonMartRoof': {2: girl},
               'CeladonMansion1F': {1: cry(0x80, 1, MEOWTH), 3: cry(0x80, 3, CLEFAIRY), 4: cry(0x80, 4, NIDORAN_F)},
               'CeladonMansion3F': {4: designer}, 'CeladonMansionRoofHouse': {2: eevee}}
    built = {}
    for n in NEW:
        objs = P25.red_objects(n)[0]
        sp_ = {}
        for tid, f in special.get(n, {}).items():
            objs[tid - 1]['_id'] = tid + 1
            sp_[tid] = (lambda f, o_: (lambda a_, t_, l_, o: f(a_, t_, l_, o_)))(f, objs[tid - 1])
        bsp = {}
        if n == 'CeladonMartRoof':                                       # the vending machines
            bsp = {k: (0, 'vend') for k, (x, y, tc) in enumerate(P25.red_objects(n)[2]) if 'VENDING' in tc}
        if n == 'CeladonMartElevator': bsp = {0: (0, 'elev')}
        ob, bgs = K.red_events(a, texts, n, RED_ID[n], n[7:] + '_', sp_, SPR, bsp)
        if n in ('CeladonMart1F', 'CeladonMart2F', 'CeladonMart3F', 'CeladonMart4F', 'CeladonMart5F'):
            pass
        built[n] = (ob, bgs)
    # the elevator (Red: 1F-5F)
    a.label('elev'); a.opentext(); a.elevator('elev_d'); a.closetext(); a.iffalse('end41')
    a.pause(5); a.playsound(SFX_ELEVATOR); a.earthquake(60); a.waitsfx(); a.end()
    a.label('elev_d'); a.db(5)
    for k, fl in enumerate(('1F', '2F', '3F', '4F', '5F')):
        n = 'CeladonMart' + fl
        wi = [i + 1 for i, (x, y, d, w_) in enumerate(P25.red_objects(n)[1]) if d == 'CELADON_MART_ELEVATOR'][0]
        a.db(FLOOR_1F + k, wi, *nid[n])
    a.db(0xFF)
    K.put_texts(a, texts)

    # warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    for n in NEW:
        ws = []
        for x, y, d, wi in P25.red_objects(n)[1]:
            if d == 'LAST_MAP': ws.append(W(x, y, wi, cel))
            elif n == 'CeladonMartElevator': ws.append(W(x, y, 0xFF, nid['CeladonMart1F']))
            else: ws.append(W(x, y, wi, nid[CONST[d]]))
        ob, bgs = built[n]
        K.emit(a, n, ws, [], bgs, ob, [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Celadon Dept. Store / Mansion: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    for i, n in enumerate(NEW):
        src = 'CeladonDeptStore1F' if n in MART else 'CeladonMansion1F'
        K.make_map(FIRST_MAP + i, nmp[n], tss[tk[n]][0], border_of(n), src, 3, a, n)

    # ================= the city's doors (phase 40: Crystal's buildings) -> Red's
    def fn(i, w_):
        if (w_[3], w_[4]) == mapid('CeladonDeptStore1F'): return (1 if w_[1] == 8 else 3, nid['CeladonMart1F'])
        if (w_[3], w_[4]) == mapid('CeladonDeptStore5F'): return (1, nid['CeladonMart5F'])
        if (w_[3], w_[4]) == mapid('CeladonMansion1F'): return (1 if w_[0] == 9 else 3, nid['CeladonMansion1F'])
    assert K.fix_warps('CeladonCity', fn) == 6

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
