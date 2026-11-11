#!/usr/bin/env python3
"""Phase 40: Celadon City as in Red / the Pikachu full-color hack:
 * Red's town (Gen I overworld tileset, Red's 25x18 blocks): Red's people (the old man who gives TM41, Poliwrath and
   its trainer, the Rockets by the Game Corner), signs, the hidden PP Up.  Routes 7 and 16 joined at Red's offsets.
 * Crystal's Department Store, Mansion, Pokémon Center and Gym behind Red's doors; Red's Game Corner of phase 12 and
   the prize room.
 * Red's buildings (new maps): the diner (the man who lost everything at the slots gives the Coin Case), the Game
   Corner chief's house, the hotel.
usage: build_phase40.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import redmap as RM
from evedit import MapEvents
import build_phase15 as P15
import build_phase17 as P17
import build_phase25 as P25
import build_phase26 as P26
import build_phase28 as P28
import build_phase37 as P37
import routekit as RK

FIRST_FLAG = 452                   # 450-451: phase 39
FIRST_MAP = 123                    # 26:121-122 = phase 39
TBANK, BANK, DBANK = 0x78, 0x69, 0x66
LOBBY_TS, PC_TS = 35, 41
SPR = dict(P37.SPR); SPR.update({'SPRITE_COOK': 0x6D, 'SPRITE_GYM_GUIDE': 0x48})
RED_C = 0x06
NEW = ['CeladonDiner', 'CeladonChiefHouse', 'CeladonHotel']
NEW_RED = {'CeladonDiner': 0x8A, 'CeladonChiefHouse': 0x8B, 'CeladonHotel': 0x8C}
NEW_DOOR = {'CELADON_DINER': 'CeladonDiner', 'CELADON_CHIEF_HOUSE': 'CeladonChiefHouse', 'CELADON_HOTEL': 'CeladonHotel'}
CR_DOOR = {'CELADON_MART_1F': 'CeladonDeptStore1F', 'CELADON_MANSION_1F': 'CeladonMansion1F',
           'CELADON_POKECENTER': 'CeladonPokecenter1F', 'CELADON_GYM': 'CeladonGym', 'GAME_CORNER': 'CeladonGameCorner',
           'GAME_CORNER_PRIZE_ROOM': 'CeladonGameCornerPrizeRoom', 'CELADON_MART_5F': 'CeladonDeptStore5F'}
COIN_CASE = 0x36
POLIWRATH = 62
# Red door (x, y) -> which of the Crystal interior's doors (its warps to the city, in order) it uses
DOOR_PICK = {(8, 13): 0, (10, 13): 1, (24, 9): 0, (24, 3): 2, (25, 3): 2}


def add_tileset(rom, sp, TS, ts, data_bank, log, anim_src=5):
    """portmaps.Tilesets.add, for a full bank 12: the palettes and their copy routine go to data_bank, only a short
    hook (farcall) in bank 12"""
    def r16(o): return rom[o] | rom[o + 1] << 8
    i = TS.count(); assert i < P15.TS_CAP
    gfx = lz(ts.gfx_raw)
    a_g = sp.put(data_bank, gfx); a_m = sp.put(data_bank, ts.blocks); a_c = sp.put(data_bank, bytes(ts.coll))
    lo, hi = P15.OLD_TS_HOLE
    hole = next((o for o in range(lo, hi - 0x70 + 1, 0x70) if not any(rom[o:o + 0x70])), None)
    if hole is not None: rom[hole:hole + 0x70] = ts.palmap; a_p = 0x4000 + hole % 0x4000
    else: a_p = sp.put(0x13, ts.palmap)
    anim = TS.entry(anim_src)[9:11]
    rom[TS.tab + 15 * i:TS.tab + 15 * i + 15] = bytes([data_bank, a_g & 0xFF, a_g >> 8, data_bank, a_m & 0xFF, a_m >> 8,
                                                      data_bank, a_c & 0xFF, a_c >> 8]) + anim + b'\x00\x00' + bytes([a_p & 0xFF, a_p >> 8])
    prev = r16(LSMP + 1)
    hp = rom[HOUSEPAL_CALL:HOUSEPAL_CALL + 14]; wbg = hp[3:5]; fc = hp[12:14]
    ld_ts = bytes(rom[fo(0x12, prev):fo(0x12, prev) + 3])
    a_pal = sp.put(data_bank, ts.pals)
    cp = sp.put(data_bank, bytes([0x21, a_pal & 0xFF, a_pal >> 8, 0x3E, 0x05, 0x11]) + bytes(wbg) + bytes([0x01, 0x40, 0x00, 0xCD]) +
                bytes(fc) + b'\xc9')
    a = Asm(sp.here(0x12))
    a.raw(ld_ts); a.db(0xFE, i, 0x28, 0x03); a.db(0xC3); a.dw(prev)
    a.db(0x3E, data_bank, 0x21); a.dw(cp); a.db(0xCF, 0x37, 0xC9)                       # farcall; scf; ret
    hk = sp.put(0x12, a.done()); rom[LSMP + 1] = hk & 0xFF; rom[LSMP + 2] = hk >> 8
    log.append('tileset %s id %d (gfx %d bytes, %d blocks)' % (ts.name, i, len(gfx), ts.nblocks))
    return i


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    for b in (TBANK, BANK, DBANK, 0x6D, 0x12):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    # bank 13 (palette maps): the old map scene table that phase 28 moved to bank 61 (left as FF bytes) is free
    OLD_SCENES = (0x4D012, 0x4D14F)
    assert all(v == 0xFF for v in rom[OLD_SCENES[0]:OLD_SCENES[1]])
    sp.set_area(0x13, OLD_SCENES[0] + 1, OLD_SCENES[1])
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    got_tm41 = FL.new(); got_coin_case = FL.new()
    nid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(NEW)}
    cel = mapid('CeladonCity')

    # ================= tilesets: the town; the diner (Lobby), the hotel (Pokémon Center); the chief's house: Red's
    # Mansion tileset (new)
    w, h = RK.red_dims('CeladonCity'); town = MapPort('CeladonCity', K.ow, w, h, 'CeladonCity.blk')
    K.dims['CeladonCity'] = (w, h)
    redwarps = P25.red_objects('CeladonCity')[1]
    K.overworld_variants({'CeladonCity': town}, {'CeladonCity': RK.warp_overrides(K.ow, town, redwarps)})
    lts = Tileset('Lobby', 18, 'lobby.bst', SC + '/out/pk_lobby.pkl')
    pts = Tileset('Pokecenter', 2, 'pokecenter.bst', SC + '/out/pk_mart.pkl')
    mts = Tileset('Mansion', 19, 'mansion.bst', SC + '/out/pk_mansion.pkl')
    nmp = {}
    for n, ts in (('CeladonDiner', lts), ('CeladonHotel', pts), ('CeladonChiefHouse', mts)):
        w_, h_ = RK.red_dims(n); nmp[n] = MapPort(n, ts, w_, h_, n + '.blk')
    def ovr(ts, n): return {n: {(x, y): P25.warp_override(ts, nmp[n], x, y) for x, y, d, wi in P25.red_objects(n)[1]}}
    K.ts_variants(LOBBY_TS, lts, {'CeladonDiner': nmp['CeladonDiner']}, ovr(lts, 'CeladonDiner'))
    K.ts_variants(PC_TS, pts, {'CeladonHotel': nmp['CeladonHotel']}, ovr(pts, 'CeladonHotel'))
    TS = PM.Tilesets(rom, sp)
    meta2, coll2, blks = pairwalls.variants(mts, bytes(mts.blocks), bytes(mts.coll), {'CeladonChiefHouse': nmp['CeladonChiefHouse']},
                                            [], ovr(mts, 'CeladonChiefHouse'))
    mts.blocks = meta2; mts.coll = bytearray(coll2); mts.nblocks = len(coll2) // 4
    nmp['CeladonChiefHouse'].blk = blks['CeladonChiefHouse']
    mansion_ts = add_tileset(rom, sp, TS, mts, 0x6D, log)
    tsid = {'CeladonDiner': LOBBY_TS, 'CeladonHotel': PC_TS, 'CeladonChiefHouse': mansion_ts}
    K.bank = BANK
    K.alloc_headers(FIRST_MAP, len(NEW))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end40'); a.end()
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    def tm41(a, texts, lab, o):
        T(lab + 'a', 6, 0x68A9); T(lab + 'f', 6, 0x6953); T(lab + 'x', 6, 0x6912)
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_tm41); a.iftrue(lab + 'e')
        a.writetext(lab + 'a'); a.verbosegiveitem(PM.item_id('TM_SOFTBOILED'), 1); a.iffalse(lab + 'n'); a.setevent(got_tm41)
        a.label(lab + 'e'); a.writetext(lab + 'x'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'n'); a.writetext(lab + 'f'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    def poliwrath(a, texts, lab, o):
        first, more = P37.text_then_asm(RED_C, 7); texts[lab + 't'] = first
        a.label(lab); a.opentext(); a.writetext(lab + 't'); a.cry(POLIWRATH); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    ob, bgs = K.red_events(a, texts, 'CeladonCity', RED_C, 'C_', {5: tm41, 7: poliwrath}, SPR)
    # new buildings
    nb = {}
    K.bench_texts = {(0, 4): RM.crystal_text(0x18, 0x7F7A)}         # Red: CeladonCityHotelText (the bench)
    for n in ('CeladonChiefHouse', 'CeladonHotel'):
        nb[n] = K.red_events(a, texts, n, NEW_RED[n], n[7:] + '_', {}, SPR)
    def guide(a, texts, lab, o):
        T(lab + 'a', 0x12, 0x61C4); T(lab + 'f', 0x12, 0x623C); T(lab + 'w', 0x12, 0x624A)
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_coin_case); a.iftrue(lab + 'e')
        a.writetext(lab + 'a'); a.promptbutton(); a.verbosegiveitem(COIN_CASE, 1); a.iffalse(lab + 'n')
        a.setevent(got_coin_case); a.closetext(); a.end()
        a.label(lab + 'e'); a.writetext(lab + 'w'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'n'); a.writetext(lab + 'f'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    nb['CeladonDiner'] = K.red_events(a, texts, 'CeladonDiner', 0x8A, 'Diner_', {5: guide}, SPR)
    K.put_texts(a, texts)

    # warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    tw = []; back = {}
    for i, (x, y, d, wi) in enumerate(redwarps):
        if d in NEW_DOOR: tw.append(W(x, y, wi, nid[NEW_DOOR[d]])); continue
        cr = CR_DOOR[d]
        pi = [k + 1 for k, w_ in enumerate(K.warps_of(cr)) if (w_[3], w_[4]) == cel]
        if d == 'CELADON_MART_5F': pi = [1]                        # Red: an inaccessible door
        k_ = DOOR_PICK.get((x, y), 0)
        tw.append(W(x, y, pi[min(k_, len(pi) - 1)], mapid(cr)))
        if d != 'CELADON_MART_5F': back.setdefault(cr, {}).setdefault(0, i + 1)
    back['CeladonDeptStore1F'] = {0: 1, 1: 2}                   # Crystal's two door warps -> Red's two doors
    back['CeladonMansion1F'] = {0: 3, 1: 3, 2: 4}               # front, front, back
    cbs = []
    for t_, r in MapEvents(rom, 'CeladonCity').callbacks:
        L_ = 'Ccb%d' % t_; a.label(L_); a.farsjump(r[1], r[2]); cbs.append((t_, L_))
    K.emit(a, 'CeladonCity', tw, [], bgs, ob, cbs)
    for n in NEW:
        K.emit(a, n, [W(x, y, wi, cel) for x, y, d, wi in P25.red_objects(n)[1]], [], nb[n][1], nb[n][0], [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Celadon: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    hsrc = {'CeladonDiner': 'CeladonCafe', 'CeladonChiefHouse': 'CeladonCafe', 'CeladonHotel': 'CeladonCafe'}
    for i, n in enumerate(NEW):
        K.make_map(FIRST_MAP + i, nmp[n], tsid[n], border_of(n), hsrc[n], 3, a, n)

    # ================= attributes, connections (Red's: Routes 7, 16 are Red's), blocks
    conns = RK.red_conns('CeladonCity')
    K.new_attrs('CeladonCity', w, h, border_of('CeladonCity'), a.labels['CeladonCityms'], a.labels['CeladonCityev'], conns)
    rom[hdr_index('CeladonCity') + 1] = RK.OVERWORLD_TS
    opp = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
    for d, nb_, o_ in conns: K.set_conn(nb_, opp[d], 'CeladonCity', -o_)
    K.place_blocks('CeladonCity', town.blk, True)
    for d, nb_, o_ in conns: K.place_blocks(nb_, K.crystal_blocks(nb_), True)

    # ================= warps back (the k-th warp of a Crystal interior to the city -> Red's door)
    for cr, m in back.items():
        k_ = [0]
        def fn(i, w_, m=m, k_=k_):
            if (w_[3], w_[4]) == cel: r_ = (m.get(k_[0], m[max(m)]), cel); k_[0] += 1; return r_
        assert K.fix_warps(cr, fn) >= 1, cr
    pc = [(x, y) for x, y, d, wi in redwarps if d == 'CELADON_POKECENTER'][0]
    sp_i = [i for i in range(40) if (rom[P26.SPAWN_TABLE + 4 * i], rom[P26.SPAWN_TABLE + 4 * i + 1]) == cel]
    assert len(sp_i) == 1
    rom[P26.SPAWN_TABLE + 4 * sp_i[0] + 2:P26.SPAWN_TABLE + 4 * sp_i[0] + 4] = bytes([pc[0], pc[1] + 1])

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
