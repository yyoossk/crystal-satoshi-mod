#!/usr/bin/env python3
"""Phase 39: Lavender Town as in Red / the Pikachu full-color hack:
 * Red's town (Gen I overworld tileset): Red's people (the girl who asks whether you believe in ghosts), signs.
   Routes 8, 10 and 12 joined at Red's offsets.
 * Crystal's Pokémon Center, Name Rater and Mart (Red's goods) behind Red's doors; the Pokémon Tower of phase 11.
 * Red's houses (new maps): Mr. Fuji's Pokémon house (Red's people; Mr. Fuji there after the Pokémon Tower, with the
   Poké Flute of phase 35; the tower's top floor now sends the player there, as in Red) and the Cubone house.
 * Crystal's Soul House, Radio Tower and speech house are no longer there.
usage: build_phase39.py IN.gbc OUT.gbc OUT.ips
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
import build_phase28 as P28
import build_phase35 as P35
import build_phase37 as P37
import routekit as RK

FIRST_FLAG = 450                   # 446-449: phase 38
FIRST_MAP = 121                    # 26:119-120 = phase 38
TBANK, BANK, DBANK = 0x6C, 0x64, 0x6B
HOUSE_TS = 44
SPR = dict(P37.SPR); SPR.update({'SPRITE_MR_FUJI': 0x2F, 'SPRITE_POKEDEX': 0x55})
RED_L = 0x04
HOUSES = ['MrFujisHouse', 'LavenderCuboneHouse']
HOUSE_NAME = {'MrFujisHouse': 'RedMrFujisHouse', 'LavenderCuboneHouse': 'LavenderCuboneHouse'}     # labels
CR_DOOR = {'LAVENDER_POKECENTER': 'LavenderPokecenter1F', 'NAME_RATERS_HOUSE': 'LavenderNameRater',
           'LAVENDER_MART': 'LavenderMart'}
NEW_DOOR = {'MR_FUJIS_HOUSE': 'MrFujisHouse', 'LAVENDER_CUBONE_HOUSE': 'LavenderCuboneHouse'}
MART_GOODS = ('GREAT_BALL', 'SUPER_POTION', 'REVIVE', 'ESCAPE_ROPE', 'SUPER_REPEL', 'ANTIDOTE', 'BURN_HEAL', 'ICE_HEAL', 'PARLYZ_HEAL')
CRYSTAL_MART = ('GREAT_BALL', 'POTION', 'SUPER_POTION', 'MAX_REPEL', 'ANTIDOTE', 'PARLYZ_HEAL', 'AWAKENING', 'BURN_HEAL')
EV_RESCUED_FUJI = 0x817
GOT_FLUTE = 0x800 + P35.FIRST_FLAG + 2         # phase 35's flags: snorlax gone, snorlax had, got flute, ...
POKE_FLUTE = P35.POKE_FLUTE
PSYDUCK, NIDORINO, CUBONE = 54, 33, 104
TOWER_FUJI_WARP = bytes([0x3C, 18, 7, 2, 4])  # phase 11: Mr. Fuji on the tower's top floor -> his (Crystal's) house


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
    fuji_hide = FL.new()
    hid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(HOUSES)}
    lav = mapid('LavenderTown')

    # ================= the mart's goods: Red's nine (a new list in bank 5, the mart table re-pointed)
    ids = [P15.item_id(n) for n in CRYSTAL_MART]
    mo = rom.find(bytes([8] + ids)); assert mo > 0 and rom.find(bytes([8] + ids), mo + 1) < 0 and mo // 0x4000 == 5
    p_ = 0x4000 + mo % 0x4000; refs = [i for i in range(0x14000, 0x18000 - 1) if rom[i] == p_ & 0xFF and rom[i + 1] == p_ >> 8]
    assert len(refs) == 1, refs
    red = [P15.item_id(n) for n in MART_GOODS]
    w16(refs[0], sp.put(0x05, bytes([len(red)] + red + [0xFF])))

    # ================= tilesets
    w, h = RK.red_dims('LavenderTown'); town = MapPort('LavenderTown', K.ow, w, h, 'LavenderTown.blk')
    K.dims['LavenderTown'] = (w, h)
    redwarps = P25.red_objects('LavenderTown')[1]
    K.overworld_variants({'LavenderTown': town}, {'LavenderTown': RK.warp_overrides(K.ow, town, redwarps)})
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
    a.label('end39'); a.end()
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    def girl(a, texts, lab, o):
        T(lab + 'q', 0x11, 0x413C); T(lab + 'y', 0x11, 0x4150); T(lab + 'n', 0x11, 0x4166)
        a.label(lab); a.faceplayer(); a.opentext(); a.writetext(lab + 'q'); a.yesorno(); a.iffalse(lab + 'x')
        a.writetext(lab + 'y'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'x'); a.writetext(lab + 'n'); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    ob, bgs = K.red_events(a, texts, 'LavenderTown', RED_L, 'L_', {1: girl}, SPR)

    def obj(o, lab, fl=0xFFFF):
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        return [SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, fl]
    def cry_text(lab, g, tid, mon):
        first, more = P37.text_then_asm(g, tid); texts[lab + 't'] = first
        a.label(lab); a.opentext(); a.writetext(lab + 't'); a.cry(mon); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
        return lab
    def by_rescue(lab, before, after):
        T(lab + 'b', 7, before); T(lab + 'a', 7, after)
        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(EV_RESCUED_FUJI); a.iftrue(lab + 'r')
        a.writetext(lab + 'b'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'r'); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
        return lab
    hb = {}
    # Mr. Fuji's house (Red)
    objs = P25.red_objects('MrFujisHouse')[0]
    fj = []
    for b_, p__ in RM.asm_hl(0x95, 5):
        try: fj.append(RM.crystal_text(b_, p__))
        except ValueError: pass                      # the "received" text (item name from RAM): Crystal's own
    t_help, t_full, t_helped = fj
    t_expl = RM.crystal_text(7, 0x6082); assert t_expl[1] == 0x51; t_expl = b'\x00' + t_expl[2:]
    texts.update(fj_help=t_help, fj_expl=t_expl, fj_full=t_full, fj_helped=t_helped, fj_dex=K.rt(0x95, 6))
    a.label('fj'); a.faceplayer(); a.opentext(); a.checkevent(GOT_FLUTE); a.iftrue('fj_h')
    a.writetext('fj_help'); a.verbosegiveitem(POKE_FLUTE, 1); a.iffalse('fj_f'); a.setevent(GOT_FLUTE)
    a.writetext('fj_expl'); a.waitbutton(); a.closetext(); a.end()
    a.label('fj_h'); a.writetext('fj_helped'); a.waitbutton(); a.closetext(); a.end()
    a.label('fj_f'); a.writetext('fj_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('fj_d'); a.jumptext('fj_dex')
    a.label('fj_cb'); a.checkevent(EV_RESCUED_FUJI); a.iftrue('fj_cs')
    a.setevent(fuji_hide); a.endcallback()
    a.label('fj_cs'); a.clearevent(fuji_hide); a.endcallback()
    hb['MrFujisHouse'] = [obj(objs[0], by_rescue('fn', 0x5EDA, 0x5EFF)), obj(objs[1], by_rescue('fg', 0x5F39, 0x5F82)),
                          obj(objs[2], cry_text('fp', 0x95, 3, PSYDUCK)), obj(objs[3], cry_text('fo', 0x95, 4, NIDORINO)),
                          obj(objs[4], 'fj', fuji_hide), obj(objs[5], 'fj_d')]
    assert [o['sprite'] for o in objs] == ['SPRITE_SUPER_NERD', 'SPRITE_LITTLE_GIRL', 'SPRITE_MONSTER', 'SPRITE_MONSTER',
                                           'SPRITE_MR_FUJI', 'SPRITE_POKEDEX']
    # the Cubone house
    objs = P25.red_objects('LavenderCuboneHouse')[0]
    T('cg_b', 7, 0x61B1); T('cg_a', 7, 0x61F6)
    a.label('cg'); a.faceplayer(); a.opentext(); a.checkevent(EV_RESCUED_FUJI); a.iftrue('cg_r')
    a.writetext('cg_b'); a.waitbutton(); a.closetext(); a.end()
    a.label('cg_r'); a.writetext('cg_a'); a.waitbutton(); a.closetext(); a.end()
    hb['LavenderCuboneHouse'] = [obj(objs[0], cry_text('cc', 0x97, 1, CUBONE)), obj(objs[1], 'cg')]
    K.put_texts(a, texts)

    # warps
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    tower = [(w_[3], w_[4]) for w_ in K.warps_of('LavenderTown') if w_[3] == G26]
    assert len(tower) == 1; tower = tower[0]
    tw = []; back = {}
    for i, (x, y, d, wi) in enumerate(redwarps):
        if d in NEW_DOOR: tw.append(W(x, y, wi, hid[NEW_DOOR[d]]))
        elif d == 'POKEMON_TOWER_1F': tw.append(W(x, y, 1, tower)); back.setdefault(tower, []).append(i + 1)
        else:
            cr = CR_DOOR[d]
            pi = [k + 1 for k, w_ in enumerate(K.warps_of(cr)) if (w_[3], w_[4]) == lav]
            tw.append(W(x, y, pi[0], mapid(cr))); back.setdefault(cr, []).append(i + 1)
    cbs = []
    for t_, r in MapEvents(rom, 'LavenderTown').callbacks:
        L_ = 'Lcb%d' % t_; a.label(L_); a.farsjump(r[1], r[2]); cbs.append((t_, L_))
    K.emit(a, 'LavenderTown', tw, [], bgs, ob, cbs)
    for n in HOUSES:
        K.emit(a, HOUSE_NAME[n], [W(x, y, wi, lav) for x, y, d, wi in P25.red_objects(n)[1]], [], [], hb[n],
               [(2, 'fj_cb')] if n == 'MrFujisHouse' else [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Lavender: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    for i, n in enumerate(HOUSES):
        K.make_map(FIRST_MAP + i, hmp[n], HOUSE_TS, border_of(n), 'MrFujisHouse', 3, a, HOUSE_NAME[n])

    # ================= attributes, connections (Red's: Routes 8, 10, 12 are Red's), blocks
    conns = [(d, 'Route10North' if nb_ == 'Route10' else nb_, o_) for d, nb_, o_ in RK.red_conns('LavenderTown')]
    K.new_attrs('LavenderTown', w, h, border_of('LavenderTown'), a.labels['LavenderTownms'], a.labels['LavenderTownev'], conns)
    rom[hdr_index('LavenderTown') + 1] = RK.OVERWORLD_TS
    opp = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
    for d, nb_, o_ in conns: K.set_conn(nb_, opp[d], 'LavenderTown', -o_)
    K.place_blocks('LavenderTown', town.blk, True)
    for d, nb_, o_ in conns: K.place_blocks(nb_, K.crystal_blocks(nb_), True)

    # ================= warps back; the tower's Mr. Fuji sends the player to Red's house (in front of the door, facing up)
    for cr, idxs in back.items():
        k_ = [0]
        def fn(i, w_, idxs=idxs, k_=k_):
            if (w_[3], w_[4]) == lav: r_ = (idxs[min(k_[0], len(idxs) - 1)], lav); k_[0] += 1; return r_
        hdr = GROUP26_END + 9 * (cr[1] - G26_COUNT - 1) if isinstance(cr, tuple) else cr
        assert K.fix_warps(hdr, fn) >= 1, cr
    assert TOWER_FUJI_WARP[1:3] == bytes(mapid('MrFujisHouse'))
    o_ = rom.find(TOWER_FUJI_WARP); assert o_ > 0 and rom.find(TOWER_FUJI_WARP, o_ + 1) < 0
    rom[o_ + 1:o_ + 5] = bytes([*hid['MrFujisHouse'], 2, 6])
    pc = [(x, y) for x, y, d, wi in redwarps if d == 'LAVENDER_POKECENTER'][0]
    sp_i = [i for i in range(40) if (rom[P26.SPAWN_TABLE + 4 * i], rom[P26.SPAWN_TABLE + 4 * i + 1]) == lav]
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
