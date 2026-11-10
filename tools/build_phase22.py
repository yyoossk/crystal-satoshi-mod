#!/usr/bin/env python3
"""Phase 22: Route 20 as in Red / the Pikachu full-color hack, for good (also after the Hall of Fame):
Red's layout on the Gen I overworld tileset, its two Seafoam Islands caves, Red's 10 trainers (Jr. Trainer F =
phase 10's ガールスカウト class), the two signs, Red's water Pokémon.  Crystal's Seafoam Gym is no longer reached.
Connections: Cinnabar Island (Red's, both ways with Red's blocks) and Crystal's Route 19 (sea drawn on both sides,
as their tilesets differ).  Crystal's callback that clears Route 19's rocks is kept.
usage: build_phase22.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import pkmap
import portmaps as PM
import build_phase10 as P10
import build_phase12 as P12
import build_phase13 as P13
import build_phase17 as P17

FIRST_FLAG = 153
OVERWORLD_TS = 40
RED_ROUTE20 = 0x1F
W, H = 50, 9
SEAFOAM_1F = (26, 63)
EV_ROCKS_CLEARED = 0x00D7            # Crystal: Route20ClearRocksCallback
W_OVERWORLDMAPBLOCKS = 0xC800
SEA = 0x43                           # sea block in both tilesets
ROUTE19_SEA_STRIP = (0x2A, 0x6F0B)   # Crystal map blocks (bank 2A) where 12 rows x 3 columns (stride 10) are all sea
KANTO_WATER_ROUTE20 = 0x2BD56        # Crystal's water table entry for Route 20 (moved by phase 12)
TENTACOOL = 0x48
SPR_SWIMMER = 0x31                   # Crystal SPRITE_SWIMMER_GUY (Red's SPRITE_SWIMMER)
FEMALE = ['ミナミ', 'アユミ', 'サトミ', 'ユカリ', 'マユミ', 'ナツキ', 'チアキ', 'カオリ', 'ハルカ', 'リエ']
PAD = 3                              # MAP_CONNECTION_PADDING_WIDTH


def connection(direction, cur_w, cur_h, tgt, tgt_w, tgt_h, off, strip):
    """pokecrystal's `connection` macro; strip = address of the strip's first block (the caller decides)"""
    src = 0; tg = off + PAD
    if tg < 0: src = -tg; tg = 0
    if direction == 'west':
        mp = (cur_w + 2 * PAD) * tg; win = (tgt_w + 2 * PAD) * 2 - 2 * PAD
        y, x = -2 * off, tgt_w * 2 - 1; ln = min(cur_h + PAD - off, tgt_h)
    elif direction == 'east':
        mp = (cur_w + 2 * PAD) * tg + cur_w + PAD; win = tgt_w + 2 * PAD + 1
        y, x = -2 * off, 0; ln = min(cur_h + PAD - off, tgt_h)
    else:
        raise ValueError(direction)
    return bytes([*tgt, strip & 0xFF, strip >> 8, (W_OVERWORLDMAPBLOCKS + mp) & 0xFF, (W_OVERWORLDMAPBLOCKS + mp) >> 8,
                  ln - src, tgt_w, y & 0xFF, x & 0xFF, (W_OVERWORLDMAPBLOCKS + win) & 0xFF, (W_OVERWORLDMAPBLOCKS + win) >> 8])


def strip_src(direction, tgt_w, off):
    src = max(0, -(off + PAD))
    return tgt_w * src + (tgt_w - PAD if direction == 'west' else 0)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x61, 0x63, 0x78, 0x79):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    n = 'Route20'; g = RED_ROUTE20
    r20, cin, r19 = mapid('Route20'), mapid('CinnabarIsland'), mapid('Route19')
    h20 = hdr_index('Route20')
    old = attrs(rom, h20)
    so = fo(old['scbank'], old['scripts'])
    assert rom[so] == 0 and rom[so + 1] == 1 and rom[so + 2] == 5
    cbo = fo(old['scbank'], r16(so + 3)); assert rom[cbo:cbo + 4] == bytes([0x33, EV_ROCKS_CLEARED & 0xFF, EV_ROCKS_CLEARED >> 8, 0x8F])

    # ================= blocks + warp collision (Gen I overworld tileset of phase 19)
    TS = PM.Tilesets(rom, sp)
    ow = Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)
    assert rom[hdr_index('CinnabarIsland') + 1] == OVERWORLD_TS
    co = TS.coll_off(OVERWORLD_TS)
    coll = {'Overworld': bytearray(rom[co:co + 4 * ow.nblocks])}
    mp = MapPort(n, ow, W, H, 'Route20.blk')
    assert (pkmap.header(g)['w'], pkmap.header(g)['h']) == (W, H)
    PM.warp_collisions({n: mp}, lambda m: PM.objects_of(m)[:3], log, coll)
    rom[co:co + len(coll['Overworld'])] = coll['Overworld']
    blkp = sp.put(0x61, mp.blk)

    # ================= trainer parties (bank 7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    objs, warps, skip, bgl = PM.objects_of(n)
    party_of = {}
    for i, o in enumerate(objs):
        c = o['extra'][0][4:]; k = int(o['extra'][1]); cid = PM.TCLS[c]
        pool = FEMALE if c in ('BEAUTY', 'JR_TRAINER_F') else PM.NAMEPOOL
        groups[cid - 1].append([encode(pool[(i + 3) % len(pool)] + '@'), pb(PM.red_party(c, k))])
        party_of[i] = (cid, len(groups[cid - 1]))
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= scripts / events
    a = Asm(sp.here(0x63)); texts = {}; obj_bytes = []; bgs = []
    a.label('cb_rocks'); a.setevent(EV_ROCKS_CLEARED); a.endcallback()
    for idx, o in enumerate(objs):
        tid = idx + 1; lab = 'o%d' % tid
        sprite = SPR_SWIMMER if o['sprite'] == 'SPRITE_SWIMMER' else PM.SPR[o['sprite']]
        sight, seen, aft, win = P12.trainer_texts(g, tid)
        fl = FL.new(); cid, pid = party_of[idx]
        a.label(lab); a.dw(fl); a.db(cid, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
        a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
        texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
        obj_bytes.append([sprite, o['y'] + 4, o['x'] + 4, P12.FACE.get(o['face'], 6), 0, 0xFF, 0xFF, 2, sight, lab, fl])
    for k, (x, y, tconst) in enumerate(bgl):
        b_, p_ = pkmap.text_ptr(g, len(objs) + k + 1); k_, body = pkmap.text_body(b_, p_); assert k_ == 'text'
        L = 'bg%d' % k; a.label(L); a.jumptext(L + 't'); texts[L + 't'] = body
        bgs.append((y, x, 0, L))
    for k_, v in texts.items():
        a.label(k_); a.raw(P12.text(v))
    a.label('mapscripts'); a.db(0, 1, 5); a.dw('cb_rocks')               # MAPCALLBACK_NEWMAP
    a.label('events'); a.db(0, 0)
    a.db(len(warps))
    for x, y, dest, wid in warps:
        assert dest == 'SEAFOAM_ISLANDS_1F'; a.db(y, x, wid, *SEAFOAM_1F)
    a.db(0)
    a.db(len(bgs))
    for (y, x, f_, l_) in bgs: a.db(y, x, f_); a.dw(l_)
    a.db(len(obj_bytes))
    for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
    base = a.base; blob = a.done(); assert sp.put(0x63, blob) == base

    # ================= attributes + connections
    ca = attrs(rom, hdr_index('CinnabarIsland'))
    assert (ca['w'], ca['h'], ca['blkbank']) == (10, 9, 0x60)
    r19a = attrs(rom, hdr_index('Route19')); assert (r19a['w'], r19a['h']) == (10, 18)
    sb, sa = ROUTE19_SEA_STRIP
    assert all(rom[fo(sb, sa) + 10 * r + c] == SEA for r in range(12) for c in range(3))
    assert r19a['blkbank'] == sb
    west = connection('west', W, H, cin, 10, 9, 0, ca['blk'] + strip_src('west', 10, 0))
    east = connection('east', W, H, r19, 10, 18, -9, sa)
    attr = bytes([old['border'], H, W, 0x61, blkp & 0xFF, blkp >> 8, 0x63, a.labels['mapscripts'] & 0xFF,
                  a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0x02 | 0x01]) + west + east
    aa = sp.put(0x61, attr)
    rom[h20] = 0x61; w16(h20 + 3, aa); rom[h20 + 1] = OVERWORLD_TS
    # Cinnabar's east side: Red's Route 20 blocks
    def patch(owner, tgt, new):
        oa = attrs(rom, hdr_index(owner)); ao = oa['attr_off']
        for k in range(bin(oa['conn'] & 0xF).count('1')):
            c = ao + 12 + 12 * k
            if (rom[c], rom[c + 1]) == tgt: rom[c:c + 12] = new; return
        raise AssertionError((owner, tgt))
    patch('CinnabarIsland', r20, connection('east', 10, 9, r20, W, H, 0, blkp + strip_src('east', W, 0)))
    # Route 19's west side: sea (Route 20 is on another tileset)
    rows = min(18 + PAD - 9, H)
    sea19 = sp.put(0x61, bytes([SEA]) * (W * (rows - 1) + PAD))
    patch('Route19', r20, connection('west', 10, 18, r20, W, H, 9, sea19))
    log.append('Route20: Red layout %dx%d (tileset %d), attributes 61:%04X, events 63:%04X (%d bytes)'
               % (W, H, OVERWORLD_TS, aa, base, len(blob)))

    # ================= water Pokémon: Red's sea routes (Tentacool Lv 5-40, rate 5) -> Crystal's 3 slots
    o = KANTO_WATER_ROUTE20
    assert rom[o:o + 3] == bytes([*r20, 0x0F])
    red = [5, 10, 15, 5, 10, 15, 20, 30, 35, 40]
    rom[o + 2:o + 9] = bytes([5, red[0], TENTACOOL, red[2], TENTACOOL, red[7], TENTACOOL])

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
