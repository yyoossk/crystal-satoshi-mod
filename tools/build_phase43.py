#!/usr/bin/env python3
"""Phase 43: the Underground Path as in Red / the Pikachu full-color hack (new maps; Crystal's no longer reached):
 * the four entrance houses on Routes 5, 6, 7 and 8 (Red's people; Route 5: the Nidoran♀ <-> Nidoran♂ trade),
 * the north-south and west-east tunnels (Red's Underground tileset, new), their hidden items.
 Phase 34's routes lead into them.
usage: build_phase43.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import redtexts as RT
from evedit import MapEvents
import build_phase15 as P15
import build_phase17 as P17
import build_phase19 as P19
import build_phase25 as P25
import build_phase28 as P28
import build_phase34 as P34
import build_phase40 as P40
import build_phase41 as P41
import routekit as RK

FIRST_FLAG = 476                   # 462-475: phase 42
FIRST_MAP = P34.UNDERGROUND_FIRST_MAP          # 26:139-144 (26:138 = phase 42)
TBANK, BANK, DBANK, UBANK = 0x79, 0x66, 0x62, 0x63
GATE_TS = 47
SPR = dict(P41.SPR)
NEW = ['UndergroundPathRoute5', 'UndergroundPathRoute6', 'UndergroundPathRoute7', 'UndergroundPathRoute8',
       'UndergroundPathNorthSouth', 'UndergroundPathWestEast']
RED_ID = {'UndergroundPathRoute5': 0x47, 'UndergroundPathRoute6': 0x4A, 'UndergroundPathRoute7': 0x4D,
          'UndergroundPathRoute8': 0x50, 'UndergroundPathNorthSouth': 0x77, 'UndergroundPathWestEast': 0x79}
CONST = {'UNDERGROUND_PATH_ROUTE_%d' % k: 'UndergroundPathRoute%d' % k for k in (5, 6, 7, 8)}
CONST.update({'UNDERGROUND_PATH_NORTH_SOUTH': 'UndergroundPathNorthSouth', 'UNDERGROUND_PATH_WEST_EAST': 'UndergroundPathWestEast'})
NIDORAN_F, NIDORAN_M = 29, 32
OLD_SCENES = (0x4D012, 0x4D14F)    # bank 13: phase 28's old scene table (phase 40 took its start for a palette map)


def add_tileset(rom, sp, TS, ts, data_bank, log, anim_src=5):
    """phase 40's add_tileset with a 16-byte hook (jp nz) for the last bytes of bank 12"""
    def r16(o): return rom[o] | rom[o + 1] << 8
    i = TS.count(); assert i < P15.TS_CAP
    gfx = lz(ts.gfx_raw)
    a_g = sp.put(data_bank, gfx); a_m = sp.put(data_bank, ts.blocks); a_c = sp.put(data_bank, bytes(ts.coll))
    a_p = sp.put(0x13, ts.palmap)
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
    a.raw(ld_ts); a.db(0xFE, i, 0xC2); a.dw(prev)                                         # cp i ; jp nz, prev
    a.db(0x3E, data_bank, 0x21); a.dw(cp); a.db(0xCF, 0x37, 0xC9)                        # farcall; scf; ret
    blob = a.done(); assert len(blob) == 16
    hk = sp.put(0x12, blob); rom[LSMP + 1] = hk & 0xFF; rom[LSMP + 2] = hk >> 8
    log.append('tileset %s id %d (gfx %d bytes, %d blocks)' % (ts.name, i, len(gfx), ts.nblocks))
    return i


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (TBANK, BANK, DBANK, UBANK, 0x12, 0x3F):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    s_ = OLD_SCENES[1]
    while rom[s_ - 1] == 0xFF and s_ > OLD_SCENES[0]: s_ -= 1
    sp.set_area(0x13, s_ + 1, OLD_SCENES[1])
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1); K.dbank = DBANK
    nid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(NEW)}

    # ================= Red's trade: Nidoran♀ -> Nidoran♂ (JP Red's tenth trade)
    ref = P19.NPC_TRADES_REF; assert rom[ref] == 0x21
    to = fo(0x3F, r16(ref + 1)); nt = 7 + len(P19.RED_TRADES) + 4
    table = bytearray(rom[to:to + 16 * nt])
    assert RT.R[0x7208B:0x7208E] == bytes([0x0F, 0x03, 0x02])
    nick = bytes(RT.R[0x7208B + 3:0x7208B + 7])
    table += bytes([0, NIDORAN_F, NIDORAN_M]) + nick + bytes([0x96, 0x66, 0x00]) + (31415 + 1111 * nt).to_bytes(2, 'little') + \
        encode('ゴロウ')[:3] + b'\x00'
    trade_spot = nt
    w16(ref + 1, sp.put(0x3F, bytes(table)))

    # ================= tilesets: the entrances (Gate), the tunnels (Underground, new)
    gts = Tileset('Gate', 12, 'gate.bst', SC + '/out/pk_gate.pkl')
    uts = Tileset('Underground', 11, 'underground.bst', SC + '/out/pk_underground.pkl')
    nmp = {}
    for n in NEW:
        w_, h_ = RK.red_dims(n); ts = gts if 'Route' in n else uts
        if n == 'UndergroundPathNorthSouth': h_ = 23                    # (Red: the blocks are 4x23)
        nmp[n] = MapPort(n, ts, w_, h_, n + '.blk')
    def ovr(ts, n): return {(x, y): P25.warp_override(ts, nmp[n], x, y, ts is uts) for x, y, d, wi in P25.red_objects(n)[1]}
    ents = {n: nmp[n] for n in NEW if 'Route' in n}
    K.ts_variants(GATE_TS, gts, ents, {n: ovr(gts, n) for n in ents})
    import pairwalls
    tun = {n: nmp[n] for n in NEW if 'Route' not in n}
    meta2, coll2, blks = pairwalls.variants(uts, bytes(uts.blocks), bytes(uts.coll), tun, [], {n: ovr(uts, n) for n in tun})
    uts.blocks = meta2; uts.coll = bytearray(coll2); uts.nblocks = len(coll2) // 4
    for n in tun: nmp[n].blk = blks[n]
    TS = PM.Tilesets(rom, sp)
    ug_ts = add_tileset(rom, sp, TS, uts, UBANK, log)
    K.bank = BANK
    K.alloc_headers(FIRST_MAP, len(NEW))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    def trade(a, texts, lab, o):
        a.label(lab); a.faceplayer(); a.opentext(); a.db(0x95, trade_spot); a.waitbutton(); a.closetext(); a.end()
        return None, 0, 0xFFFF, 0
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    for n in NEW:
        ob, bgs = K.red_events(a, texts, n, RED_ID[n], n[13:] + '_', {1: trade} if n == 'UndergroundPathRoute5' else {}, SPR)
        rn = 'Route' + n[-1] if 'Route' in n else None
        ws = [W(x, y, wi, mapid(rn) if d == 'LAST_MAP' else nid[CONST[d]]) for x, y, d, wi in P25.red_objects(n)[1]]
        K.emit(a, n, ws, [], bgs, ob, [])
    K.put_texts(a, texts)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Underground Path: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    for i, n in enumerate(NEW):
        ent = 'Route' in n
        K.make_map(FIRST_MAP + i, nmp[n], GATE_TS if ent else ug_ts, border_of(n),
                   'Route5UndergroundPathEntrance' if ent else 'UndergroundPath', 6 if ent else 4, a, n)

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
