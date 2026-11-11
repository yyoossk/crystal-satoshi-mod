#!/usr/bin/env python3
"""Phase 29: Viridian City as in Red / the Pikachu full-color hack, for good, with Oak's parcel:
 * Red's town (Gen I overworld tileset) in place of Crystal's: Red's people and signs, the hidden Potion; the drunk
   old man lying on the road north (until the Pokédex) who sends the player back, then his catching demonstration
   (Weedle, with Red's old man in the battle), the girl, the TM42 (Dream Eater) man, the gym locked until the other
   seven Kanto badges.  Route 2 (Red) is joined directly, Routes 1 and 22 (Crystal's) show their edges drawn with the
   other tileset (blockxlat).  Crystal's Pokémon Center, house and gym are used for those doors.
 * Red's Viridian Mart: the clerk hands over Oak's parcel (new key item) the first time; no shopping until the parcel
   is delivered; Red's goods afterwards.  Red's school house (the notebook, the blackboard menu).
 * Oak's lab (before the Kanto Hall of Fame): the parcel is delivered, Shigeru comes in, both get the Pokédex
   (it is no longer handed out right after the starter); later Oak's Poké Balls, his lines and the Pokédex rating.
usage: build_phase29.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import blockxlat as X
import redmap as RM
import redtexts as RT
from evedit import MapEvents
import build_phase10 as P10
import build_phase12 as P12
import build_phase14 as P14
import build_phase15 as P15
import build_phase17 as P17
import build_phase24 as P24
import build_phase25 as P25
import build_phase26 as P26
import build_phase27 as P27
import build_phase28 as P28

P15.TS_CAP = P27.TS_CAP
FIRST_FLAG = 256                   # 240-255: phase 28
FIRST_MAP = 97                     # 26:87-96 = phase 28
BANK, BANK2 = 0x6F, 0x70           # free in the JP original
OVERWORLD_TS, HOUSE_TS = 40, 44
RED_VIRIDIAN, RED_LAB, RED_MART, RED_SCHOOL = 0x01, 0x28, 0x2A, 0x2B
PARCEL = 0x99                      # unused item slot -> key item とどけもの
EV_HOF, EV_GOT_STARTER = 0x34A, 0x342
ENGINE_POKEDEX = 0x0B
KANTO_BADGES = list(range(0x23, 0x2A))     # Boulder .. Volcano (engine flags)
ENGINE_EARTH = 0x2A
LAB_DONE = P15.EXT_FLAGS[60]       # phase 17: the lab battle is over (Shigeru hidden)
R22_FIRST = P15.EXT_FLAGS[63]      # phase 17: Route 22, first battle won
MART_VIRIDIAN = 18
POKE_BALL = 0x05
MUS_RIVAL = 0x1F
SPECIAL_DEX_RATING = 0x65          # ProfOaksPCBoot (US 0x66)
VAR_DEXCAUGHT = 0x05
VAR_X, VAR_Y = P26.VAR_X, P26.VAR_Y
BT_TUTORIAL = 3
W_MAP_GROUP, W_MAP_NUMBER, W_BATTLE_TYPE = 0xDC7B, 0xDC7C, 0xD261
SPAWN_TABLE = P26.SPAWN_TABLE
GAMBLER_ASLEEP_SPRITE = 0x13C50    # PKFC GamblerAsleepSprite (4 tiles)
OAK_TALK = (0x62, 0x4DE6)          # Oak's object script in the lab: farsjump to the base mod's (1F:7FA0 -> 78:5D38)
OAK_BASE_POST, OAK_BASE_PRE = (0x78, 0x5D38), (0x78, 0x4462)
BACKPIC = 0x3FC1C                  # 0F:7C1C  ld a,[wBattleType] / cp BATTLETYPE_TUTORIAL / jr z,.Decompress
BACKPIC_STUB = (0x3FFB8, 0x3FFE0)  # 0F:7FB8-7FDF free (between phase 28's hook and its helper)
DUDE_NAME = 0x4E3A2                # 13:63A2  ld hl, .Dude (CatchTutorial)
U, D, L, R_ = 0x0D, 0x0C, 0x0E, 0x0F
TU, TD, TL, TR = 1, 0, 2, 3
SPR = dict(P28.SPR)
# Red's warps: (x, y, map, warp id in it); None = Crystal's map (its warp back is re-pointed)
TOWN_WARPS = [(23, 25, 'ViridianPokecenter1F', None), (29, 19, 'ViridianMart', 1), (21, 15, 'ViridianSchoolHouse', 1),
              (21, 9, 'ViridianNicknameSpeechHouse', None), (32, 7, 'ViridianGym', None)]
NEIGHBOURS = ['Route1', 'Route22']
MAPS = [('ViridianMart', RED_MART), ('ViridianSchoolHouse', RED_SCHOOL)]


def riv(b): return bytes(b).replace(b'\x53', encode('シゲル').rstrip(b'\x50'))


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x05, 0x0B, BANK, BANK2):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    f, n = bank_free_tail(rom, 0x13); assert n > 40; sp.set_area(0x13, f + 1, 0x13 * 0x4000 + 0x4000)
    assert not any(rom[BACKPIC_STUB[0] - 1:BACKPIC_STUB[1]]); sp.set_area(0x0F, *BACKPIC_STUB)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    vir = mapid('ViridianCity'); r2 = mapid('Route2')
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g) in enumerate(MAPS)}
    TS = PM.Tilesets(rom, sp)
    got_parcel, got_tm42, got_balls = FL.new(), FL.new(), FL.new()
    asleep_hide, awake_hide = FL.new(), FL.new()

    def hl(mapid_, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid_, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    def rt(mapid_, tid):
        b, p = RM.text_ptr(mapid_, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return hl(mapid_, tid)[0]
    def jp(o): return P28.jp(o)

    # ================= the sleeping old man's sprite (one more entry in phase 14's second table)
    stubs = []
    for off, d in P14.OW_READERS:
        assert rom[off] == 0xCD; s_ = fo(0x05, r16(off + 1))
        assert rom[s_:s_ + 2] == bytes([0xFE, 0x67]) and rom[s_ + 8] == 0x21
        stubs.append((s_, d))
    virt = r16(stubs[0][0] + 9) - stubs[0][1]
    t2 = virt + 0x66 * 6; n2 = len(P14.NEW_SPRITES) + 2                   # + Old Amber (26), Safari worker (28)
    tab = bytes(rom[fo(0x05, t2):fo(0x05, t2) + 6 * n2])
    pk = open(P10.PKFC, 'rb').read()
    ga = sp.put(BANK2, pk[GAMBLER_ASLEEP_SPRITE:GAMBLER_ASLEEP_SPRITE + 4 * 16])
    tab += bytes([ga & 0xFF, ga >> 8, 0x40, BANK2, 3, 3])
    nt = sp.put(0x05, tab); nv = nt - 0x66 * 6
    for s_, d in stubs: w16(s_ + 9, nv + d)
    SPR['SPRITE_GAMBLER_ASLEEP'] = 0x67 + n2
    log.append('sleeping old man sprite -> id %02X' % SPR['SPRITE_GAMBLER_ASLEEP'])

    # ================= Oak's parcel (key item)
    nb = rom[P12.ITEMNAMES_PTR]; o = fo(nb, r16(P12.ITEMNAMES_PTR + 1)); names = []
    for i in range(256):
        e_ = rom.index(0x50, o); names.append(bytes(rom[o:e_ + 1])); o = e_ + 1
    assert names[PARCEL - 1] == names[0x9A - 1], names[PARCEL - 1]          # an unused slot ("?")
    names[PARCEL - 1] = encode('とどけもの@')
    an = sp.put(BANK, b''.join(names)); rom[P12.ITEMNAMES_PTR] = BANK; w16(P12.ITEMNAMES_PTR + 1, an)
    rom[P12.ITEMATTR + 7 * (PARCEL - 1):P12.ITEMATTR + 7 * PARCEL] = rom[P12.ITEMATTR + 7 * (P25.SECRET_KEY - 1):][:7]
    w16(P12.ITEMDESC + 2 * (PARCEL - 1), sp.put(0x0B, encode('オーキド　はかせに<NEXT>とどける　にもつ@')))

    # ================= the Viridian Mart's goods: Red's (Crystal's own Viridian Mart is no longer reachable)
    ids = [P15.item_id(n) for n in ('ULTRA_BALL', 'HYPER_POTION', 'FULL_HEAL', 'REVIVE', 'ANTIDOTE', 'PARLYZ_HEAL',
                                    'AWAKENING', 'BURN_HEAL')]
    mo = rom.find(bytes([9] + ids)); assert mo > 0 and rom.find(bytes([9] + ids), mo + 1) < 0
    red = [P15.item_id(n) for n in ('POKE_BALL', 'ANTIDOTE', 'PARLYZ_HEAL', 'BURN_HEAL')]
    rom[mo:mo + 11] = bytes([len(red)] + red + [0xFF]) + bytes(11 - len(red) - 2)

    # ================= the catching demonstration: Red's old man (name and back picture) in Viridian City
    from PIL import Image
    im = Image.open(PR + '/gfx/battle/oldmanb.png').convert('L')
    assert im.size == (32, 32)
    big = im.resize((48, 48), Image.NEAREST); px = big.load(); data = bytearray()
    for tx in range(6):
        for ty in range(6):
            for r in range(8):
                lo_ = hi_ = 0
                for c in range(8):
                    v = 3 - px[8 * tx + c, 8 * ty + r] // 85
                    lo_ |= (v & 1) << (7 - c); hi_ |= (v >> 1) << (7 - c)
                data += bytes([lo_, hi_])
    pic = sp.put(BANK2, lz(bytes(data)))
    g, m = vir
    assert rom[BACKPIC:BACKPIC + 7] == bytes([0xFA, 0x61, 0xD2, 0xFE, BT_TUTORIAL, 0x28, 0x1A])
    st = bytes([0xFA, 0x61, 0xD2, 0xFE, BT_TUTORIAL, 0xC0,                                   # ret nz (not the demo)
                0xFA, W_MAP_GROUP & 0xFF, W_MAP_GROUP >> 8, 0xFE, g, 0x20, 0x0C,
                0xFA, W_MAP_NUMBER & 0xFF, W_MAP_NUMBER >> 8, 0xFE, m, 0x20, 0x05,
                0x06, BANK2, 0x21, pic & 0xFF, pic >> 8, 0xAF, 0xC9])                        # .z: xor a / ret
    sa = sp.put(0x0F, st)
    rom[BACKPIC:BACKPIC + 7] = bytes([0xCD, sa & 0xFF, sa >> 8, 0x28, 0x1C, 0x00, 0x00])
    assert rom[DUDE_NAME:DUDE_NAME + 3] == bytes([0x21, 0x06, 0x64])
    nm = sp.put(0x13, encode('おじいさん@'))
    ns = sp.put(0x13, bytes([0xFA, W_MAP_GROUP & 0xFF, W_MAP_GROUP >> 8, 0xFE, g, 0x20, 0x0B,
                             0xFA, W_MAP_NUMBER & 0xFF, W_MAP_NUMBER >> 8, 0xFE, m, 0x20, 0x04,
                             0x21, nm & 0xFF, nm >> 8, 0xC9, 0x21, 0x06, 0x64, 0xC9]))
    rom[DUDE_NAME:DUDE_NAME + 3] = bytes([0xCD, ns & 0xFF, ns >> 8])

    # ================= tilesets: Overworld / House variant blocks for the warps
    ow = Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)
    house = Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl')
    town = MapPort('ViridianCity', ow, 20, 18, 'ViridianCity.blk')
    school = MapPort('ViridianSchoolHouse', house, 4, 4, 'ViridianSchoolHouse.blk')
    objs_school = P25.red_objects('ViridianSchoolHouse')
    for ts, tid, mm, ov in ((ow, OVERWORLD_TS, {'ViridianCity': town},
                             {'ViridianCity': {(x, y): P25.warp_override(ow, town, x, y) for x, y, d, w in TOWN_WARPS}}),
                            (house, HOUSE_TS, {'ViridianSchoolHouse': school},
                             {'ViridianSchoolHouse': {(x, y): P25.warp_override(house, school, x, y)
                                                      for x, y, d, w in objs_school[1]}})):
        e = TS.entry(tid); am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
        assert e[3] == e[6] and ac_ > am_
        nb0 = (ac_ - am_) // 16
        meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytes(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
        assert meta[:16 * ts.nblocks] == bytes(ts.blocks)
        ts.coll = bytearray(coll[:4 * ts.nblocks])                    # Cut trees (phase 27) included
        meta2, coll2, blks = pairwalls.variants(ts, meta, coll, mm, [], ov)
        meta2, coll2, blks = P27.block0_copy(meta2, coll2, blks)
        assert len(coll2) // 4 <= 256
        am = sp.put(BANK2, meta2 + coll2); t0 = TS.tab + 15 * tid
        rom[t0 + 3] = BANK2; w16(t0 + 4, am); rom[t0 + 6] = BANK2; w16(t0 + 7, am + len(meta2))
        for n in mm: mm[n].blk = blks[n]
        log.append('tileset %s: %d blocks (+%d)' % (ts.name, len(coll2) // 4, len(coll2) // 4 - nb0))

    # ================= headers 26:97-98 (move what lies there)
    u = US.get(); G = u.groups()
    lo, hi = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1), GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1 + len(MAPS))
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            if not rom[hdr]: continue
            ab = rom[hdr]; ap = r16(hdr + 3); ao_ = fo(ab, ap)
            nconn = bin(rom[ao_ + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao_ < hi and ao_ + size > lo:
                rom[hdr] = BANK; w16(hdr + 3, sp.put(BANK, bytes(rom[ao_:ao_ + size])))
                log.append('moved map attributes %X:%04X' % (ab, ap))
    rom[lo:hi] = bytes(hi - lo)
    hcity = hdr_index('ViridianCity')

    # ================= the mart (Red's layout = Cinnabar Mart's, phase 19: its blocks and tileset)
    hcm = GROUP26_END + 9 * (52 - G26_COUNT - 1)
    acm = attrs(rom, hcm); assert (acm['w'], acm['h']) == (4, 4)
    mart_blk = bytes(rom[fo(acm['blkbank'], acm['blk']):fo(acm['blkbank'], acm['blk']) + 16])
    # Red: the clerk is talked to over the counter (Mart / Pokecenter tileset counter tiles $18, $19, $1E)
    e = TS.entry(rom[hcm + 1]); am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8; nbm = (ac_ - am_) // 16
    mo_, co_ = fo(e[3], am_), fo(e[6], ac_); nc = 0
    for b_ in range(nbm):
        for q in range(4):
            r_, c_ = ((1, 0), (1, 2), (3, 0), (3, 2))[q]
            if rom[mo_ + 16 * b_ + 4 * r_ + c_] in (0x18, 0x19, 0x1E) and rom[co_ + 4 * b_ + q] != 0x90:
                rom[co_ + 4 * b_ + q] = 0x90; nc += 1                                        # COLL_COUNTER
    log.append('mart tileset %d: %d counter quarters' % (rom[hcm + 1], nc))
    objs, warps, bgl = P25.red_objects('ViridianMart')
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}; obj_bytes = []
    a.label('end'); a.end()
    for idx, o in enumerate(objs):
        tid = idx + 1; lab = 'o%d' % tid
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        if tid == 1:
            a.label(lab); a.faceplayer(); a.opentext(); a.checkflag(ENGINE_POKEDEX); a.iftrue(lab + 'm')
            a.writetext(lab + 'h'); a.waitbutton(); a.closetext(); a.end()
            a.label(lab + 'm'); a.db(0x93, 0x00); a.dw(MART_VIRIDIAN); a.closetext(); a.end()          # pokemart
            texts[lab + 'h'] = rt(RED_MART, 1)
        else:
            a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(RED_MART, tid)
        obj_bytes.append([SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, 0xFFFF])
    # Red: coming in for the first time, the clerk calls the player to the counter and hands over the parcel
    a.label('sc'); a.checkevent(got_parcel); a.iftrue('end'); a.checkflag(ENGINE_POKEDEX); a.iftrue('end')
    a.opentext(); a.writetext('pq'); a.waitbutton(); a.closetext()
    a.applymovement(0, 'mv_counter'); a.turnobject(0, TL)
    a.opentext(); a.writetext('pg'); a.db(0x1F, PARCEL, 1); a.setevent(got_parcel)               # giveitem
    a.waitbutton(); a.closetext(); a.end()
    a.label('mv_counter'); a.db(L, U, U, 0x47)
    texts['pq'] = rt(RED_MART, 4); texts['pg'] = rt(RED_MART, 5)
    for k_, v in texts.items():
        assert k_ not in a.labels, k_
        a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
    a.label('mapscripts'); a.db(1); a.dw('sc'); a.dw(0); a.db(0)
    a.label('events'); a.db(0, 0)
    a.db(len(warps))
    for x, y, dest, wid in warps: assert dest == 'LAST_MAP'; a.db(y, x, wid, *vir)
    a.db(0); a.db(0)
    a.db(len(obj_bytes))
    for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    blkp = sp.put(BANK, mart_blk)
    aa = sp.put(BANK, bytes([rom[acm['attr_off']], 4, 4, BANK, blkp & 0xFF, blkp >> 8, BANK,
                             a.labels['mapscripts'] & 0xFF, a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF,
                             a.labels['events'] >> 8, 0]))
    hh = GROUP26_END + 9 * (mapids['ViridianMart'][1] - G26_COUNT - 1)
    rom[hh:hh + 9] = bytes([BANK, rom[hcm + 1], rom[hcm + 2], aa & 0xFF, aa >> 8, rom[hcity + 5]]) + rom[hcm + 6:hcm + 9]
    log.append('ViridianMart -> map %d:%d  scripts %X:%04X (%d bytes)' % (*mapids['ViridianMart'], BANK, base, len(blob)))

    # ================= the school house
    objs, warps, bgl = objs_school
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}; obj_bytes = []; bgs = []
    for idx, o in enumerate(objs):
        tid = idx + 1; lab = 'o%d' % tid
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(RED_SCHOOL, tid)
        obj_bytes.append([SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, 0xFFFF])
    # the notebook (Red: ViridianSchoolNotebook)
    pages = [0x53E45, 0x53E93, 0x53EDB, 0x53F33]
    texts.update({'nb%d' % i: jp(o_) for i, o_ in enumerate(pages)})
    texts['nbturn'] = jp(0x53E1B); texts['nbgirl'] = jp(0x53E2C)
    a.label('nb'); a.opentext()
    for i in range(4):
        a.writetext('nb%d' % i)
        if i < 3: a.writetext('nbturn'); a.yesorno(); a.iffalse('nbx')
    a.writetext('nbgirl'); a.waitbutton()
    a.label('nbx'); a.closetext(); a.end()
    # the blackboard (Red: ViridianSchoolBlackboard; two columns: SLP PSN PAR / BRN FRZ QUIT)
    texts['bbi'] = jp(0x5FC12); texts['bbq'] = jp(0x5FC40)
    order = [('slp', 0x5FC77), ('brn', 0x5FD2E), ('psn', 0x5FCB3), ('frz', 0x5FD81), ('par', 0x5FCEF)]
    for k_, o_ in order: texts['bb' + k_] = jp(o_)
    a.label('bb'); a.opentext(); a.writetext('bbi')
    a.label('bbl'); a.writetext('bbq')
    a.db(0x4F); a.dw('bbmh'); a.db(0x57); a.db(0x50)                        # loadmenu ; _2dmenu ; closewindow
    for i, (k_, o_) in enumerate(order): a.ifequal(i + 1, 'bbs' + k_)
    a.closetext(); a.end()
    for k_, o_ in order: a.label('bbs' + k_); a.writetext('bb' + k_); a.sjump('bbl')
    a.label('bbmh'); a.db(0x40, 0, 0, 6, 11); a.dw('bbmd'); a.db(1)
    a.label('bbmd'); a.db(0xC0, 0x32, 5, BANK); a.dw('bbmt'); a.db(BANK); a.dw(0)            # 3 rows x 2 columns
    a.label('bbmt'); a.raw(b''.join(encode(s) for s in ('ねむり@', 'やけど@', 'どく@', 'こおり@', 'マヒ@', 'やめる@')))
    bgs += [(4, 3, 0, 'nb'), (0, 3, 1, 'bb')]          # Red's hidden texts: notebook (3,4), blackboard (3,0)
    for k_, v in texts.items():
        assert k_ not in a.labels, k_
        a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
    a.label('mapscripts'); a.db(0, 0)
    a.label('events'); a.db(0, 0)
    a.db(len(warps))
    for x, y, dest, wid in warps: assert dest == 'LAST_MAP'; a.db(y, x, wid, *vir)
    a.db(0)
    a.db(len(bgs))
    for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
    a.db(len(obj_bytes))
    for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    blkp = sp.put(BANK, school.blk)
    aa = sp.put(BANK, bytes([border_of('ViridianSchoolHouse'), 4, 4, BANK, blkp & 0xFF, blkp >> 8, BANK,
                             a.labels['mapscripts'] & 0xFF, a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF,
                             a.labels['events'] >> 8, 0]))
    hs = hdr_index('ViridianNicknameSpeechHouse')
    hh = GROUP26_END + 9 * (mapids['ViridianSchoolHouse'][1] - G26_COUNT - 1)
    rom[hh:hh + 9] = bytes([BANK, HOUSE_TS, 3, aa & 0xFF, aa >> 8, rom[hcity + 5]]) + rom[hs + 6:hs + 9]
    log.append('ViridianSchoolHouse -> map %d:%d  scripts %X:%04X (%d bytes)' % (*mapids['ViridianSchoolHouse'], BANK,
                                                                             base, len(blob)))

    # ================= Viridian City
    me = MapEvents(rom, 'ViridianCity')
    old_warps = list(me.warps)
    objs, warps_red, bgl = P25.red_objects('ViridianCity')
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    me.objs = []; me.bgs = []; me.coords = []
    a.label('end'); a.end()
    flag_of = {5: asleep_hide, 7: awake_hide}
    for idx, o in enumerate(objs):
        tid = idx + 1; L_ = 'p%d' % tid
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        fl = flag_of.get(tid, 0xFFFF)
        me.objs.append([bytearray([SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, 0, 0,
                                   fl & 0xFF, fl >> 8]), L_])
    assert objs[4]['sprite'] == 'SPRITE_GAMBLER_ASLEEP' and objs[6]['sprite'] == 'SPRITE_GAMBLER'
    a.label('p1'); a.jumptextfaceplayer('p1t'); texts['p1t'] = rt(RED_VIRIDIAN, 1)
    # the man by the gym: "the leader is back" once the other seven badges are there
    back, closed = hl(RED_VIRIDIAN, 2)[:2]
    texts.update(p2b=back, p2c=closed)
    a.label('p2'); a.faceplayer(); a.opentext(); a.checkflag(ENGINE_EARTH); a.iftrue('p2y')
    for f_ in KANTO_BADGES: a.checkflag(f_); a.iffalse('p2n')
    a.label('p2y'); a.writetext('p2b'); a.waitbutton(); a.closetext(); a.end()
    a.label('p2n'); a.writetext('p2c'); a.waitbutton(); a.closetext(); a.end()
    # Caterpie and Weedle
    q, yes, no = hl(RED_VIRIDIAN, 3)[:3]
    texts.update(p3q=q, p3y=yes, p3n=no)
    a.label('p3'); a.faceplayer(); a.opentext(); a.writetext('p3q'); a.yesorno(); a.iffalse('p3x')
    a.writetext('p3y'); a.waitbutton(); a.closetext(); a.end()
    a.label('p3x'); a.writetext('p3n'); a.waitbutton(); a.closetext(); a.end()
    # the girl
    coffee, shop = hl(RED_VIRIDIAN, 4)[:2]
    texts.update(p4a=coffee, p4b=shop)
    a.label('p4'); a.faceplayer(); a.opentext(); a.checkflag(ENGINE_POKEDEX); a.iftrue('p4y')
    a.writetext('p4a'); a.waitbutton(); a.closetext(); a.end()
    a.label('p4y'); a.writetext('p4b'); a.waitbutton(); a.closetext(); a.end()
    # the drunk old man on the road: private property, the player is sent back
    texts['p5t'] = hl(RED_VIRIDIAN, 5)[0]
    a.label('p5'); a.opentext(); a.writetext('p5t'); a.waitbutton(); a.closetext()
    a.applymovement(0, 'mv_d'); a.end()
    a.label('mv_d'); a.db(D, 0x47)
    a.label('om'); a.checkflag(ENGINE_POKEDEX); a.iftrue('end'); a.sjump('p5')
    me.coords.append((0xFF, 9, 19, 'om'))
    # TM42 Dream Eater
    texts.update(p6g=RM.crystal_text(6, 0x5437), p6f=RM.crystal_text(6, 0x54D6), p6x=RM.crystal_text(6, 0x54BB))
    a.label('p6'); a.faceplayer(); a.opentext(); a.checkevent(got_tm42); a.iftrue('p6e')
    a.writetext('p6g'); a.verbosegiveitem(P12.tm_item(42), 1); a.iffalse('p6z'); a.setevent(got_tm42)
    a.closetext(); a.end()
    a.label('p6z'); a.writetext('p6f'); a.waitbutton(); a.closetext(); a.end()
    a.label('p6e'); a.writetext('p6x'); a.waitbutton(); a.closetext(); a.end()
    # the old man, awake: in a hurry?  no -> the catching demonstration (Weedle)
    hurry, lesson, money = hl(RED_VIRIDIAN, 7)[:3]
    texts.update(p7q=hurry, p7l=lesson, p7m=money, p7w=rt(RED_VIRIDIAN, 15))
    a.label('p7'); a.faceplayer(); a.opentext(); a.writetext('p7q'); a.yesorno(); a.iffalse('p7d')
    a.writetext('p7m'); a.waitbutton(); a.closetext(); a.end()
    a.label('p7d'); a.writetext('p7l'); a.waitbutton(); a.closetext()
    a.loadwildmon(PM.MON['WEEDLE'], 5); a.db(0x60, BT_TUTORIAL)                     # catchtutorial
    a.opentext(); a.writetext('p7w'); a.waitbutton(); a.closetext(); a.end()
    # the gym: locked until the other seven badges
    texts['glt'] = rt(RED_VIRIDIAN, 14)
    a.label('gl'); a.checkflag(ENGINE_EARTH); a.iftrue('end')
    for f_ in KANTO_BADGES: a.checkflag(f_); a.iffalse('gl_x')
    a.end()
    a.label('gl_x'); a.opentext(); a.writetext('glt'); a.waitbutton(); a.closetext(); a.applymovement(0, 'mv_hop'); a.end()
    a.label('mv_hop'); a.db(0x30, 0x47)                                 # jump_step DOWN (the ledge below)
    me.coords.append((0xFF, 8, 32, 'gl'))
    # signs, the hidden Potion
    nobj = len(objs)
    for k, (x, y, tconst) in enumerate(bgl):
        L_ = 'vs%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(RED_VIRIDIAN, nobj + 1 + k)
        me.bgs.append((y, x, 0, L_))
    for k, (x, y, fn, arg) in enumerate(P25.hidden('VIRIDIAN_CITY')):
        assert fn == 'HiddenItems'
        me.bgs.append((y, x, 7, ('data', bytes([*FL.new().to_bytes(2, 'little'), PM.item_id(arg)]))))
    # the old man: lying until the Pokédex, awake afterwards
    a.label('vc_cb'); a.checkflag(ENGINE_POKEDEX); a.iftrue('vc_cbd')
    a.setevent(awake_hide); a.clearevent(asleep_hide); a.endcallback()
    a.label('vc_cbd'); a.setevent(asleep_hide); a.clearevent(awake_hide); a.endcallback()
    me.callbacks.append((2, 'vc_cb'))
    dest_of = {(w[3], w[4]): w[2] for w in old_warps}
    me.warps = []
    for x, y, dn, wid in TOWN_WARPS:
        if wid is None: d = mapid(dn); me.warps.append(bytes([y, x, dest_of[d], *d]))
        else: me.warps.append(bytes([y, x, wid, *mapids[dn]]))
    assert [(x, y) for x, y, *_ in TOWN_WARPS] == [(x, y) for x, y, *_ in warps_red]
    for k_, v in texts.items():
        assert k_ not in a.labels, k_
        a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('ViridianCity: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= Red's blocks; the neighbours' edges translated, Route 2 joined directly
    ca = attrs(rom, hcity); ao = ca['attr_off']; assert (ca['w'], ca['h']) == (20, 18)
    old_city = ca['blk']; assert ca['blkbank'] == P27.BANK
    rom[hcity + 1] = OVERWORLD_TS
    vblk = sp.put(BANK, town.blk)
    rom[ao] = border_of('ViridianCity'); rom[ao + 3] = BANK; w16(ao + 4, vblk)
    e = TS.entry(OVERWORLD_TS); co = fo(e[6], e[7] | e[8] << 8)
    g1side = X.gen1_side(ow, bytes(rom[co:co + 4 * 128])); crside = X.crystal_side(rom, TS)
    xcity = sp.put(BANK, X.translate(MapPort('ViridianCity', ow, 20, 18, 'ViridianCity.blk').blk, g1side, crside))
    allhdr = [G[gi] + 9 * k for gi in range(26) for k in range((G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP + len(MAPS) - 1)]
    allhdr = [h_ for h_ in allhdr if rom[h_] and attrs(rom, h_)['scbank']]
    def conns(hdr):
        a_ = attrs(rom, hdr); o2 = a_['attr_off']
        return [o2 + 12 + 12 * k for k in range(bin(a_['conn'] & 0xF).count('1'))]
    xls = {}
    for nn in NEIGHBOURS:
        na_ = attrs(rom, hdr_index(nn)); size = na_['w'] * na_['h']; ob, oa = na_['blkbank'], na_['blk']
        blk = bytes(rom[fo(ob, oa):fo(ob, oa) + size])
        nbp = sp.put(BANK2, blk); xl = sp.put(BANK2, X.translate(blk, crside, g1side))
        rom[na_['attr_off'] + 3] = BANK2; w16(na_['attr_off'] + 4, nbp)
        tgt = mapid(nn)
        for hdr in allhdr:
            for c in conns(hdr):
                if (rom[c], rom[c + 1]) == tgt:
                    s_ = r16(c + 2); assert oa <= s_ < oa + size, (nn, hex(hdr))
                    w16(c + 2, (xl if hdr == hcity else nbp) + s_ - oa)
        n_ = 0
        for c in conns(hdr_index(nn)):
            if (rom[c], rom[c + 1]) == vir:
                s_ = r16(c + 2); assert old_city <= s_ < old_city + 360; w16(c + 2, xcity + s_ - old_city); n_ += 1
        assert n_ == 1, nn
        xls[nn] = xl
    # Crystal's Route 1 has its road one block further west than Red's: the two are joined one block apart
    hr1 = hdr_index('Route1'); r1 = mapid('Route1'); a1 = attrs(rom, hr1); assert (a1['w'], a1['h']) == (10, 18)
    n_ = 0
    for c in conns(hr1):
        if (rom[c], rom[c + 1]) == vir: rom[c:c + 12] = P24.connection('north', 10, 18, vir, 20, 18, -6, xcity); n_ += 1
    for c in conns(hcity):
        if (rom[c], rom[c + 1]) == r1: rom[c:c + 12] = P24.connection('south', 20, 18, r1, 10, 18, 6, xls['Route1']); n_ += 1
    assert n_ == 2
    hr2 = hdr_index('Route2'); ar2 = attrs(rom, hr2); assert (ar2['w'], ar2['h'], ar2['blkbank']) == (10, 36, P27.BANK)
    n_ = 0
    for c in conns(hr2):
        if (rom[c], rom[c + 1]) == vir: rom[c:c + 12] = P24.connection('south', 10, 36, vir, 20, 18, -5, vblk); n_ += 1
    for c in conns(hcity):
        if (rom[c], rom[c + 1]) == r2: rom[c:c + 12] = P24.connection('north', 20, 18, r2, 10, 36, 5, ar2['blk']); n_ += 1
    assert n_ == 2
    for i, (x, y, dn, wid) in enumerate(TOWN_WARPS):
        if wid is not None: continue
        a_ = attrs(rom, hdr_index(dn)); ev = parse_events(rom, a_['scbank'], a_['events']); n_ = 0
        for o_, w in ev['warps']:
            if (w[3], w[4]) == vir: rom[o_ + 2] = i + 1; n_ += 1
        assert n_, dn
    sp_i = [i for i in range(40) if (rom[SPAWN_TABLE + 4 * i], rom[SPAWN_TABLE + 4 * i + 1]) == vir]
    assert len(sp_i) == 1
    rom[SPAWN_TABLE + 4 * sp_i[0] + 2:SPAWN_TABLE + 4 * sp_i[0] + 4] = bytes([23, 26])

    # ================= Oak's lab (before the Hall of Fame): the parcel and the Pokédex
    lab = MapEvents(rom, 'OaksLab')
    rv_i = [i for i, (o_, r) in enumerate(lab.objs) if o_[0] == P17.SPR_BLUE]; assert len(rv_i) == 1
    ro = lab.objs[rv_i[0]][0]; assert ro[11] | ro[12] << 8 == LAB_DONE
    rv = rv_i[0] + 2; OAK = 2
    assert lab.objs[0][0][0] == 0x05 and (lab.objs[0][0][2] - 4, lab.objs[0][0][1] - 4) == (4, 2)
    t5 = hl(RED_LAB, 5, n=400, stop=False)
    T5 = {k: riv(t5[i]) for i, k in enumerate(('rate', 'which', 'fight', 'raise', 'deliver', 'world', 'balls', 'come'))}
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('oak'); a.checkevent(EV_HOF); a.iftrue('oak_post')
    a.checkevent(EV_GOT_STARTER); a.iffalse('oak_pre')
    a.faceplayer(); a.opentext(); a.checkflag(ENGINE_POKEDEX); a.iftrue('ok_dex')
    a.checkevent(LAB_DONE); a.iffalse('ok_fight')
    a.checkitem(PARCEL); a.iftrue('ok_parcel')
    a.writetext('raise'); a.waitbutton(); a.closetext(); a.end()
    a.label('ok_fight'); a.writetext('fight'); a.waitbutton(); a.closetext(); a.end()
    a.label('ok_dex'); a.checkevent(got_balls); a.iftrue('ok_rate')
    a.db(0x1C, VAR_DEXCAUGHT); a.db(0x0B, 2); a.dw('ok_chk')                  # readvar ; ifless 2
    a.sjump('ok_rate')
    a.label('ok_chk'); a.checkitem(POKE_BALL); a.iftrue('ok_come')
    a.checkevent(R22_FIRST); a.iftrue('ok_balls')
    a.writetext('world'); a.waitbutton(); a.closetext(); a.end()
    a.label('ok_balls'); a.db(0x1F, POKE_BALL, 5); a.setevent(got_balls)                       # giveitem
    a.writetext('balls'); a.waitbutton(); a.closetext(); a.end()
    a.label('ok_come'); a.writetext('come'); a.waitbutton(); a.closetext(); a.end()
    a.label('ok_rate'); a.writetext('rate'); a.special(SPECIAL_DEX_RATING); a.closetext(); a.end()
    # the parcel: Shigeru comes in, both get the Pokédex
    a.label('ok_parcel'); a.writetext('deliver'); a.waitbutton(); a.db(0x20, PARCEL, 1); a.closetext()   # takeitem
    a.playmusic(MUS_RIVAL); a.opentext(); a.writetext('gramps'); a.waitbutton(); a.closetext()
    a.db(0x1C, VAR_X); a.ifnotequal(4, 'ok_side'); a.db(0x1C, VAR_Y); a.ifnotequal(3, 'ok_side')
    a.moveobject(rv, 5, 7); a.appear(rv); a.applymovement(rv, 'mv_up4'); a.turnobject(rv, TU); a.sjump('ok_talk')
    a.label('ok_side'); a.moveobject(rv, 4, 7); a.appear(rv); a.applymovement(rv, 'mv_up4'); a.turnobject(rv, TU)
    a.label('ok_talk'); a.playmapmusic(); a.turnobject(OAK, TD)
    a.opentext(); a.writetext('what'); a.waitbutton(); a.writetext('request'); a.waitbutton()
    a.writetext('invent'); a.waitbutton(); a.writetext('gotdex'); a.waitbutton(); a.setflag(ENGINE_POKEDEX)
    a.writetext('dream'); a.waitbutton(); a.closetext()
    a.db(0x1C, VAR_X); a.ifnotequal(4, 'ok_up'); a.db(0x1C, VAR_Y); a.ifnotequal(3, 'ok_up')
    a.turnobject(rv, TL); a.sjump('ok_leave')
    a.label('ok_up'); a.turnobject(rv, TU)
    a.label('ok_leave'); a.opentext(); a.writetext('leave'); a.waitbutton(); a.closetext()
    a.playmusic(MUS_RIVAL); a.applymovement(rv, 'mv_dn8'); a.disappear(rv); a.playmapmusic(); a.end()
    a.label('mv_up4'); a.db(*([U] * 4), 0x47)   # (he appears at the edge of the screen)
    a.label('mv_dn8'); a.db(*([D] * 8), 0x47)
    a.label('oak_post'); a.farsjump(*OAK_BASE_POST)
    a.label('oak_pre'); a.farsjump(*OAK_BASE_PRE)
    texts = dict(T5)
    texts.update({k: riv(rt(RED_LAB, t)) for k, t in (('gramps', 21), ('what', 22), ('request', 23), ('invent', 24),
                                                       ('gotdex', 25), ('dream', 26), ('leave', 27))})
    for k_, v in texts.items():
        assert k_ not in a.labels, k_
        a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    p_ = fo(*OAK_TALK); assert rom[p_] == 0x04 and (rom[p_ + 1], r16(p_ + 2)) == (0x1F, 0x7FA0)
    q_ = fo(0x1F, 0x7FA0); assert rom[q_] == 0x04 and (rom[q_ + 1], r16(q_ + 2)) == OAK_BASE_POST
    rom[p_ + 1] = BANK; w16(p_ + 2, a.labels['oak'])
    log.append('OaksLab: Oak (parcel / Pokédex) %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= scene table: the mart's entry script (shares phase 28's always-0 scene byte)
    import build_phase21 as P21
    sr = P21.SCENES_REF
    tb = fo(rom[sr], r16(sr + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    tab = bytes(rom[tb:tb + 4 * n_]) + bytes([*mapids['ViridianMart'], P28.SCENE_AREAS & 0xFF, P28.SCENE_AREAS >> 8])
    assert rom[sr] == 0x61
    at = P28.sp_put61(rom, tab + b'\xff'); w16(sr + 3, at)
    rom[tb:tb + 4 * n_ + 1] = b'\xff' * (4 * n_ + 1)

    # ================= crossing into a map on another tileset (Gen I <-> Crystal): its graphics are loaded and the
    # screen redrawn (as after a warp; the screen goes blank for a moment).  Crystal's connection setup only loads the
    # tileset's pointers (map setup command 0F = LoadMapTileset, used by the connection script only).
    cs = rom.find(bytes([0x2A, 0x18, 0x1A, 0x14, 0x23, 0x0A, 0x0F, 0x0C, 0x16, 0x05, 0x11, 0x2D, 0x2B, 0x12, 0x26, 0x29, 0xFF]))
    j = rom.find(bytes([0x4F, 0x06, 0x00, 0x21]), cs); assert 0 < j - cs < 0x80
    cmds = fo(cs // 0x4000, r16(j + 4))
    assert rom[cmds + 3 * 0x0F:cmds + 3 * 0x0F + 3] == bytes([0x00, 0xF9, 0x2C])               # LoadMapTileset
    assert rom[cmds + 3 * 0x10:cmds + 3 * 0x10 + 3] == bytes([0x41, 0x50, 0x47])               # LoadMapTimeOfDay
    W_TS = 0xD20A
    hk = sp.put(BANK, bytes([0xFA, W_TS & 0xFF, W_TS >> 8, 0x47, 0xFA, (W_TS + 1) & 0xFF, W_TS >> 8, 0x4F,
                             0xFA, (W_TS + 2) & 0xFF, W_TS >> 8, 0x57, 0xC5, 0xD5,
                             0xCD, 0xF9, 0x2C,                                   # call LoadMapTileset
                             0xD1, 0xC1,
                             0xFA, W_TS & 0xFF, W_TS >> 8, 0xB8, 0x20, 0x0B,
                             0xFA, (W_TS + 1) & 0xFF, W_TS >> 8, 0xB9, 0x20, 0x05,
                             0xFA, (W_TS + 2) & 0xFF, W_TS >> 8, 0xBA, 0xC8,
                             0xCD, 0x68, 0x05,                                   # call DisableLCD
                             0xCD, 0xF3, 0x27,                                   # call LoadTilesetGFX
                             0x3E, 0x23, 0x21, 0xE5, 0x40, 0xCF,                 # farcall ReplaceTimeOfDayPals
                             0x3E, 0x41, 0x21, 0x66, 0x47, 0xCF,                 # farcall LoadMapTimeOfDay (the redraw part)
                             0xC3, 0x8A, 0x05]))                                 # jp EnableLCD
    rom[cmds + 3 * 0x0F] = BANK; w16(cmds + 3 * 0x0F + 1, hk)

    P17.fix_outdoor_sprites(rom, log)
    P26.trim_outdoor_sprites(rom, vir[0], log)
    # the sleeping old man (second sprite table) needs his own place in the group's outdoor sprite list
    tab = fo(*P17.OUTDOOR_SPRITES_PTR); gi = vir[0] - 1
    lp = fo(5, rom[tab + 2 * gi] | rom[tab + 2 * gi + 1] << 8); lst = list(rom[lp:lp + 23])
    k = next(i for i in range(1, 23) if lst[i] == lst[0]); rom[lp + k] = SPR['SPRITE_GAMBLER_ASLEEP']
    log.append('outdoor sprites group %d: + %02X' % (vir[0], SPR['SPRITE_GAMBLER_ASLEEP']))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
