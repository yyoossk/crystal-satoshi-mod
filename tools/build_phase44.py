#!/usr/bin/env python3
"""Phase 44: the Fighting Dojo and the Copycat's house as in Red / the Pikachu full-color hack:
 * Red's Dojo room (Red's Dojo tileset, new) in place of Crystal's; phase 42's people stay.
 * Red's Copycat's house 1F / 2F (Red's house tileset, new; new maps): Red's people where Red has them; the Copycat
   gives TM31 for a Poké Doll; the Super Famicom; her PC (her diary, read facing it).
 * Tileset palettes: the chain of hooks in bank 12 (full) becomes one table-driven routine (palhooks), so new tilesets
   need no room there any more.
usage: build_phase44.py IN.gbc OUT.gbc OUT.ips
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
import palhooks
import build_phase15 as P15
import build_phase17 as P17
import build_phase25 as P25
import build_phase28 as P28
import build_phase37 as P37
import build_phase41 as P41
import build_phase42 as P42
import routekit as RK

FIRST_FLAG = 481                   # 476-480: phase 43
FIRST_MAP = 145                    # 26:139-144 = phase 43
TBANK, BANK, PBANK = 0x5A, 0x59, 0x6A    # tilesets / events / palette routine
SPR = dict(P41.SPR)
NEW = ['CopycatsHouse1F', 'CopycatsHouse2F']
RED_ID = {'CopycatsHouse1F': 0xAF, 'CopycatsHouse2F': 0xB0}
OLD_SCENES = (0x4D012, 0x4D14F)
POKE_DOLL, TM_MIMIC, CHANSEY = 0x25, 0xDF, 113
VAR_FACING = 0x09


def palmap_len(bst):
    """palette map bytes a Gen I blockset needs (tiles 0-$5F; font tiles of the unused block 0 left out)"""
    b = open(PY + '/gfx/blocksets/' + bst, 'rb').read()
    used = [x for i in range(1, len(b) // 16) for x in b[16 * i:16 * i + 16] if x < 0x60]
    return max(used) // 2 + 1


def add_tileset(rom, sp, TS, ts, data_bank, pm_len, log, anim_src=5):
    """a tileset table entry (graphics, blocks, collision in data_bank; the palette map's used part in bank 13); its
    palettes are given to palhooks.rebuild"""
    i = TS.count(); assert i < P15.TS_CAP
    gfx = lz(ts.gfx_raw)
    a_g = sp.put(data_bank, gfx); a_m = sp.put(data_bank, ts.blocks); a_c = sp.put(data_bank, bytes(ts.coll))
    a_p = sp.put(0x13, ts.palmap[:pm_len])
    anim = TS.entry(anim_src)[9:11]
    rom[TS.tab + 15 * i:TS.tab + 15 * i + 15] = bytes([data_bank, a_g & 0xFF, a_g >> 8, data_bank, a_m & 0xFF, a_m >> 8,
                                                      data_bank, a_c & 0xFF, a_c >> 8]) + anim + b'\x00\x00' + bytes([a_p & 0xFF, a_p >> 8])
    log.append('tileset %s id %d (gfx %d bytes, %d blocks, palette map %d bytes)' % (ts.name, i, len(gfx), ts.nblocks, pm_len))
    return i


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (TBANK, BANK, PBANK):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    s_ = OLD_SCENES[1]
    while rom[s_ - 1] == 0xFF and s_ > OLD_SCENES[0]: s_ -= 1
    sp.set_area(0x13, s_ + 1, OLD_SCENES[1])
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1)
    got_tm31 = 0x800 + P42.FIRST_FLAG + 12                     # phase 42's (shared with its Crystal-room version)
    nid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(NEW)}
    saf = mapid('SaffronCity')

    # ================= tilesets: Dojo (Red 5) and Red's house (Red 1 / 4: same blocks and palette map)
    TS = PM.Tilesets(rom, sp)
    dts = Tileset('Dojo', 5, 'gym.bst', SC + '/out/pk_dojo.pkl')
    hts = Tileset('RedsHouse1', 1, 'reds_house.bst', SC + '/out/pk_redshouse1.pkl')
    dw, dh = RK.red_dims('FightingDojo'); dojo = MapPort('FightingDojo', dts, dw, dh, 'FightingDojo.blk')
    hmp = {}
    for n in NEW:
        w_, h_ = RK.red_dims(n); hmp[n] = MapPort(n, hts, w_, h_, n + '.blk')
    def ovr(ts, mp, n): return {(x, y): P25.warp_override(ts, mp, x, y) for x, y, d, wi in P25.red_objects(n)[1]}
    meta2, coll2, blks = pairwalls.variants(dts, bytes(dts.blocks), bytes(dts.coll), {'FightingDojo': dojo}, [],
                                            {'FightingDojo': ovr(dts, dojo, 'FightingDojo')})
    dts.blocks = meta2; dts.coll = bytearray(coll2); dts.nblocks = len(coll2) // 4; dojo.blk = blks['FightingDojo']
    meta2, coll2, blks = pairwalls.variants(hts, bytes(hts.blocks), bytes(hts.coll), hmp, [], {n: ovr(hts, hmp[n], n) for n in NEW})
    hts.blocks = meta2; hts.coll = bytearray(coll2); hts.nblocks = len(coll2) // 4
    for n in NEW: hmp[n].blk = blks[n]
    dojo_ts = add_tileset(rom, sp, TS, dts, TBANK, palmap_len('gym.bst'), log)
    house_ts = add_tileset(rom, sp, TS, hts, TBANK, palmap_len('reds_house.bst'), log)

    # ================= the palette hooks -> one routine (+ the two new tilesets)
    hooks, ld_ts, end = palhooks.parse(rom)
    hp = rom[HOUSEPAL_CALL:HOUSEPAL_CALL + 14]; wbg = hp[3:5]; fc = hp[12:14]
    pals = [(i, bytes(rom[fo(b, a):fo(b, a) + 64])) for i, (b, a) in hooks] + [(dojo_ts, dts.pals), (house_ts, hts.pals)]
    a = Asm(sp.here(PBANK)); a.bank = PBANK
    a.label('r'); a.raw(ld_ts); a.db(0x47, 0x21); a.dw('tab')                      # ld a, [wMapTileset] ; ld b, a ; ld hl, tab
    a.db(0x2A, 0xFE, 0xFF, 0x28, 0x07, 0xB8, 0x28, 0x06, 0x23, 0x23, 0x18, 0xF4)  # loop: ld a,[hli]; cp $ff; jr z,no; cp b; jr z,hit; inc hl x2; jr loop
    a.db(0xAF, 0xC9)                                                               # no: xor a (carry clear) ; ret
    a.db(0x2A, 0x66, 0x6F, 0x3E, 0x05, 0x11); a.raw(bytes(wbg)); a.db(0x01, 0x40, 0x00, 0xCD); a.raw(bytes(fc))
    # dark map (Rock Tunnel before Flash: wTimeOfDayPal = DARKNESS): BG palettes 0-6 black, as Red's darkness
    a.db(0xFA, 0x34, 0xD8, 0xE6, 0x03, 0xFE, 0x03, 0x20, 0x14)
    a.db(0xF0, 0x70, 0xF5, 0x3E, 0x05, 0xE0, 0x70, 0x21); a.raw(bytes(wbg)); a.db(0x06, 0x38, 0xAF, 0x22, 0x05, 0x20, 0xFC)
    a.db(0xF1, 0xE0, 0x70)
    a.db(0x37, 0xC9)                                                               # hit: hl = palettes; copy; scf ; ret
    a.label('tab')
    for i, pb in pals: a.db(i); a.dw('p%d' % i)
    a.db(0xFF)
    for i, pb in pals: a.label('p%d' % i); a.raw(pb)
    base = a.base; blob = a.done(); assert sp.put(PBANK, blob) == base
    hk = r16(LSMP + 1); ho = fo(0x12, hk)
    new = bytes([0x3E, PBANK, 0x21, base & 0xFF, base >> 8, 0xCF, 0xD8]) + ld_ts + bytes([0xC3, end & 0xFF, end >> 8])
    assert len(new) <= 16
    rom[ho:ho + len(new)] = new
    log.append('tileset palettes: %d in one table at %X:%04X' % (len(pals), PBANK, base))

    # ================= the Dojo: Red's room on Crystal's map
    ao = attrs(rom, hdr_index('FightingDojo'))['attr_off']
    rom[ao] = border_of('FightingDojo'); rom[ao + 3] = TBANK; w16(ao + 4, sp.put(TBANK, dojo.blk)); rom[hdr_index('FightingDojo') + 1] = dojo_ts

    # ================= the Copycat's house (new maps)
    K.bank = BANK
    K.alloc_headers(FIRST_MAP, len(NEW))
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    def T(lab, b, p): texts[lab] = RM.crystal_text(b, p); return lab
    def obj(o, lab, spr=None):
        mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        return [spr or SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, 0xFFFF]
    o1 = P25.red_objects('CopycatsHouse1F')[0]
    texts['c1_w'] = RK.Kit.rt(0xAF, 1); texts['c1_m'] = RK.Kit.rt(0xAF, 2); texts['c1_c'] = P37.text_then_asm(0xAF, 3)[0]
    a.label('c1w'); a.jumptextfaceplayer('c1_w')
    a.label('c1m'); a.jumptextfaceplayer('c1_m')
    a.label('c1c'); a.opentext(); a.writetext('c1_c'); a.cry(CHANSEY); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    ob1 = [obj(o1[0], 'c1w'), obj(o1[1], 'c1m'), obj(o1[2], 'c1c')]
    o2 = P25.red_objects('CopycatsHouse2F')[0]
    T('cc_hi', 0x17, 0x5CF6); T('cc_doll', 0x17, 0x5D78); T('cc_full', 0x17, 0x5E4E); T('cc_after', 0x17, 0x5DFD)
    texts['cc_dd'] = RK.Kit.rt(0xB0, 2); texts['cc_toy'] = RK.Kit.rt(0xB0, 3); texts['cc_snes'] = RK.Kit.rt(0xB0, 6)
    T('cc_diary', 0x17, 0x5EEA); T('cc_cant', 0x17, 0x5F2B)
    a.label('cc'); a.faceplayer(); a.opentext(); a.checkevent(got_tm31); a.iftrue('cc_a')
    a.checkitem(POKE_DOLL); a.iftrue('cc_d')
    a.writetext('cc_hi'); a.waitbutton(); a.closetext(); a.end()
    a.label('cc_d'); a.writetext('cc_doll'); a.promptbutton(); a.verbosegiveitem(TM_MIMIC, 1); a.iffalse('cc_f')
    a.db(0x20, POKE_DOLL, 1); a.setevent(got_tm31); a.closetext(); a.end()                       # takeitem
    a.label('cc_f'); a.writetext('cc_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('cc_a'); a.writetext('cc_after'); a.waitbutton(); a.closetext(); a.end()
    a.label('ccd'); a.jumptextfaceplayer('cc_dd')
    a.label('cct'); a.jumptext('cc_toy')
    a.label('ccs'); a.jumptext('cc_snes')
    a.label('ccp'); a.db(0x1C, VAR_FACING); a.ifequal(1, 'ccp_u'); a.jumptext('cc_cant')
    a.label('ccp_u'); a.jumptext('cc_diary')
    assert [o['sprite'] for o in o2] == ['SPRITE_BRUNETTE_GIRL', 'SPRITE_BIRD', 'SPRITE_MONSTER', 'SPRITE_BIRD', 'SPRITE_FAIRY']
    ob2 = [obj(o2[0], 'cc'), obj(o2[1], 'ccd'), obj(o2[2], 'cct'), obj(o2[3], 'cct'), obj(o2[4], 'cct')]
    bg2 = [(y, x, 0, 'ccs' if 'SNES' in t else 'ccp') for x, y, t in P25.red_objects('CopycatsHouse2F')[2]]
    red_i = [i + 1 for i, w_ in enumerate(P25.red_objects('SaffronCity')[1]) if w_[2] == 'COPYCATS_HOUSE_1F'][0]
    K.put_texts(a, texts)
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    w1 = [W(x, y, red_i, saf) if d == 'LAST_MAP' else W(x, y, wi, nid['CopycatsHouse2F']) for x, y, d, wi in P25.red_objects('CopycatsHouse1F')[1]]
    w2 = [W(x, y, wi, nid['CopycatsHouse1F']) for x, y, d, wi in P25.red_objects('CopycatsHouse2F')[1]]
    K.emit(a, 'CopycatsHouse1F', w1, [], [], ob1, [])
    K.emit(a, 'CopycatsHouse2F', w2, [], bg2, ob2, [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Copycat\'s house: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    for i, n in enumerate(NEW):
        K.make_map(FIRST_MAP + i, hmp[n], house_ts, border_of(n), n, 3, a, n)
    # Saffron's door
    cw = mapid('CopycatsHouse1F')
    assert K.fix_warps('SaffronCity', lambda i, w_: (1, nid['CopycatsHouse1F']) if (w_[3], w_[4]) == cw else None) == 1

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
