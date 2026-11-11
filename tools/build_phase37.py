#!/usr/bin/env python3
"""Phase 37: Vermilion City as in Red / the Pikachu full-color hack:
 * Red's town (Gen I overworld tileset): Red's people, signs, hidden item; the sailor at the harbour who checks the
   S.S. Ticket (and turns the player back once the ship has left, until the Kanto Hall of Fame: then Crystal's port
   and the ship to Olivine, as phase 16 made it).  Crystal's Snorlax, Diglett's Cave entrance and the houses that
   are not in Red are no longer there.
 * Crystal's Pokémon Center, Fan Club, Mart (with Red's goods) and Gym behind Red's doors; the harbour door leads into
   Crystal's port passage (phase 16: the dock / the port).
 * Red's houses (new maps): the Pidgey mail house, the fishing guru (the Old Rod), the trade house (Spearow for
   Farfetch'd).
 * Routes 6 and 11 joined to it at Red's offsets.
usage: build_phase37.py IN.gbc OUT.gbc OUT.ips
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
import build_phase15 as P15
import build_phase17 as P17
import build_phase19 as P19
import build_phase25 as P25
import build_phase26 as P26
import build_phase27 as P27
import build_phase28 as P28
import build_phase35 as P35
import routekit as RK

FIRST_FLAG = 443                   # 396-442: phase 36
FIRST_MAP = 116                    # 26:111-115 = phase 36
TBANK, BANK, DBANK = 0x6B, 0x6C, 0x6F
HOUSE_TS = 44
SPR = dict(P35.SPR); SPR.update({'SPRITE_BIRD': 0x4E, 'SPRITE_PAPER': 0x55})
RED_V = 0x05
HOUSES = ['VermilionPidgeyHouse', 'VermilionTradeHouse', 'VermilionOldRodHouse']
HOUSE_RED = {'VermilionPidgeyHouse': 0x5D, 'VermilionTradeHouse': 0xC4, 'VermilionOldRodHouse': 0xA3}
# Red's door -> Crystal's interior (its warps back are re-pointed)
CR_DOOR = {'VERMILION_POKECENTER': 'VermilionPokecenter1F', 'POKEMON_FAN_CLUB': 'PokemonFanClub',
           'VERMILION_MART': 'VermilionMart', 'VERMILION_GYM': 'VermilionGym', 'VERMILION_DOCK': 'VermilionPortPassage'}
NEW_DOOR = {'VERMILION_PIDGEY_HOUSE': 'VermilionPidgeyHouse', 'VERMILION_TRADE_HOUSE': 'VermilionTradeHouse',
            'VERMILION_OLD_ROD_HOUSE': 'VermilionOldRodHouse'}
MART_GOODS = ('POKE_BALL', 'SUPER_POTION', 'ICE_HEAL', 'AWAKENING', 'PARLYZ_HEAL', 'REPEL')
CRYSTAL_MART = ('ULTRA_BALL', 'SUPER_POTION', 'HYPER_POTION', 'REVIVE', 'PARLYZ_HEAL', 'AWAKENING', 'BURN_HEAL', 'LITEBLUEMAIL')
S_S_TICKET, OLD_ROD = 0x44, 0x3A
MACHOP, PIDGEY, SPEAROW, FARFETCHD = 66, 16, 21, 83
EV_HOF = 0x34A
VAR_FACING = 0x09


def text_then_asm(g, tid):
    """a Red text that prints, then runs asm (cry) and maybe prints one more text: (first, [more])"""
    R = RM.R; b, p = RM.text_ptr(g, tid); o = RM.fo(b, p); assert R[o] == 0x00
    e = o + 1
    while R[e] != 0x50: e += 1
    assert R[e + 1] == 0x08, (hex(g), tid)
    first = bytes(R[o:e]) + b'\x57'
    more = []
    for i in range(e + 2, e + 40):
        if R[i] == 0x21:
            pp = R[i + 1] | R[i + 2] << 8
            if 0x4000 <= pp < 0x8000 and RM.text_body(b, pp)[0] == 'text': more.append(RM.crystal_text(b, pp)); break
        if R[i] == 0xC3 and R[i + 1:i + 3] == bytes([0x6A, 0x0F]): break
    return first, more


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
    got_rod = FL.new()
    hid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(HOUSES)}
    ver = mapid('VermilionCity')

    # phase 16's flags, read from its dock gate script (got HM01 / ticket shown / ship left)
    pw = MapEvents(rom, 'VermilionPortPassage').warps
    dock = [(w[3], w[4]) for w in pw if w[3] == G26][0]
    da = attrs(rom, GROUP26_END + 9 * (dock[1] - G26_COUNT - 1)); dev = parse_events(rom, da['scbank'], da['events'])
    c_ = dev['coords'][0][1]; o_ = fo(da['scbank'], c_[4] | c_[5] << 8)
    assert rom[o_] == 0x31 and rom[o_ + 3] == 0x09 and rom[o_ + 6] == 0x31
    got_hm01, shown = r16(o_ + 1), r16(o_ + 7); gl = fo(da['scbank'], r16(o_ + 4))
    assert rom[gl] == 0x31; ship_left = r16(gl + 1)
    log.append('phase 16 flags: HM01 %X, ticket shown %X, ship left %X' % (got_hm01, shown, ship_left))

    # ================= Red's trade: Spearow -> Farfetch'd (after phases 19, 27, 35, 36)
    ref = P19.NPC_TRADES_REF; assert rom[ref] == 0x21
    to = fo(0x3F, r16(ref + 1)); nt = 7 + len(P19.RED_TRADES) + 3
    table = bytearray(rom[to:to + 16 * nt])
    nick = bytes(RT.R[0x72063 + 3:0x72063 + 7])
    table += bytes([0, SPEAROW, FARFETCHD]) + nick + bytes([0x96, 0x66, 0x00]) + (31415 + 1111 * nt).to_bytes(2, 'little') + \
        encode('ゴロウ')[:3] + b'\x00'
    trade_dux = nt
    w16(ref + 1, sp.put(0x3F, bytes(table)))

    # ================= the mart's goods: Red's
    ids = [P15.item_id(n) for n in CRYSTAL_MART]
    mo = rom.find(bytes([8] + ids)); assert mo > 0 and rom.find(bytes([8] + ids), mo + 1) < 0
    red = [P15.item_id(n) for n in MART_GOODS]
    rom[mo:mo + 10] = bytes([len(red)] + red + [0xFF]) + bytes(10 - len(red) - 2)

    # ================= tilesets
    w, h = RK.red_dims('VermilionCity'); town = MapPort('VermilionCity', K.ow, w, h, 'VermilionCity.blk')
    K.dims['VermilionCity'] = (w, h)
    redwarps = P25.red_objects('VermilionCity')[1]
    K.overworld_variants({'VermilionCity': town}, {'VermilionCity': RK.warp_overrides(K.ow, town, redwarps)})
    hts = Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl')
    hmp = {}
    for n in HOUSES:
        w_, h_ = RK.red_dims(n); hmp[n] = MapPort(n, hts, w_, h_, n + '.blk')
    K.ts_variants(HOUSE_TS, hts, hmp, {n: {(x, y): P25.warp_override(hts, hmp[n], x, y) for x, y, d, wi in P25.red_objects(n)[1]}
                                       for n in HOUSES})
    K.bank = BANK
    K.alloc_headers(FIRST_MAP, len(HOUSES))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end37'); a.end()
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    T('sl_wel', 6, 0x650A); T('sl_tk', 6, 0x651D); T('sl_no', 6, 0x657F); T('sl_ok', 6, 0x6548); T('sl_gone', 6, 0x65CB)
    def gambler(a, texts, lab, o):
        T(lab + 'a', 6, 0x6453); T(lab + 'b', 6, 0x647A)
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(ship_left); a.iftrue(lab + 'g')
        a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'g'); a.writetext(lab + 'b'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    def sailor(a, texts, lab, o):
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(EV_HOF); a.iftrue(lab + 'w')
        a.checkevent(ship_left); a.iftrue(lab + 'g')
        a.label(lab + 'w'); a.writetext('sl_wel'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'g'); a.writetext('sl_gone'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    def machop(a, texts, lab, o):
        first, more = text_then_asm(RED_V, 5); texts[lab + 'a'] = first; texts[lab + 'b'] = more[0]
        a.label(lab); a.opentext(); a.writetext(lab + 'a'); a.cry(MACHOP); a.waitsfx(); a.writetext(lab + 'b')
        a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    ob, bgs = K.red_events(a, texts, 'VermilionCity', RED_V, 'V_', {2: gambler, 3: sailor, 5: machop}, SPR)
    # the harbour: the sailor checks the S.S. Ticket when the player walks down to the dock (Red: (18, 30), facing down)
    a.label('tick'); a.db(0x1C, VAR_FACING); a.ifnotequal(0, 'end37')
    a.checkevent(EV_HOF); a.iftrue('end37')
    a.opentext(); a.checkevent(ship_left); a.iftrue('tick_g')
    a.writetext('sl_tk'); a.waitbutton(); a.checkitem(S_S_TICKET); a.iffalse('tick_n')
    a.writetext('sl_ok'); a.waitbutton(); a.closetext(); a.setevent(shown); a.end()
    a.label('tick_n'); a.writetext('sl_no'); a.waitbutton(); a.closetext(); a.applymovement(0, 'tick_up'); a.end()
    a.label('tick_g'); a.writetext('sl_gone'); a.waitbutton(); a.closetext(); a.applymovement(0, 'tick_up'); a.end()
    a.label('tick_up'); a.db(0x0D, 0x47)

    # houses
    def obj(o, lab, fl=0xFFFF):
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        return [SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, fl]
    hb = {}
    objs = P25.red_objects('VermilionPidgeyHouse')[0]
    texts['ph_yt'] = K.rt(0x5D, 1); first, more = text_then_asm(0x5D, 2); texts['ph_pt'] = first; texts['ph_lt'] = K.rt(0x5D, 3)
    a.label('ph_y'); a.jumptextfaceplayer('ph_yt')
    a.label('ph_p'); a.opentext(); a.writetext('ph_pt'); a.cry(PIDGEY); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    a.label('ph_l'); a.jumptext('ph_lt')
    hb['VermilionPidgeyHouse'] = [obj(objs[0], 'ph_y'), obj(objs[1], 'ph_p'), obj(objs[2], 'ph_l')]
    objs = P25.red_objects('VermilionTradeHouse')[0]
    a.label('th'); a.faceplayer(); a.opentext(); a.db(0x95, trade_dux); a.waitbutton(); a.closetext(); a.end()
    hb['VermilionTradeHouse'] = [obj(objs[0], 'th')]
    objs = P25.red_objects('VermilionOldRodHouse')[0]
    T('or_hi', 0x15, 0x6ED1); T('or_no', 0x15, 0x6F80); T('or_full', 0x15, 0x6FA3); T('or_how', 0x15, 0x6F8D)
    texts['or_give'] = P27.gen1_text(RM.fo(0x15, 0x6F02), {('ram', 0xCF45): P27.lit('ボロのつりざお')})
    a.label('or'); a.faceplayer(); a.opentext(); a.checkevent(got_rod); a.iftrue('or_h')
    a.writetext('or_hi'); a.yesorno(); a.iffalse('or_n')
    a.db(0x1F, OLD_ROD, 1); a.iffalse('or_f')                                          # giveitem
    a.writetext('or_give'); a.waitbutton(); a.closetext(); a.setevent(got_rod); a.end()
    a.label('or_n'); a.writetext('or_no'); a.waitbutton(); a.closetext(); a.end()
    a.label('or_f'); a.writetext('or_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('or_h'); a.writetext('or_how'); a.waitbutton(); a.closetext(); a.end()
    hb['VermilionOldRodHouse'] = [obj(objs[0], 'or')]
    K.put_texts(a, texts)

    # warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    cw = K.warps_of('VermilionCity')
    def cr_idx(name): return [i + 1 for i, w_ in enumerate(cw) if (w_[3], w_[4]) == mapid(name)]
    tw = []; back = {}
    for i, (x, y, d, wi) in enumerate(redwarps):
        if d in NEW_DOOR: tw.append(W(x, y, 1, hid[NEW_DOOR[d]]))
        else:
            cr = CR_DOOR[d]
            if d == 'VERMILION_DOCK':
                pi = [k + 1 for k, w_ in enumerate(K.warps_of(cr)) if (w_[3], w_[4]) == ver]
                tw.append(W(x, y, pi[0 if x == 18 else 1], mapid(cr)))
            else:
                pi = [k + 1 for k, w_ in enumerate(K.warps_of(cr)) if (w_[3], w_[4]) == ver]
                tw.append(W(x, y, pi[0], mapid(cr)))
            back.setdefault(cr, []).append(i + 1)
    cbs = []
    for t_, r in MapEvents(rom, 'VermilionCity').callbacks:
        L_ = 'Vcb%d' % t_; a.label(L_); a.farsjump(r[1], r[2]); cbs.append((t_, L_))
    K.emit(a, 'VermilionCity', tw, [(0xFF, 30, 18, 'tick')], bgs, ob, cbs)
    hw = {}
    for n in HOUSES:
        hw[n] = [W(x, y, wi, ver) for x, y, d, wi in P25.red_objects(n)[1]]
        K.emit(a, n, hw[n], [], [], hb[n], [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Vermilion: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    for i, n in enumerate(HOUSES):
        K.make_map(FIRST_MAP + i, hmp[n], HOUSE_TS, border_of(n), 'VermilionFishingSpeechHouse', 3, a, n)

    # ================= attributes, connections (Red's offsets: Routes 6 and 11 are Red's), blocks
    conns = RK.red_conns('VermilionCity')
    K.new_attrs('VermilionCity', w, h, border_of('VermilionCity'), a.labels['VermilionCityms'], a.labels['VermilionCityev'], conns)
    rom[hdr_index('VermilionCity') + 1] = RK.OVERWORLD_TS
    opp = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
    for d, nb_, o_ in conns: K.set_conn(nb_, opp[d], 'VermilionCity', -o_)
    K.place_blocks('VermilionCity', town.blk, True)
    for d, nb_, o_ in conns: K.place_blocks(nb_, K.crystal_blocks(nb_), True)

    # ================= warps back
    for cr, idxs in back.items():
        k_ = [0]
        def fn(i, w_, idxs=idxs, k_=k_):
            if (w_[3], w_[4]) == ver: r_ = (idxs[min(k_[0], len(idxs) - 1)], ver); k_[0] += 1; return r_
        assert K.fix_warps(cr, fn) >= 1, cr
    # spawn point (fly / last Pokémon Center): in front of Red's Pokémon Center
    pc = [(x, y) for x, y, d, wi in redwarps if d == 'VERMILION_POKECENTER'][0]
    sp_i = [i for i in range(40) if (rom[P26.SPAWN_TABLE + 4 * i], rom[P26.SPAWN_TABLE + 4 * i + 1]) == ver]
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
