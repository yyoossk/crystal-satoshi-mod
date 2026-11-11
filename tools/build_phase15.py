#!/usr/bin/env python3
"""Phase 15:
 * 800 more event flags (0x800-0xB1F) in the unused saved WRAM just before wEventFlags (EventFlagAction hook).
 * Mt. Moon 1F/B1F/B2F ported from the Pikachu full-color hack (CAVERN tileset), Red's trainers, the super nerd
   and the fossils (new key items), the Pikachu version's Jessie & James on B2F, wild Pokémon (Yellow).
   Route 3 / Route 4 lead to it until the Kanto Hall of Fame, afterwards to Crystal's own Mt. Moon (Johto part).
usage: build_phase15.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode, decode
import pkmap
import build_phase10 as P10
import build_phase11 as P11
import build_phase12 as P12
import build_phase13 as P13
import build_phase14 as P14

ITEM = load_consts(PC + '/constants/item_constants.asm')
MON = load_consts(PC + '/constants/pokemon_constants.asm')
FREE_EV = json.load(open(SC + '/out/free_events.json'))
EXT_FLAGS = list(range(0x800, 0x800 + 94 * 8))       # new flag range (DA01-DA5E; DA5F-DA64 = scene bytes, phases 21/23/24)
EVI = [0]
def newflag():
    f = EXT_FLAGS[EVI[0]]; EVI[0] += 1; return f

W_EVENTFLAGS, W_EXTFLAGS = 0xDA65, 0xDA01
EFA = 0x2E41                       # EventFlagAction: ld hl,wEventFlags / call FlagAction / ret
FLAGACTION = 0x2E48
DLBR = (0x2B953, 0x2BA3D)          # DetermineLinkBattleResult (bank 0A) -> moved to bank 0x76
DLBR_FARCALL = 0x3F7DD
KANTO_GRASS = 0x2B297
EV_KANTO_HOF = 0x34A; W_WARPS_PTR = 0xDBC2
TS_CAP = 48                        # tileset table capacity (bank 0x13)
OLD_TS_HOLE = (0x4D405, 0x4D405 + 15 * 33)   # the original table's place (free, for palette maps)

GRUNTM, JJ = 31, 72
CLS = {'OPP_HIKER': 0x2C, 'OPP_YOUNGSTER': 0x16, 'OPP_LASS': 0x19, 'OPP_SUPER_NERD': 0x29, 'OPP_BUG_CATCHER': 0x24,
       'OPP_ROCKET': GRUNTM}
RED_DATA = {'OPP_HIKER': 'HikerData', 'OPP_YOUNGSTER': 'YoungsterData', 'OPP_LASS': 'LassData',
            'OPP_SUPER_NERD': 'SuperNerdData', 'OPP_BUG_CATCHER': 'BugCatcherData', 'OPP_ROCKET': 'RocketData'}
NAMES = {'OPP_HIKER': ['ゴロウ'], 'OPP_YOUNGSTER': ['ジョウジ'], 'OPP_LASS': ['イズミ', 'ミユキ'],
         'OPP_SUPER_NERD': ['ミノル', 'ヒデキ'], 'OPP_BUG_CATCHER': ['ケント', 'ヨシノブ'], 'OPP_ROCKET': ['したっぱ']}
HELIX_FOSSIL, DOME_FOSSIL = 0x8D, 0x8E
MOON = [('MtMoon1F', 0x3B), ('MtMoonB1F', 0x3C), ('MtMoonB2F', 0x3D)]
SPR = dict(P14.SPR)
SPR.update({'SPRITE_HIKER': 0x50 if False else 0x2D, 'SPRITE_YOUNGSTER': 0x27, 'SPRITE_COOLTRAINER_F': 0x24,
            'SPRITE_SUPER_NERD': 0x2B, 'SPRITE_FOSSIL': 0x67 + 4})
TM_NUM = {'TM_WATER_GUN': 11, 'TM_MEGA_PUNCH': 1}


def item_id(n):
    if n in TM_NUM: return P12.tm_item(TM_NUM[n])
    return P14.item_id(n)


DLBR_BANK = 0x60                 # empty bank in JP Crystal (keeps 0x76 free for map scripts)


def install_hof_switch(rom, sp, mapname, warp_fix, log):
    """after the Kanto Hall of Fame, warps listed in warp_fix {index: 5 bytes} replace the map's current ones
    (wCurMapWarpEventsPointer swapped from a NEWMAP/CMDQUEUE callback)"""
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    a_ = attrs(rom, hdr_index(mapname)); sb = a_['scbank']
    ev = parse_events(rom, sb, a_['events'])
    alt = bytearray(b''.join(w for _, w in ev['warps']))
    for i, wb in warp_fix.items():
        alt[5 * i:5 * i + 5] = wb
    f, _ = bank_free_tail(rom, sb)
    if sb not in sp.cur: sp.set_area(sb, f + 1, sb * 0x4000 + 0x4000)
    a_alt = sp.put(sb, bytes(alt))
    fb = W_EVENTFLAGS + (EV_KANTO_HOF >> 3); bit = EV_KANTO_HOF & 7
    a = Asm(sp.here(0x78))
    a.db(0xFA); a.dw(fb); a.db(0xCB, 0x47 | (bit << 3), 0xC8)
    a.db(0x21); a.dw(a_alt); a.db(0x7D, 0xEA); a.dw(W_WARPS_PTR); a.db(0x7C, 0xEA); a.dw(W_WARPS_PTR + 1); a.db(0xC9)
    fn = sp.put(0x78, a.done())
    so = fo(sb, a_['scripts'])
    nsc = rom[so]; scenes = bytes(rom[so + 1:so + 1 + 4 * nsc])
    cbo = so + 1 + 4 * nsc; ncb = rom[cbo]
    cbs = [(rom[cbo + 1 + 3 * k], r16(cbo + 2 + 3 * k)) for k in range(ncb)]
    old_new = [p for t, p in cbs if t == 5]; old_cq = [p for t, p in cbs if t == 3]
    rest = [(t, p) for t, p in cbs if t not in (3, 5)]
    a = Asm(sp.here(sb))
    a.db(nsc); a.raw(scenes); a.db(len(rest) + 2)
    for t, p in rest:
        a.db(t); a.dw(p)
    a.db(0x05); a.dw('nm'); a.db(0x03); a.dw('cq')
    a.label('nm'); a.callasm(0x78, fn)
    if old_new: a.sjump(old_new[0])
    else: a.endcallback()
    a.label('cq'); a.callasm(0x78, fn)
    if old_cq: a.sjump(old_cq[0])
    else: a.endcallback()
    nh = sp.put(sb, a.done()); assert nh == a.base
    w16(a_['attr_off'] + 7, nh)
    log.append('%s: after the Hall of Fame warps %s are restored (%X:%04X)' % (mapname, sorted(warp_fix), sb, nh))


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    log = []

    # ================= DetermineLinkBattleResult -> bank 0x79 (frees room after the Kanto grass table)
    lo, hi = DLBR
    from jpfind import L as OPLEN
    f76, _ = bank_free_tail(rom, DLBR_BANK); dst = f76 + 1
    code = bytearray(rom[lo:hi]); delta = (dst % 0x4000) - (lo % 0x4000)
    i = 0
    while i < len(code):                       # internal calls -> relocated
        op = code[i]; n_ = OPLEN[op]
        if n_ == 3 and op in (0xCD, 0xC3, 0xC2, 0xCA, 0xD2, 0xDA, 0xC4, 0xCC, 0xD4, 0xDC):
            t = code[i + 1] | code[i + 2] << 8
            if 0x4000 + lo % 0x4000 <= t < 0x4000 + hi % 0x4000:
                t += delta; code[i + 1] = t & 0xFF; code[i + 2] = t >> 8
        i += n_
    rom[dst:dst + len(code)] = code
    assert rom[DLBR_FARCALL] == 0x0A and r16(DLBR_FARCALL + 2) == 0x4000 + lo % 0x4000
    rom[DLBR_FARCALL] = DLBR_BANK; w16(DLBR_FARCALL + 2, 0x4000 + dst % 0x4000)
    rom[lo:hi] = bytes(hi - lo)
    for b in (0x13, 0x12, 0x7C, 0x7D, 0x78, 0x79, 0x7A, 0x77, 0x76, 0x75, 0x62):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)

    # ================= extended event flags
    assert rom[EFA:EFA + 7] == bytes([0x21, W_EVENTFLAGS & 0xFF, W_EVENTFLAGS >> 8, 0xCD, FLAGACTION & 0xFF, FLAGACTION >> 8, 0xC9])
    a = Asm(sp.here(0x78))
    a.db(0x7A, 0xFE, 0x08, 0x38, 0x09)                      # ld a,d ; cp 8 ; jr c,.old
    a.db(0xD6, 0x08, 0x57, 0x21); a.dw(W_EXTFLAGS); a.db(0xC3); a.dw(FLAGACTION)
    a.db(0x21); a.dw(W_EVENTFLAGS); a.db(0xC3); a.dw(FLAGACTION)
    efa = sp.put(0x78, a.done())
    rom[EFA:EFA + 7] = bytes([0x3E, 0x78, 0x21, efa & 0xFF, efa >> 8, 0xCF, 0xC9])
    js = json.load(open(SC + '/out/free_events.json'))
    log.append('event flags 0x800-0xB1F (DA01-DA64) via 78:%04X' % efa)

    # ================= tileset CAVERN
    tab_ptr = r16(R_TILESETS[0]); tab_o = fo(0x13, tab_ptr); ntab = 37
    old_tab = bytes(rom[tab_o:tab_o + 15 * ntab])
    ts = Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl')
    maps = {}
    for n, g in MOON:
        h = pkmap.header(g); maps[n] = MapPort(n, ts, h['w'], h['h'], n + '.blk')
    for n, mp in maps.items():
        objs, warps = P11.objects_of(n)
        for (x, y, dest, wid) in warps:
            b_, q = mp.block_at(x, y); tile = ts.quad_tile(b_, q)
            if tile in ts.warp_tiles:                         # ladders (even on the map edge)
                v = COLL_STAIRCASE
            elif y == mp.h * 2 - 1 or y == 0 or x == 0 or x == mp.w * 2 - 1:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            else:
                raise AssertionError((n, x, y, hex(tile)))
            old = ts.coll[4 * b_ + q]
            assert old in (COLL_FLOOR, COLL_WALL, v), (n, x, y, hex(old), hex(v))
            ts.coll[4 * b_ + q] = v
    gfx = lz(ts.gfx_raw)
    a_gfx = sp.put(0x7C, gfx); a_meta = sp.put(0x62, ts.blocks); a_coll = sp.put(0x62, bytes(ts.coll))
    anim_none = old_tab[15 * 5 + 9:15 * 5 + 11]
    TS_ID = ntab
    new_tab = bytearray(old_tab + bytes([0x7C, a_gfx & 0xFF, a_gfx >> 8, 0x62, a_meta & 0xFF, a_meta >> 8, 0x62, a_coll & 0xFF, a_coll >> 8]) +
                        anim_none + b'\x00\x00\x00\x00')
    # bank 0x13 is nearly full: re-lay the mod's palette maps, the tileset table and the CheckBattleScene hook
    # contiguously in the area the mod uses (from phase 11's start)
    R0, R1 = 0x4F9CB, 0x50000
    pms = {}
    for i in range(33, ntab):
        p_ = new_tab[15 * i + 13] | new_tab[15 * i + 14] << 8
        pms[i] = bytes(rom[fo(0x13, p_):fo(0x13, p_) + 0x70])
    pms[TS_ID] = ts.palmap
    H_SCENE = P13.H_SCENE
    assert rom[H_SCENE] == 0xC3
    tr_o = fo(0x13, r16(H_SCENE + 1)); tramp = bytearray(rom[tr_o:tr_o + 15])
    assert tramp[12] == 0xC3 and tramp[0] == 0x3E
    rom[R0:R1] = bytes(R1 - R0)
    cur = R0
    def put13(data):
        nonlocal cur
        o = cur; rom[o:o + len(data)] = data; cur += len(data); return 0x4000 + o % 0x4000
    # tileset table with room for TS_CAP entries (later phases fill entries in place)
    tab_at = cur; cur += 15 * TS_CAP
    for i, pm in pms.items():
        pa = put13(pm); new_tab[15 * i + 13] = pa & 0xFF; new_tab[15 * i + 14] = pa >> 8
    w16(H_SCENE + 1, put13(bytes(tramp)))
    rom[tab_at:tab_at + len(new_tab)] = new_tab
    w16(R_TILESETS[0], 0x4000 + tab_at % 0x4000)
    sp.set_area(0x13, cur, R1)
    log.append('bank 0x13 re-laid: %d bytes free' % (R1 - cur))
    prev_hook = r16(LSMP + 1)
    hp = rom[HOUSEPAL_CALL:HOUSEPAL_CALL + 14]; wbgpals = hp[3:5]; farcopy = hp[12:14]
    ph = fo(0x12, prev_hook); ld_ts = bytes(rom[ph:ph + 3])
    a_pc = sp.put(0x12, ts.pals)
    a = Asm(sp.here(0x12))
    a.raw(ld_ts); a.db(0xFE, TS_ID, 0x28, 0x03); a.db(0xC3); a.dw(prev_hook)
    a.db(0x21); a.dw(a_pc); a.db(0x3E, 0x05, 0x11); a.raw(wbgpals); a.db(0x01, 0x40, 0x00, 0xCD); a.raw(farcopy); a.db(0x37, 0xC9)
    w16(LSMP + 1, sp.put(0x12, a.done()))
    log.append('tileset Cavern id %d (gfx %d bytes, %d blocks)' % (TS_ID, len(gfx), ts.nblocks))

    # ================= map headers 26:37-39
    u = US.get(); G = u.groups()
    first_new = 37
    lo_, hi_ = GROUP26_END + 9 * (first_new - G26_COUNT - 1), GROUP26_END + 9 * (first_new - G26_COUNT - 1 + len(MOON))
    moved = 0
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else first_new - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi_ and ao + size > lo_:
                rom[hdr] = 0x79; w16(hdr + 3, sp.put(0x79, bytes(rom[ao:ao + size]))); moved += 1
    rom[lo_:hi_] = bytes(hi_ - lo_)
    mapids = {n: (G26, first_new + i) for i, (n, g) in enumerate(MOON)}
    r3, r4 = mapid('Route3'), mapid('Route4')

    # ================= wild Pokémon (Yellow) -> Kanto grass table
    p = KANTO_GRASS
    while rom[p] != 0xFF: p += 47
    ent = b''
    for n, g in MOON:
        t = open(PY + '/data/wild/maps/%s.asm' % n, encoding='utf-8').read()
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        e = bytes([*mapids[n], rate, rate, rate]) + bytes(sum(([lv, MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
        ent += e
    assert lo - p < 320            # left-over copy of the Kanto water tables (moved by phase 12) up to the old DLBR
    rom[p + 1:lo] = bytes(lo - p - 1)
    assert p + len(ent) + 1 <= hi, 'no room for wild data'
    rom[p:p + len(ent) + 1] = ent + b'\xff'
    log.append('Mt. Moon wild data (%d bytes)' % len(ent))

    # ================= trainer parties (bank 7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, MON[P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    party_of = {}; nidx = {}
    for n, g in MOON:
        objs, _ = P11.objects_of(n)
        for o in objs:
            if o['extra'] and o['extra'][0] in CLS:
                c, k = o['extra'][0], int(o['extra'][1])
                data = P11.red_parties(RED_DATA[c])
                i = nidx.get(c, 0); nidx[c] = i + 1
                groups[CLS[c] - 1].append([encode(NAMES[c][i % len(NAMES[c])] + '@'), pb(data[k - 1])])
                party_of[(n, o['text'])] = (CLS[c], len(groups[CLS[c] - 1]))
    free = P13.write_groups7e(rom, groups)
    log.append('trainer parties added (bank 7E free %d)' % free)

    # ================= maps
    landmark = rom[hdr_index('Route3') + 5]
    music = rom[hdr_index('MountMoon') + 6]
    for n, mp in maps.items():
        g = dict(MOON)[n]
        objs, warps = P11.objects_of(n)
        sb = next(b for b in (0x7A, 0x79, 0x77) if sp.cur[b][1] - sp.cur[b][0] > 2200)
        a = Asm(sp.here(sb))
        callbacks = []; coords = []; bgs = []; texts = {}; obj_bytes = []
        oid = {}; oflag = {}
        for idx, o in enumerate(objs):
            tid = idx + 1
            if o['sprite'] in ('SPRITE_POKE_BALL', 'SPRITE_FOSSIL'): oflag[tid] = newflag()
            oid.setdefault(o['sprite'], []).append(tid)
        if 'SPRITE_JAMES' in oid:
            jjv = newflag()
            for t_ in oid['SPRITE_JAMES'] + oid['SPRITE_JESSIE']: oflag[t_] = jjv
        nerd_beat = None
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid
            sprite = SPR[o['sprite']]; mv = P12.FACE.get(o['face'], 6) if o['move'] == 'STAY' else 2
            flag = oflag.get(tid, 0xFFFF); typ = 0; sight = 0
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; a.label(lab); a.db(item_id(o['extra'][0]), 1)
            elif n == 'MtMoonB2F' and o['sprite'] == 'SPRITE_SUPER_NERD':
                nerd_beat = newflag(); got_f = newflag()
                tg = P14.asm_block_texts(g, tid)
                cls_, pid = party_of[(n, o['text'])]
                a.label(lab); a.faceplayer()
                a.label('nerd'); a.checkevent(nerd_beat); a.iftrue(lab + 'b')
                a.opentext(); a.writetext(lab + 'm'); a.waitbutton(); a.closetext()
                a.winlosstext(lab + 'w', 0); a.loadtrainer(cls_, pid); a.startbattle(); a.reloadmapafterbattle()
                a.setevent(nerd_beat); a.end()
                a.label(lab + 'b'); a.opentext(); a.checkevent(got_f); a.iftrue(lab + 'c')
                a.writetext(lab + 'e'); a.waitbutton(); a.closetext(); a.end()
                a.label(lab + 'c'); a.writetext(lab + 'l'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 'e'] = tg[0]; texts[lab + 'm'] = tg[1]; texts[lab + 'w'] = tg[2]; texts[lab + 'l'] = tg[3]
                nerd_tid = tid
            elif o['extra'] and o['extra'][0] in CLS:
                typ = 2; fl = newflag()
                sight, seen, aft, win = P12.trainer_texts(g, tid)
                cls_, pid = party_of[(n, o['text'])]
                a.label(lab); a.dw(fl); a.db(cls_, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            elif o['sprite'] == 'SPRITE_FOSSIL':
                a.label(lab); a.end()                          # filled below
            elif o['sprite'] in ('SPRITE_JAMES', 'SPRITE_JESSIE'):
                a.label(lab); a.end()
            else:
                b_, p_ = pkmap.text_ptr(g, tid); k_, body = pkmap.text_body(b_, p_)
                a.label(lab); a.jumptextfaceplayer(lab + 't')
                texts[lab + 't'] = body if k_ == 'text' else P14.asm_block_texts(g, tid)[0]
            obj_bytes.append([sprite, o['y'] + 4, o['x'] + 4, mv, 0, 0xFF, 0xFF, typ, sight, lab, flag])

        if n == 'MtMoonB2F':
            fossils = oid['SPRITE_FOSSIL']                     # dome, helix
            fd, fh = fossils
            for tid, item, other in ((fd, DOME_FOSSIL, fh), (fh, HELIX_FOSSIL, fd)):
                lab = 'f%d' % tid
                tg = P14.asm_block_texts(g, tid)
                # patch the object's script pointer label
                obj_bytes[tid - 1][9] = lab
                a.label(lab); a.checkevent(nerd_beat); a.iffalse('nerd')
                a.opentext(); a.writetext(lab + 'q'); a.yesorno(); a.iffalse(lab + 'n')
                a.verbosegiveitem(item, 1); a.iffalse(lab + 'n'); a.closetext()
                a.disappear(tid + 1); a.setevent(got_f)
                a.opentext(); a.writetext('mine'); a.waitbutton(); a.closetext()
                a.disappear(other + 1); a.end()
                a.label(lab + 'n'); a.closetext(); a.end()
                texts[lab + 'q'] = tg[0]
            _, t11 = pkmap.text_body(*pkmap.text_ptr(g, 11)); texts['mine'] = t11
            # the nerd blocks the way to the fossils (Red: he talks to you at 13,8)
            a.label('ncoord'); a.checkevent(nerd_beat); a.iftrue('nce'); a.sjump('nerd')
            a.label('nce'); a.end()
            coords.append((8, 13, 'ncoord'))
            # Jessie & James (Pikachu version)
            jjf = newflag()
            a.label('cbo'); a.checkevent(jjf); a.iftrue('cbo2'); a.setevent(jjv)
            a.label('cbo2'); a.endcallback()
            callbacks.append((2, 'cbo'))
            jam, jes = oid['SPRITE_JAMES'][0] + 1, oid['SPRITE_JESSIE'][0] + 1
            _, t12 = pkmap.text_body(*pkmap.text_ptr(g, 12)); _, t13 = pkmap.text_body(*pkmap.text_ptr(g, 13))
            _, t14 = pkmap.text_body(*pkmap.text_ptr(g, 14))
            h = pkmap.header(g); hb = h['bank']; s0 = pkmap.fo(hb, h['script'])
            m = re.search(rb'\x21(..)\x11\1\xcd', pkmap.F[s0 - 0x200:s0 + 0x800], re.S)
            tl = None
            for m in re.finditer(rb'\x21(..)\x11(..)\xcd', pkmap.F[s0 - 0x200:s0 + 0x800], re.S):
                p1 = m.group(1)[0] | m.group(1)[1] << 8; k1, tt = pkmap.text_body(hb, p1)
                if k1 == 'text' and 'まけるなんて' in decode(tt): tl = tt
            assert tl is not None
            a.label('jj'); a.checkevent(jjf); a.iftrue('jje')
            a.playmusic(0x39); a.opentext(); a.writetext('j12'); a.waitbutton(); a.closetext()
            a.appear(jam); a.appear(jes)
            a.applymovement(jam, 'jmv'); a.applymovement(jes, 'jmv')
            a.opentext(); a.writetext('j13'); a.waitbutton(); a.closetext()
            a.winlosstext('jl', 0); a.loadtrainer(JJ, 1); a.startbattle(); a.reloadmapafterbattle()
            a.opentext(); a.writetext('j14'); a.waitbutton(); a.closetext()
            a.disappear(jam); a.disappear(jes); a.setevent(jjf)
            a.label('jje'); a.end()
            a.label('jmv'); a.db(*([0x0E] * 5), 0x47)            # step LEFT x5
            texts['j12'] = t12; texts['j13'] = t13; texts['j14'] = bytes(t14).replace(b'\x6e', encode('ィ')); texts['jl'] = tl
            coords.append((5, 3, 'jj'))
        if n == 'MtMoon1F':
            src = open(PY + '/data/maps/objects/MtMoon1F.asm').read()
            for x, y in re.findall(r'bg_event\s+(\d+),\s*(\d+)', src):
                ntext = len(objs) + 1
                b_, p_ = pkmap.text_ptr(g, ntext); k_, body = pkmap.text_body(b_, p_)
                a.label('sign'); a.jumptext('signt'); texts['signt'] = body
                bgs.append((int(y), int(x), 0, 'sign'))

        for k_, v in texts.items():
            assert isinstance(v, (bytes, bytearray)) and len(v) < 700, (n, k_)
            a.label(k_); a.raw(P12.text(v))
        a.label('mapscripts'); a.db(0, len(callbacks))
        for t_, l_ in callbacks:
            a.db(t_); a.dw(l_)
        a.label('events'); a.db(0, 0)
        a.db(len(warps))
        for (x, y, dest, wid) in warps:
            if dest == 'LAST_MAP':
                a.db(y, x, 1, *(r3 if n == 'MtMoon1F' else r4))
            else:
                dn = 'MtMoon' + dest.split('_')[-1]
                a.db(y, x, wid, *mapids[dn])
        a.db(len(coords))
        for (y, x, l_) in coords:
            a.db(0xFF, y, x, 0); a.dw(l_); a.db(0, 0)
        a.db(len(bgs))
        for (y, x, f_, l_) in bgs:
            a.db(y, x, f_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes:
            a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(sb, blob) == base
        db_ = next(b for b in (0x7C, 0x79, 0x7A, 0x77, 0x76, 0x75) if sp.cur[b][1] - sp.cur[b][0] > len(mp.blk) + 16)
        blkp = sp.put(db_, mp.blk)
        attr_ = bytes([border_of(n), mp.h, mp.w, db_, blkp & 0xFF, blkp >> 8, sb, a.labels['mapscripts'] & 0xFF,
                       a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0])
        aa = sp.put(db_, attr_)
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        rom[hh:hh + 9] = bytes([db_, TS_ID, 4, aa & 0xFF, aa >> 8, landmark, music, 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, *mapids[n], sb, base, len(blob)))

    # ================= Route 3 / Route 4 entrances (before the Hall of Fame -> ported Mt. Moon)
    for rname, target, twarp in (('Route3', 'MtMoon1F', 1), ('Route4', 'MtMoonB1F', 8)):
        a_ = attrs(rom, hdr_index(rname)); ev = parse_events(rom, a_['scbank'], a_['events'])
        mm = mapid('MountMoon')
        fix = {}
        for i, (o_, w) in enumerate(ev['warps']):
            if (w[3], w[4]) == mm:
                fix[i] = bytes(w)
                rom[o_ + 2] = twarp; rom[o_ + 3], rom[o_ + 4] = mapids[target]
        assert fix, rname
        install_hof_switch(rom, sp, rname, fix, log)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used %d of %d' % (EVI[0], len(EXT_FLAGS)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
