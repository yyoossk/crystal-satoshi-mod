#!/usr/bin/env python3
"""Phase 14: Silph Co. 1F-11F + elevator, ported from the Pikachu full-color hack (maps, tilesets, sprites, texts)
with Red's trainers (Rockets, scientists, juggler, Shigeru on 7F, Giovanni on 11F) and the Pikachu version's
Jessie & James on 11F.  Card-key doors, the Lapras gift (7F), the nurse (9F), the Master Ball (11F president).
New overworld sprites (Silph workers, president, clipboard) from the Pikachu full-color hack.
usage: build_phase14.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode, decode
import pkmap
import build_phase11 as P11
import build_phase12 as P12
import build_phase13 as P13
import build_phase10 as P10

ITEM = load_consts(PC + '/constants/item_constants.asm')
MON = load_consts(PC + '/constants/pokemon_constants.asm')
FREE_EV = json.load(open(SC + '/out/free_events.json'))
EVI = [58]                       # phase 12 used up to 58
def newflag():
    f = FREE_EV[EVI[0]]; EVI[0] += 1; return f

GRUNTM, SCIENTIST, JUGGLER, BLUE, GIOVANNI, JJ = 31, 20, 49, 64, 71, 72
SILPH_CARD_KEY = 0x89
EV_OAK_GOT = {'fire': 0x343, 'water': 0x344, 'grass': 0x345}
PKFC = SC + '/pkfc/pkfc.gbc'

SILPH = [('SilphCo1F', 0xB5), ('SilphCo2F', 0xCF), ('SilphCo3F', 0xD0), ('SilphCo4F', 0xD1), ('SilphCo5F', 0xD2),
         ('SilphCo6F', 0xD3), ('SilphCo7F', 0xD4), ('SilphCo8F', 0xD5), ('SilphCo9F', 0xE9), ('SilphCo10F', 0xEA),
         ('SilphCo11F', 0xEB), ('SilphCoElevator', 0xEC)]
TSNAME = {'SilphCo11F': 'Interior', 'SilphCoElevator': 'Lobby'}

# new overworld sprites (second sprite table, ids 0x67+)
OW_SPRITES = 0x14727; OW_READERS = [(0x14231, 0), (0x1429E, 4), (0x142BB, 5)]
NEW_SPRITES = [  # name, PKFC offset, tiles, type (1 walking, 2 standing, 3 still), palette
    ('SPRITE_SILPH_WORKER_M', 0x13450, 12, 2, 3),
    ('SPRITE_SILPH_WORKER_F', 0x16BD2, 24, 1, 0),
    ('SPRITE_SILPH_PRESIDENT', 0x13390, 12, 2, 1),
    ('SPRITE_CLIPBOARD', 0x13B90, 4, 3, 3),
    ('SPRITE_FOSSIL', 0x13A90, 4, 3, 3),
    ('SPRITE_BRUNETTE_GIRL', 0x16ED2, 24, 1, 0),
    ('SPRITE_COOK', 0x16212, 24, 1, 1),
    ('SPRITE_JIGGLYPUFF', 0xFEBD1, 12, 2, 4),
    ('SPRITE_LITTLE_BOY', 0x17352, 12, 2, 1),
    ('SPRITE_LITTLE_GIRL', 0x15012, 24, 1, 0),
    ('SPRITE_WAITER', 0x16A52, 24, 1, 1)]
SPR = {'SPRITE_ROCKET': 0x35, 'SPRITE_GIOVANNI': 0x3F, 'SPRITE_JAMES': 0x35, 'SPRITE_JESSIE': 0x36,
       'SPRITE_POKE_BALL': 0x54, 'SPRITE_BEAUTY': 0x2A, 'SPRITE_SCIENTIST': 0x3C, 'SPRITE_ROCKER': 0x2C,
       'SPRITE_BLUE': 0x07, 'SPRITE_LINK_RECEPTIONIST': 0x38, 'SPRITE_NURSE': 0x37}
for i, s in enumerate(NEW_SPRITES):
    SPR[s[0]] = 0x67 + i
FACE = P12.FACE
SCI_NAMES = ['タダシ', 'マサオ', 'ヒロシ', 'ケンジ', 'ユウジ', 'タケシ', 'カズオ', 'ヨシオ', 'ノボル', 'ミツル']
TM_NUM = {'TM_EARTHQUAKE': 26, 'TM_SWORDS_DANCE': 3, 'TM_TAKE_DOWN': 9, 'TM_SELFDESTRUCT': 36}
SFX_ENTER_DOOR, SFX_ELEVATOR = 0x1F, 0x6E


def item_id(n):
    if n == 'CARD_KEY': return SILPH_CARD_KEY
    if n in TM_NUM: return P12.tm_item(TM_NUM[n])
    return P12.item_id(n)


def asm_block_texts(g, tid):
    """texts referenced inside one text_asm block (stops at its `jp TextScriptEnd`)"""
    b, p = pkmap.text_ptr(g, tid); k, o = pkmap.text_body(b, p)
    if k == 'text': return [o]
    out = []; i = o
    while i < o + 300:
        op = pkmap.F[i]
        if op == 0xC3 and (pkmap.F[i + 1] | pkmap.F[i + 2] << 8) < 0x4000:
            break
        if op == 0x21:
            pp = pkmap.F[i + 1] | pkmap.F[i + 2] << 8
            if 0x4000 <= pp < 0x8000:
                kk, bb = pkmap.text_body(b, pp)
                if kk == 'text' and bb not in out: out.append(bb)
        i += 1
    return out


def doors_of(mapname):
    """card-key doors: [(block x, block y, closed block id)] from the Yellow map script"""
    path = PY + '/scripts/%s.asm' % mapname
    if not os.path.exists(path): return []
    src = open(path, encoding='utf-8').read()
    return [(int(x), int(y), int(blk, 16)) for blk, y, x in
            re.findall(r'ld a, \$(\w+)\n\s+ld \[wNewTileBlockID\], a\n\s+lb bc, (\d+), (\d+)', src)]


def objects_with_comments(mapname):
    objs, warps = P11.objects_of(mapname)
    src = open(PY + '/data/maps/objects/%s.asm' % mapname, encoding='utf-8').read()
    skip = set()
    for i, l in enumerate([l for l in src.split('\n') if re.match(r'\s*warp_event\s', l)]):
        if 'inaccessible' in l or 'UNUSED_MAP' in l: skip.add(i)
    return objs, warps, skip


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x05, 0x12, 0x13, 0x79, 0x7A, 0x7C, 0x7D, 0x77, 0x76):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    pk = open(PKFC, 'rb').read()

    # ================= sprites: second table for ids 0x67+ (bank 5)
    tab = bytearray()
    for name, off, tiles, typ, pal in NEW_SPRITES:
        gb = next(b for b in (0x7D, 0x77, 0x76, 0x79) if sp.cur[b][1] - sp.cur[b][0] > tiles * 16 + 64)
        a_g = sp.put(gb, pk[off:off + tiles * 16])
        tab += bytes([a_g & 0xFF, a_g >> 8, (tiles * 16) & 0xFF if tiles < 16 else 0xC0, gb, typ, pal])
    t2 = sp.put(0x05, bytes(tab))
    virt = t2 - 0x66 * 6                     # base such that base + (id-1)*6 = t2 for id 0x67
    a = Asm(sp.here(0x05))
    for k, (off, d) in enumerate(OW_READERS):
        assert rom[off] == 0x21 and r16(off + 1) == 0x4727 + d, hex(off)
        a.label('r%d' % k)
        a.db(0xFE, 0x67, 0x30, 0x04, 0x21); a.dw(0x4727 + d); a.db(0xC9, 0x21); a.dw(virt + d); a.db(0xC9)
    base5 = a.base; blob = a.done(); assert sp.put(0x05, blob) == base5
    for k, (off, d) in enumerate(OW_READERS):
        rom[off] = 0xCD; w16(off + 1, a.labels['r%d' % k])
    log.append('sprites 67-%02X (table 05:%04X)' % (0x66 + len(NEW_SPRITES), t2))

    # ================= tilesets: INTERIOR (new), FACILITY/LOBBY collisions updated in place
    tab_ptr = r16(R_TILESETS[0]); tab_o = fo(0x13, tab_ptr); ntab = 36
    old_tab = bytes(rom[tab_o:tab_o + 15 * ntab])
    tss = {'Facility': Tileset('Facility', 22, 'facility.bst', SC + '/out/pk_facility.pkl'),
           'Lobby': Tileset('Lobby', 18, 'lobby.bst', SC + '/out/pk_lobby.pkl'),
           'Interior': Tileset('Interior', 16, 'interior.bst', SC + '/out/pk_interior.pkl')}
    for b_ in range(tss['Lobby'].nblocks):
        for q in range(4):
            if tss['Lobby'].quad_tile(b_, q) in (0x15, 0x36):
                tss['Lobby'].coll[4 * b_ + q] = 0x90
    ts_id = {'Facility': 34, 'Lobby': 35, 'Interior': 36}
    for k in ('Facility', 'Lobby'):          # current collision data (with the hideout's warp tiles)
        e = old_tab[15 * ts_id[k]:15 * ts_id[k] + 15]
        co = fo(e[6], e[7] | e[8] << 8)
        tss[k].coll = bytearray(rom[co:co + 4 * tss[k].nblocks]); tss[k].coll_off = co
    maps = {}
    for n, g in SILPH:
        h = pkmap.header(g)
        maps[n] = MapPort(n, tss[TSNAME.get(n, 'Facility')], h['w'], h['h'], n + '.blk')
    for n, mp in maps.items():
        objs, warps, skip = objects_with_comments(n)
        ts = mp.ts
        for wi, (x, y, dest, wid) in enumerate(warps):
            if wi in skip: continue
            b_, q = mp.block_at(x, y); tile = ts.quad_tile(b_, q)
            if y == mp.h * 2 - 1 or y == 0 or x == 0 or x == mp.w * 2 - 1:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            elif tile in ts.warp_tiles:
                v = COLL_STAIRCASE
            else:
                raise AssertionError((n, x, y, hex(tile)))
            old = ts.coll[4 * b_ + q]
            if old not in (COLL_FLOOR, COLL_WALL, v):
                raise AssertionError((n, x, y, hex(old), hex(v)))
            ts.coll[4 * b_ + q] = v
    for k in ('Facility', 'Lobby'):
        rom[tss[k].coll_off:tss[k].coll_off + len(tss[k].coll)] = tss[k].coll
    ti = tss['Interior']
    gfx = lz(ti.gfx_raw)
    a_gfx = sp.put(0x7C, gfx); a_meta = sp.put(0x7C, ti.blocks); a_coll = sp.put(0x7C, bytes(ti.coll))
    a_pal = sp.put(0x13, ti.palmap)
    anim_none = old_tab[15 * 5 + 9:15 * 5 + 11]
    new_tab = old_tab + bytes([0x7C, a_gfx & 0xFF, a_gfx >> 8, 0x7C, a_meta & 0xFF, a_meta >> 8, 0x7C, a_coll & 0xFF, a_coll >> 8]) + \
        anim_none + b'\x00\x00' + bytes([a_pal & 0xFF, a_pal >> 8])
    rom[tab_o:tab_o + len(old_tab)] = bytes(len(old_tab))
    w16(R_TILESETS[0], sp.put(0x13, new_tab))
    prev_hook = r16(LSMP + 1)
    hp = rom[HOUSEPAL_CALL:HOUSEPAL_CALL + 14]; wbgpals = hp[3:5]; farcopy = hp[12:14]
    ph = fo(0x12, prev_hook); ld_ts = bytes(rom[ph:ph + 3]); assert ld_ts[0] == 0xFA
    a_pi = sp.put(0x12, ti.pals)
    a = Asm(sp.here(0x12))
    a.raw(ld_ts); a.db(0xFE, ts_id['Interior'], 0x28, 0x03); a.db(0xC3); a.dw(prev_hook)
    a.db(0x21); a.dw(a_pi); a.db(0x3E, 0x05, 0x11); a.raw(wbgpals); a.db(0x01, 0x40, 0x00, 0xCD); a.raw(farcopy); a.db(0x37, 0xC9)
    hk = sp.put(0x12, a.done()); w16(LSMP + 1, hk)
    log.append('tileset Interior id 36 (gfx %d bytes, %d blocks)' % (len(gfx), ti.nblocks))

    # ================= map headers 26:26.. (bank 0x25)
    u = US.get(); G = u.groups()
    new_maps = [n for n, g in SILPH if n != 'SilphCo1F']
    first_new = 26
    lo = GROUP26_END + 9 * (first_new - G26_COUNT - 1); hi = lo + 9 * len(new_maps)
    moved = 0
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else first_new - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                rom[hdr] = 0x7C; w16(hdr + 3, sp.put(0x7C, bytes(rom[ao:ao + size]))); moved += 1
    rom[lo:hi] = bytes(hi - lo)
    mapids = {n: (G26, first_new + i) for i, n in enumerate(new_maps)}
    mapids['SilphCo1F'] = mapid('SilphCo1F')
    saf = mapid('SaffronCity')
    sa = attrs(rom, hdr_index('SaffronCity')); sev = parse_events(rom, sa['scbank'], sa['events'])
    saf_door = [i + 1 for i, (o_, w) in enumerate(sev['warps']) if (w[3], w[4]) == mapids['SilphCo1F']][0]
    log.append('moved %d attribute blocks; Saffron door = warp %d' % (moved, saf_door))

    # ================= trainer parties (bank 0x7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, MON[P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    def add(cls, name, mons):
        groups[cls - 1].append([encode(name + '@'), pb(mons)]); return len(groups[cls - 1])
    rocket = P11.red_parties('RocketData'); sci = P11.red_parties('ScientistData')
    jug = P11.red_parties('JugglerData'); riv2 = P11.red_parties('Rival2Data')
    party_of = {}
    ns = 0
    for n, g in SILPH:
        objs, _ = P11.objects_of(n)
        for o in objs:
            if o['extra'] and o['extra'][0].startswith('OPP_'):
                cls_, k = o['extra'][0], int(o['extra'][1])
                if cls_ == 'OPP_ROCKET': party_of[(n, o['text'])] = (GRUNTM, add(GRUNTM, 'したっぱ', rocket[k - 1]))
                elif cls_ == 'OPP_SCIENTIST': party_of[(n, o['text'])] = (SCIENTIST, add(SCIENTIST, SCI_NAMES[ns % 10], sci[k - 1])); ns += 1
                elif cls_ == 'OPP_JUGGLER': party_of[(n, o['text'])] = (JUGGLER, add(JUGGLER, 'カズマ', jug[k - 1]))
    riv_ids = {key: add(BLUE, 'シゲル', riv2[6 + i]) for i, key in enumerate(['fire', 'water', 'grass'])}
    free = P13.write_groups7e(rom, groups)
    log.append('trainer parties added (bank 7E free %d)' % free)

    # ================= maps
    gio_beat = newflag()                    # shared: Giovanni left Silph Co.
    landmark = rom[hdr_index('SaffronCity') + 5]
    bank_order = [0x7A, 0x79]
    for n, mp in maps.items():
        g = dict(SILPH)[n]
        objs, warps, skip = objects_with_comments(n)
        sb = next(b for b in bank_order if sp.cur[b][1] - sp.cur[b][0] > 2600)
        a = Asm(sp.here(sb))
        callbacks = []; coords = []; bgs = []; texts = {}; obj_bytes = []
        oid = {}; oflag = {}
        for idx, o in enumerate(objs):
            tid = idx + 1
            if o['sprite'] == 'SPRITE_POKE_BALL': oflag[tid] = newflag()
            if o['sprite'] in ('SPRITE_GIOVANNI', 'SPRITE_JAMES', 'SPRITE_JESSIE', 'SPRITE_BLUE'):
                oid[o['sprite']] = tid
        if 'SPRITE_JAMES' in oid:
            jjv = newflag(); oflag[oid['SPRITE_JAMES']] = jjv; oflag[oid['SPRITE_JESSIE']] = jjv
        if 'SPRITE_GIOVANNI' in oid: oflag[oid['SPRITE_GIOVANNI']] = gio_beat
        if 'SPRITE_BLUE' in oid: oflag[oid['SPRITE_BLUE']] = newflag()
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid
            sprite = SPR[o['sprite']]; mv = FACE.get(o['face'], 6) if o['move'] == 'STAY' else 2
            flag = oflag.get(tid, 0xFFFF); typ = 0; sight = 0
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; a.label(lab); a.db(item_id(o['extra'][0]), 1)
            elif o['extra'] and o['extra'][0].startswith('OPP_') and o['sprite'] != 'SPRITE_GIOVANNI':
                typ = 2; fl = newflag()
                sight, seen, aft, win = P12.trainer_texts(g, tid)
                cls_, pid = party_of[(n, o['text'])]
                a.label(lab); a.dw(fl); a.db(cls_, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            elif o['sprite'] == 'SPRITE_GIOVANNI':
                # 11F: walks up to the player (coord events below), battle (Red party 2), then leaves
                a.label(lab); a.end()
            elif o['sprite'] in ('SPRITE_JAMES', 'SPRITE_JESSIE', 'SPRITE_BLUE'):
                a.label(lab); a.jumptextfaceplayer(lab + 't')
                b_, p_ = pkmap.text_ptr(g, tid); k_, body = pkmap.text_body(b_, p_)
                texts[lab + 't'] = body if k_ == 'text' else asm_block_texts(g, tid)[0]
            else:
                tg = asm_block_texts(g, tid)
                special = (n, tid)
                if special == ('SilphCo7F', 1):                 # Lapras gift
                    got = newflag()
                    a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got); a.iftrue(lab + 'g')
                    a.writetext(lab + 'a'); a.waitbutton(); a.givepoke(MON['LAPRAS'], 15); a.iffalse(lab + 'z'); a.setevent(got)
                    a.label(lab + 'g'); a.checkevent(gio_beat); a.iftrue(lab + 'h')
                    a.writetext(lab + 'b'); a.waitbutton(); a.closetext(); a.end()
                    a.label(lab + 'h'); a.writetext(lab + 'c'); a.waitbutton()
                    a.label(lab + 'z'); a.closetext(); a.end()
                    texts[lab + 'a'] = tg[1]; texts[lab + 'b'] = tg[2]; texts[lab + 'c'] = tg[3]
                elif special == ('SilphCo2F', 1):               # TM gift
                    got = newflag()
                    a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got); a.iftrue(lab + 'g')
                    a.writetext(lab + 'a'); a.waitbutton(); a.verbosegiveitem(item_id('TM_SELFDESTRUCT'), 1)
                    a.iffalse(lab + 'z'); a.setevent(got)
                    a.label(lab + 'g'); a.writetext(lab + 'b'); a.waitbutton()
                    a.label(lab + 'z'); a.closetext(); a.end()
                    texts[lab + 'a'] = tg[0]; texts[lab + 'b'] = encode('{00}がんばってね！')
                elif o['sprite'] == 'SPRITE_NURSE':              # rest here (heal)
                    a.label(lab); a.faceplayer(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext()
                    a.special(27)
                    a.opentext(); a.writetext(lab + 'b'); a.waitbutton(); a.closetext(); a.end()
                    texts[lab + 'a'] = tg[0]; texts[lab + 'b'] = tg[1]
                elif o['sprite'] == 'SPRITE_SILPH_PRESIDENT':   # Master Ball
                    got = newflag()
                    a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got); a.iftrue(lab + 'g')
                    a.writetext(lab + 'a'); a.waitbutton(); a.verbosegiveitem(ITEM['MASTER_BALL'], 1); a.iffalse(lab + 'z')
                    a.setevent(got)
                    a.label(lab + 'g'); a.writetext(lab + 'b'); a.waitbutton()
                    a.label(lab + 'z'); a.closetext(); a.end()
                    texts[lab + 'a'] = tg[0]; texts[lab + 'b'] = tg[3]
                else:
                    a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = tg[0]
            obj_bytes.append([sprite, o['y'] + 4, o['x'] + 4, mv, 0, 0xFF, 0xFF, typ, sight, lab, flag])

        # ---- card-key doors
        doors = doors_of(n)
        if doors:
            dfl = [newflag() for _ in doors]
            a.label('cbt')
            for i, (bx, by, blk) in enumerate(doors):
                a.checkevent(dfl[i]); a.iftrue('cb%d' % i); a.changeblock(2 * bx, 2 * by, blk); a.label('cb%d' % i)
            a.endcallback()
            callbacks.append((1, 'cbt'))
            open_blk = 0x03 if n == 'SilphCo11F' else 0x0E
            for i, (bx, by, blk) in enumerate(doors):
                L = 'dr%d' % i
                a.label(L); a.checkevent(dfl[i]); a.iftrue(L + 'e')
                a.opentext(); a.checkitem(SILPH_CARD_KEY); a.iffalse(L + 'n')
                a.writetext('ck_ok'); a.playsound(SFX_ENTER_DOOR); a.waitsfx(); a.waitbutton(); a.closetext()
                a.changeblock(2 * bx, 2 * by, open_blk); a.refreshmap(); a.setevent(dfl[i]); a.end()
                a.label(L + 'n'); a.writetext('ck_ng'); a.waitbutton(); a.closetext()
                a.label(L + 'e'); a.end()
                for dy in (0, 1):
                    for dx in (0, 1):
                        bgs.append((2 * by + dy, 2 * bx + dx, 0, L))
            texts['ck_ok'] = encode('{00}<……>ピンポーン！<LINE>カードキーで　ロック　をはずした！')
            texts['ck_ng'] = encode('{00}<……>だめだ！<LINE>カードキーが　ないと　あかない！')

        # ---- 7F: Shigeru
        if n == 'SilphCo7F':
            rt = oid['SPRITE_BLUE']; rflag = oflag[rt]
            _, t_wait = pkmap.text_body(*pkmap.text_ptr(g, 13))
            _, t_win = pkmap.text_body(*pkmap.text_ptr(g, 14))
            _, t_bye = pkmap.text_body(*pkmap.text_ptr(g, 15))
            def riv(bb): return bytes(bb).replace(b'\x53', encode('シゲル'))
            for y, steps in ((2, 4), (3, 3)):
                L = 'rv%d' % y
                a.label(L); a.checkevent(rflag); a.iftrue('rve')
                a.applymovement(rt + 1, 'rm%d' % steps); a.sjump('rvb')
                coords.append((y, 3, L))
            a.label('rm4'); a.db(0x0D, 0x0D, 0x0D, 0x0D, 0x47)
            a.label('rm3'); a.db(0x0D, 0x0D, 0x0D, 0x47)
            a.label('rvb'); a.opentext(); a.writetext('rvw'); a.waitbutton(); a.closetext()
            a.winlosstext('rvl', 0)
            a.checkevent(EV_OAK_GOT['fire']); a.iftrue('rvf')
            a.checkevent(EV_OAK_GOT['water']); a.iftrue('rvv')
            a.loadtrainer(BLUE, riv_ids['grass']); a.sjump('rvg')
            a.label('rvf'); a.loadtrainer(BLUE, riv_ids['fire']); a.sjump('rvg')
            a.label('rvv'); a.loadtrainer(BLUE, riv_ids['water'])
            a.label('rvg'); a.startbattle(); a.reloadmapafterbattle()
            a.opentext(); a.writetext('rvy'); a.waitbutton(); a.closetext()
            a.disappear(rt + 1); a.setevent(rflag)
            a.label('rve'); a.end()
            texts['rvw'] = riv(t_wait); texts['rvl'] = riv(t_win); texts['rvy'] = riv(t_bye)

        # ---- 11F: Jessie & James, Giovanni
        if n == 'SilphCo11F':
            jjf = newflag()
            jam, jes = oid['SPRITE_JAMES'] + 1, oid['SPRITE_JESSIE'] + 1
            gt = oid['SPRITE_GIOVANNI'] + 1
            _, t8 = pkmap.text_body(*pkmap.text_ptr(g, 8)); _, t9 = pkmap.text_body(*pkmap.text_ptr(g, 9))
            _, t10 = pkmap.text_body(*pkmap.text_ptr(g, 10)); _, tjl = pkmap.text_body(0x18, 0x7839)
            _, tg3 = pkmap.text_body(*pkmap.text_ptr(g, 3)); _, tg7 = pkmap.text_body(*pkmap.text_ptr(g, 7))
            _, tgl = pkmap.text_body(0x18, 0x7A67)
            a.label('cbo'); a.checkevent(jjf); a.iftrue('cbo2'); a.setevent(jjv)
            a.label('cbo2'); a.endcallback()
            callbacks.append((2, 'cbo'))
            # (the callback hides J&J until they jump out)
            for x in (1, 2, 3):
                L = 'jj%d' % x
                a.label(L); a.sjump('jjs'); coords.append((3, x, L))
            a.label('jjs'); a.checkevent(jjf); a.iftrue('jje')
            a.playmusic(0x39); a.opentext(); a.writetext('j8'); a.waitbutton(); a.closetext()
            a.appear(jam); a.appear(jes)
            a.applymovement(jam, 'jmv'); a.applymovement(jes, 'jmv')
            a.opentext(); a.writetext('j9'); a.waitbutton(); a.closetext()
            a.winlosstext('jl', 0); a.loadtrainer(JJ, 4); a.startbattle(); a.reloadmapafterbattle()
            a.opentext(); a.writetext('j10'); a.waitbutton(); a.closetext()
            a.disappear(jam); a.disappear(jes); a.setevent(jjf)
            a.label('jje'); a.end()
            a.label('jmv'); a.db(0x0D, 0x0D, 0x0D, 0x0D, 0x47)
            texts['j8'] = t8; texts['j9'] = t9; texts['j10'] = bytes(t10).replace(b'\x6e', encode('ィ')); texts['jl'] = tjl
            for (x, y) in ((6, 13), (7, 12)):
                L = 'gv%d' % x
                a.label(L); a.sjump('gvs'); coords.append((y, x, L))
            a.label('gvs'); a.checkevent(gio_beat); a.iftrue('gve')
            a.opentext(); a.writetext('g3'); a.waitbutton(); a.closetext()
            a.applymovement(gt, 'gmv')
            a.winlosstext('gl', 0); a.loadtrainer(GIOVANNI, 2); a.startbattle(); a.reloadmapafterbattle()
            a.opentext(); a.writetext('g7'); a.waitbutton(); a.closetext()
            a.disappear(gt); a.setevent(gio_beat)
            a.label('gve'); a.end()
            a.label('gmv'); a.db(0x0C, 0x0C, 0x0C, 0x47)
            texts['g3'] = tg3; texts['g7'] = tg7; texts['gl'] = tgl

        # ---- elevator
        if n == 'SilphCoElevator':
            a.label('elv'); a.opentext(); a.elevator('eld'); a.closetext(); a.iffalse('ele')
            a.pause(5); a.playsound(SFX_ELEVATOR); a.earthquake(60); a.waitsfx()
            a.label('ele'); a.end()
            a.label('eld'); a.db(11)
            for fl_, (mn, wid) in enumerate([('SilphCo1F', 4)] + [('SilphCo%dF' % k, 3) for k in range(2, 11)] + [('SilphCo11F', 2)]):
                a.db(4 + fl_, wid, *mapids[mn])
            a.db(0xFF)
            bgs.append((0, 3, 1, 'elv'))

        for k_, v in texts.items():
            assert isinstance(v, (bytes, bytearray)) and len(v) < 700, (n, k_)
            a.label(k_); a.raw(P12.text(v))
        a.label('mapscripts'); a.db(0, len(callbacks))
        for t_, l_ in callbacks:
            a.db(t_); a.dw(l_)
        a.label('events'); a.db(0, 0)
        wl = []
        for wi, (x, y, dest, wid) in enumerate(warps):
            if dest == 'LAST_MAP': wl.append((y, x, saf_door) + saf)
            elif n == 'SilphCoElevator': wl.append((y, x, 0xFF) + mapids['SilphCo1F'])
            elif dest.startswith('UNUSED') or wi in skip: wl.append((y, x, 1) + mapids[n])
            else:
                dn = 'SilphCoElevator' if dest == 'SILPH_CO_ELEVATOR' else 'SilphCo' + dest.split('_')[-1]
                wl.append((y, x, wid) + mapids[dn])
        a.db(len(wl))
        for w in wl: a.db(*w)
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
        blkp = sp.put(0x7C, mp.blk)
        attr_ = bytes([border_of(n), mp.h, mp.w, 0x7C, blkp & 0xFF, blkp >> 8, sb, a.labels['mapscripts'] & 0xFF,
                       a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0])
        aa = sp.put(0x7C, attr_)
        tsid = ts_id[TSNAME.get(n, 'Facility')]
        if n == 'SilphCo1F':
            h = hdr_index('SilphCo1F'); rom[h] = 0x7C; rom[h + 1] = tsid; w16(h + 3, aa)
        else:
            h = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
            env = 3 if n == 'SilphCoElevator' else 7
            music = rom[hdr_index('SilphCo1F') + 6]
            rom[h:h + 9] = bytes([0x7C, tsid, env, aa & 0xFF, aa >> 8, landmark, music, 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, mapids[n][0], mapids[n][1], sb, base, len(blob)))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('flags used up to index %d of %d' % (EVI[0], len(FREE_EV)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
